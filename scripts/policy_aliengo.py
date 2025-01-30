import os
import sys
print(os.getcwd())
sys.path.append(os.getcwd())

import argparse
import math
import time
import torch
import numpy as np
from collections import deque

from src import utils
from src import config
from src.robots.simulation import simulation
from src import command

from standup_aliengo import standup

import src.config as config
import src.utils as utils
import src.positions as positions

from src.robots import RealAlienGo, RealGo1
from src.robots.simulation.simulation import Simulation

sys.path.append("./submodules/free-dog-sdk/")
from ucl.lowCmd import lowCmd
from ucl.lowState import lowState
from ucl.unitreeConnection import unitreeConnection, LOW_WIRED_DEFAULTS

sys.path.append('./submodules/unitree_legged_sdk/lib/python/amd64')
import robot_interface_aliengo as sdk

# to do: move to _config_ or to unitree_legged_sdk 
TARGET_PORT = 8007
LOCAL_PORT = 8082
TARGET_IP = "192.168.123.10"   # target IP address
LOW_CMD_LENGTH = 610
LOW_STATE_LENGTH = 771


ALIENGO_LOW_WIRED_DEFAULTS = (LOCAL_PORT, TARGET_IP, TARGET_PORT, LOW_CMD_LENGTH, LOW_STATE_LENGTH, -1) 

# to do: move this values to unitree_legged_sdk 
HIGHLEVEL = 0x00
LOWLEVEL  = 0xff


def setup_motor(cmd, num_motor, q, dq, Kp, Kd, tau):
    cmd.motorCmd[num_motor].q = q
    cmd.motorCmd[num_motor].dq = dq
    cmd.motorCmd[num_motor].Kp = Kp
    cmd.motorCmd[num_motor].Kd = Kd
    cmd.motorCmd[num_motor].tau = tau


def to_observation(state, action_history):
    obs = []
    imu_quaternion = state.imu.quaternion
    obs.extend(utils.quatToEuler(imu_quaternion)[:2])

    for i in range(12):
        obs.append(state.motorState[i].q)

    for i in range(12):
        obs.append(state.motorState[i].dq)

    obs.extend(action_history[-1][0])
    obs += [0] * 4
    return np.array(obs, dtype=np.float32)


def normalize_observation(obs, loaded_mean, loaded_var, clip_obs):
    return np.clip(
        (obs - loaded_mean) / np.sqrt(loaded_var + 1e-8),
        -clip_obs,
        clip_obs
    )


def push_history(deq, e):
    if len(deq) == deq.maxlen:
        deq.popleft()
    deq.append(e)


def main(args):
    device = 'cpu'

    # prop_enc_pth = 'src/models/prop_encoder_1200.pt'
    # mlp_pth = 'src/models/mlp_1200.pt'
    # mean_file = 'src/models/mean1200.csv'
    # var_file = 'src/models/var1200.csv'

    prop_enc_pth = 'src/models_new/prop_encoder_400.pt'
    mlp_pth = 'src/models_new/mlp_400.pt'
    mean_file = 'src/models_new/mean400.csv'
    var_file = 'src/models_new/var400.csv'

    udp = sdk.UDP(LOCAL_PORT, TARGET_IP, TARGET_PORT, LOW_CMD_LENGTH, LOW_STATE_LENGTH, -1)
    
    cmd = sdk.LowCmd()
    state = sdk.LowState()
    udp.InitCmdData(cmd)
    cmd.levelFlag = LOWLEVEL

    prop_loaded_encoder = torch.jit.load(prop_enc_pth).to(device)
    loaded_mlp = torch.jit.load(mlp_pth).to(device)
    loaded_mean = np.loadtxt(mean_file, dtype=np.float32)[0]
    loaded_var = np.loadtxt(var_file, dtype=np.float32)[0]
    clip_obs = 10

    action_mean = np.array([0.05,  0.8, -1.4, -0.05,  0.8, -1.4, 0.05,  0.8, -1.4,-0.05,  0.8, -1.4], dtype=np.float32)
    Kp = 35
    Kd = 0.6
    act_history = deque([np.zeros((1, 12)) for _ in range(4)], maxlen=4)
    
    calc_latent_every_steps = 2
    control_freq_hz = 100
    cycle_duration_s = 1.0 / control_freq_hz
    print('Expected cycle duration:', math.ceil(cycle_duration_s * 1000.0), 'ms')

    if args.real and args.aliengo:        
        conn = RealAlienGo()
    if args.real:        
        conn = RealGo1()
    else:
        conn = simulation.Simulation(config) 
        if args.standpos:
            conn.set_keyframe(3)
        else:
            conn.set_keyframe(0)
    
    conn.start()
    if not args.standpos:
        standup(conn, None, args.aliengo)
    
    obs = to_observation(conn.wait_latest_state(), act_history)
    obs_history = deque([obs]*50, maxlen=51)
    
    step = 0
    latent_p = None
    with torch.no_grad():
        while args.real or conn.viewer.is_running():
            start_time = time.time()

            push_history(obs_history, to_observation(conn.wait_latest_state(), act_history))
            obs = np.concatenate(
                [np.concatenate(obs_history), np.zeros(28, dtype=np.float32)]
            )
            obs = normalize_observation(obs, loaded_mean, loaded_var, clip_obs)
            obs_torch = torch.from_numpy(obs).cpu().reshape(1, -1)
    
            with torch.no_grad():
                if step%calc_latent_every_steps== 0:
                    latent_p = prop_loaded_encoder(obs_torch[:,:42*50])
                action_ll = loaded_mlp(
                    torch.cat([obs_torch[:,42*50:42*(50 + 1)], latent_p], 1)
                )

            # normalize action
            push_history(act_history, action_ll)
            action = act_history[0][0] * 0.4 + action_mean
            
            # cmd = command.Command(q=action, Kp=[Kp]*12, Kd=[Kd]*12)
            command = command.Command(q=action, Kp=[Kp]*12, Kd=[Kd]*12)
            # cmd.clamp_q()

            # for i in range(12):
            #     cmd.motorCmd[i].q = command.get_command(i)[0]
            #     cmd.motorCmd[i].dq = command.get_command(i)[1]
            #     cmd.motorCmd[i].Kp = command.get_command(i)[2]
            #     cmd.motorCmd[i].Kd = command.get_command(i)[3]
            #     cmd.motorCmd[i].tau = command.get_command(i)[4]

            for i in range( 12 ):
                setup_motor(cmd, i, *command.get_command(i))

            udp.SetSend( cmd )
            udp.Send() 

            # if args.aliengo:
            #     conn.send(cmd.aliengo_cmd())
            # else:
            #     conn.send(cmd.robot_cmd())
                       
            duration = time.time() - start_time
            if duration < cycle_duration_s:
                time.sleep(cycle_duration_s - duration)
            else:
                print('too slow:', math.ceil(duration * 1000), 'ms')
            step += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--real', action='store_true')
    parser.add_argument('-a', '--aliengo', action='store_true')
    parser.add_argument('-s', '--standpos', action='store_true')
    main(parser.parse_args())
