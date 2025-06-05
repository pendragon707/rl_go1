import os
from pathlib import Path
import sys
print(os.getcwd())
sys.path.append(os.getcwd())

import argparse
import math
import time
import torch
import numpy as np
from collections import deque

from scripts.standup import standup

from motor_data_csv_writer import csv_fill

import src.utils as utils
from src.command import Command
from src.robots import RealAlienGo, RealGo1
from src.robots.simulation import Simulation, config

sys.path.append("./submodules/free-dog-sdk/")
from ucl.lowCmd import lowCmd
from ucl.lowState import lowState
from ucl.unitreeConnection import unitreeConnection, LOW_WIRED_DEFAULTS

sys.path.append('./submodules/unitree_legged_sdk/lib/python/amd64')
import robot_interface_aliengo as sdk


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
    print( type(obs) )
    print( type(loaded_mean) )
    print( type(loaded_var) )

    print(obs.shape)
    print(loaded_mean.shape)
    print(loaded_var.shape)

    obs = np.array(obs, dtype=np.float32)
    loaded_mean = np.array(loaded_mean, dtype=np.float32)
    loaded_var = np.array(loaded_var, dtype=np.float32)

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

    # prop_enc_pth = Path(os.getcwd()) / 'models/model_kv/prop_encoder_1200.pt'
    # mlp_pth = Path(os.getcwd()) / 'models/model_kv/mlp_1200.pt'
    # mean_file = Path(os.getcwd()) / 'models/model_kv/mean1200.csv'
    # var_file = Path(os.getcwd()) / 'models/model_kv/var1200.csv'

    # prop_enc_pth = Path(os.getcwd()) / 'models/model_05_03/prop_encoder_1200.pt'
    # mlp_pth = Path(os.getcwd()) / 'models/model_05_03/mlp_1200.pt'
    # mean_file = Path(os.getcwd()) / 'models/model_05_03/mean1200.csv'
    # var_file = Path(os.getcwd()) / 'models/model_05_03/var1200.csv'

    # prop_enc_pth = Path(os.getcwd()) / 'models/model_16k_dagger_1200/prop_encoder_1200.pt'
    # mlp_pth = Path(os.getcwd()) / 'models/model_16k_dagger_1200/mlp_1200.pt'
    # mean_file = Path(os.getcwd()) / 'models/model_16k_dagger_1200/mean1200.csv'
    # var_file = Path(os.getcwd()) / 'models/model_16k_dagger_1200/var1200.csv'

    prop_enc_pth = Path(os.getcwd()) / 'models/rot_exp4_dagger/prop_encoder_1200.pt'
    mlp_pth = Path(os.getcwd()) / 'models/rot_exp4_dagger/mlp_1200.pt'
    mean_file = Path(os.getcwd()) / 'models/rot_exp4_dagger/mean1200.csv'
    var_file = Path(os.getcwd()) / 'models/rot_exp4_dagger/var1200.csv'

    prop_loaded_encoder = torch.jit.load(prop_enc_pth).to(device)
    loaded_mlp = torch.jit.load(mlp_pth).to(device)
    loaded_mean = np.loadtxt(mean_file, dtype=np.float32)[0]
    loaded_var = np.loadtxt(var_file, dtype=np.float32)[0]
    clip_obs = 10

    action_mean = np.array([0.05,  0.8, -1.4, -0.05,  0.8, -1.4, 0.05,  0.8, -1.4,-0.05,  0.8, -1.4], dtype=np.float32)
    # Kp = 35
    # Kd = 0.6
    Kp = 80
    Kd = 2

    act_history = deque([np.zeros((1, 12)) for _ in range(4)], maxlen=4)
    
    calc_latent_every_steps = 2
    control_freq_hz = 100
    cycle_duration_s = 1.0 / control_freq_hz
    print('Expected cycle duration:', math.ceil(cycle_duration_s * 1000.0), 'ms')

    if args.real and args.aliengo:        
        conn = RealAlienGo()
        # conn.start()   

    elif args.real:        
        conn = RealGo1()
        # conn.start()   

    else:
        conn = Simulation(config) 
        if args.standpos:
            conn.set_keyframe(3)
        else:
            conn.set_keyframe(0)    
        # conn.start()

    conn.start()

    if not args.standpos:
        standup(conn, None)

    print("stand")
    
    obs = to_observation(conn.wait_latest_state(), act_history)
    obs_history = deque([obs]*50, maxlen=51)
    
    step = 0
    latent_p = None
    motiontime = 0
    with torch.no_grad():
        while args.real or conn.viewer.is_running():
            motiontime +=1 
            # time.sleep(0.002)

            start_time = time.time()            

            if motiontime % 2 == 0:
                state = conn.wait_latest_state()
                push_history(obs_history, to_observation(conn.wait_latest_state(), act_history))
                # ===== logger
                tick = state.tick
                torque_vector_real = [state.motorState[i].tauEst for i in range(12)]
                position_vector_real = [state.motorState[i].q for i in range(12)]
                csv_fill(tick, torque_vector_real, position_vector_real, '/home/none/rl_go1/scripts/motorstate.csv')
                print(motiontime)
                # ===== logger  
            else:
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
            
            command = Command(q=action, Kp=[Kp]*12, Kd=[Kd]*12)
            # cmd.clamp_q()

            # if args.aliengo:
            #     conn.set_cmd(command)
            #     conn.send()
            # else:
            #     conn.send(command.robot_cmd())
            conn.send(command)
                       
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
