import argparse
import config

import math
import time
import torch
import numpy as np
from collections import deque
import utils

import config
import positions
import utils

import time
import simulation
import command
import standup
from freedogs2py_bridge import RealGo1, RealAlienGo

import sys

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



def standup(cmd, conn = None, viewer = None, aliengo = True, udp = None):
    phase = 0
    phase_cycles = 0

    stand_command = positions.stand_command_2()
    while viewer is None or viewer.is_running():
        # state = conn.wait_latest_state()

        state = sdk.LowState()
        udp.Recv()
        udp.GetRecv(state)
                
        # for i in range(12):        
        #     print(state.motorState[ i ].q, end = " ") 
        
        if phase == 0:
            if phase_cycles >= 100:
                phase = 1
                phase_cycles = 0
        elif phase == 1:
            if phase_cycles >= 100:
                phase = 2
                phase_cycles = 0
                init_q = utils.q_vec(state)
            if aliengo:     
                # conn.set_cmd( positions.laydown_command().aliengo_cmd() )
                # conn.send( positions.laydown_command().aliengo_cmd() )

                print("fasa 1")

                com = positions.laydown_command()

                for i in range(12):
                    cmd.motorCmd[i].q = com.get_command(i)[0]
                    cmd.motorCmd[i].dq = com.get_command(i)[1]
                    cmd.motorCmd[i].Kp = com.get_command(i)[2]
                    cmd.motorCmd[i].Kd = com.get_command(i)[3]
                    cmd.motorCmd[i].tau = com.get_command(i)[4]

                udp.SetSend( cmd )
                udp.Send()                                
            else:
                conn.send(positions.laydown_command().robot_cmd())
        elif phase == 2:
            print("fasa 2")

            q_step = utils.interpolate(init_q, stand_command.q, phase_cycles, 500)            
            command = stand_command.copy(q = q_step)
            if aliengo:   
                # print( cmd.aliengo_cmd() )             
                # conn.send(cmd.aliengo_cmd())

                # conn.set_cmd( cmd.aliengo_cmd() )
                # conn.send( cmd.aliengo_cmd() )

                for i in range(12):
                    cmd.motorCmd[i].q = command.get_command(i)[0]
                    cmd.motorCmd[i].dq = command.get_command(i)[1]
                    cmd.motorCmd[i].Kp = command.get_command(i)[2]
                    cmd.motorCmd[i].Kd = command.get_command(i)[3]
                    cmd.motorCmd[i].tau = command.get_command(i)[4]

                udp.SetSend( cmd )
                udp.Send() 

            else:
                print("else")
                udp.SetSend( cmd )
                udp.Send() 

                # conn.send(cmd.robot_cmd())

            if phase_cycles > 200:
                print(phase_cycles)  
                

            if phase_cycles == 500:
                print(phase_cycles)  
                return state, cmd  

        phase_cycles += 1
        time.sleep(0.01)


class Command:
    def __init__(self, q=[0.]*12, dq=[0.]*12, Kp=[0.]*12, Kd=[0.]*12, tau=[0.]*12):
        self.q = np.array(q, dtype=np.float32)
        self.dq = np.array(dq, dtype=np.float32)
        self.Kp = np.array(Kp, dtype=np.float32)
        self.Kd = np.array(Kd, dtype=np.float32)
        self.tau = np.array(tau, dtype=np.float32)

    def robot_cmd(self) -> lowCmd:
        lcmd = lowCmd()
        mCmdArr = motorCmdArray()
        for i in range(12):
            mCmdArr.setMotorCmd(
                constants.motors_names[i],
                motorCmd(mode=MotorModeLow.Servo,
                         q=self.q[i].item(),
                         dq=self.dq[i].item(),
                         Kp=self.Kp[i].item(),
                         Kd=self.Kd[i].item(),
                         tau=self.tau[i].item())
            )
        lcmd.motorCmd = mCmdArr
        return lcmd
    

    def aliengo_cmd(self, lcmd, p = False):        
        for i in range(12):
            lcmd.motorCmd[i].q = self.q[i].item()
            lcmd.motorCmd[i].dq = self.dq[i].item()
            lcmd.motorCmd[i].Kp = self.Kp[i].item()
            lcmd.motorCmd[i].Kd = self.Kd[i].item()
            lcmd.motorCmd[i].tau = self.tau[i].item()
        
        return lcmd

    def get_command(self, num):
        return (
                self.q[num].item(),
                self.dq[num].item(),
                self.Kp[num].item(),
                self.Kd[num].item(),
                self.tau[num].item(),
            )

    def clamp_q(self):
        self.q = np.clip(self.q, constants.q_mujoco_min, constants.q_mujoco_max)

    def copy(self, q=None, dq=None, Kp=None, Kd=None, tau=None):
        return Command(
            q = self.q.copy() if q is None else q,
            dq = self.dq.copy() if dq is None else dq,
            Kp = self.Kp.copy() if Kp is None else Kp,
            Kd = self.Kd.copy() if Kd is None else Kd,
            tau = self.tau.copy() if tau is None else tau,
        )


# def get_state():
#     state = sdk.LowState()
#     udp.Recv()
#     udp.GetRecv(state)


def to_observation(state, action_history):
    print("hey")

    obs = []
    imu_quaternion = state.imu.quaternion
    obs.extend(utils.quatToEuler(imu_quaternion)[:2])

    for i in range(12):
        obs.append(state.motorState[i].q)

    for i in range(12):
        obs.append(state.motorState[i].dq)

    print(obs)

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

    prop_enc_pth = 'src/models/prop_encoder_1200.pt'
    mlp_pth = 'src/models/mlp_1200.pt'
    mean_file = 'src/models/mean1200.csv'
    var_file = 'src/models/var1200.csv'

    # prop_enc_pth = 'src/models_new/prop_encoder_400.pt'
    # mlp_pth = 'src/models_new/mlp_400.pt'
    # mean_file = 'src/models_new/mean400.csv'
    # var_file = 'src/models_new/var400.csv'

    # udp = sdk.UDP(LOCAL_PORT, TARGET_IP, TARGET_PORT, LOW_CMD_LENGTH, LOW_STATE_LENGTH, -1)
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
    
    # conn.start()
    # if not args.standpos:
    #     standup.standup(conn)

    # _, command = standup(cmd, udp = udp)

    udp.Recv()
    udp.GetRecv(state)
    
    # obs = to_observation(conn.wait_latest_state(), act_history)
    obs = to_observation(state, act_history)
    obs_history = deque([obs]*50, maxlen=51)

    print(obs.shape)
    
    step = 0
    latent_p = None
    with torch.no_grad():        
        while args.real or conn.viewer.is_running():
            start_time = time.time()

            print(start_time)

            udp.Recv()
            udp.GetRecv(state)

            push_history(obs_history, to_observation(state, act_history))
            # push_history(obs_history, to_observation(conn.wait_latest_state(), act_history))
            obs = np.concatenate(
                [np.concatenate(obs_history), np.zeros(28, dtype=np.float32)]
            )

            obs = normalize_observation(obs, loaded_mean, loaded_var, clip_obs)
            obs_torch = torch.from_numpy(obs).cpu().reshape(1, -1)

            print(obs.shape)
    
            with torch.no_grad():
                if step%calc_latent_every_steps== 0:
                    latent_p = prop_loaded_encoder(obs_torch[:,:42*50])
                action_ll = loaded_mlp(
                    torch.cat([obs_torch[:,42*50:42*(50 + 1)], latent_p], 1)
                )

            # normalize action
            push_history(act_history, action_ll)
            action = act_history[0][0] * 0.4 + action_mean
            print(action.shape)
            
            # cmd = command.Command(q=action, Kp=[Kp]*12, Kd=[Kd]*12)
            # command = command.Command(q=action, Kp=[Kp]*12, Kd=[Kd]*12)
            command = Command(q=action, Kp=[Kp]*12, Kd=[Kd]*12)
            # cmd.clamp_q()

            for i in range(12):
                cmd.motorCmd[i].q = command.get_command(i)[0]
                cmd.motorCmd[i].dq = command.get_command(i)[1]
                cmd.motorCmd[i].Kp = command.get_command(i)[2]
                cmd.motorCmd[i].Kd = command.get_command(i)[3]
                cmd.motorCmd[i].tau = command.get_command(i)[4]

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
