import os
from pathlib import Path
import sys
print(os.getcwd())
sys.path.append(os.getcwd())

from collections import deque
import argparse
import math
import time
import torch
import numpy as np

from scripts.standup import standup

import src.utils as utils
import src.positions as positions
from src.command import Command
from src.robots import RealAlienGo, RealGo1
from src.robots.simulation import Simulation, config

from pynput import keyboard


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


class PolicyState:
    def __init__(self, dir_path, device='cpu'):
        self.key_a = None
        self.key_s = None
        self.key_h = None
        self.key_k = None
        self.key_d = None

        prop_enc_pth = dir_path / 'prop_encoder_1200.pt'
        mlp_pth = dir_path / 'mlp_1200.pt'
        mean_file = dir_path / 'mean1200.csv'
        var_file = dir_path / 'var1200.csv'

        self.prop_loaded_encoder = torch.jit.load(prop_enc_pth).to(device)
        self.loaded_mlp = torch.jit.load(mlp_pth).to(device)
        self.loaded_mean = np.loadtxt(mean_file, dtype=np.float32)[0]
        self.loaded_var = np.loadtxt(var_file, dtype=np.float32)[0]
        self.clip_obs = 10

        self.action_mean = np.array([0.05,  0.8, -1.4, -0.05,  0.8, -1.4, 0.05,  0.8, -1.4,-0.05,  0.8, -1.4], dtype=np.float32)
        self.Kp = 35
        self.Kd = 0.6

        self.calc_latent_every_steps = 2

    def reset(self):
        self.step = 0
        self.obs_history = None
        self.act_history = deque([np.zeros((1, 12)) for _ in range(4)], maxlen=4)
    
    def press_key(self, key):
        if key.char == 's' and self.key_s is not None:
            self.key_s.reset()
            return self.key_s
        
        if key.char == 'a' and self.key_a is not None:
            self.key_a.reset()
            return self.key_a
        
        if key.char == 'd' and self.key_d is not None:
            self.key_d.reset()
            return self.key_d
        
        if key.char == 'h' and self.key_h is not None:
            self.key_h.reset()
            return self.key_h
        
        if key.char == 'k' and self.key_k is not None:
            self.key_k.reset()
            return self.key_k
        
        return self

    def process(self, state):
        if self.obs_history is None:
            obs = to_observation(state, self.act_history)
            self.obs_history = deque([obs]*50, maxlen=51)

        push_history(self.obs_history, to_observation(state, self.act_history))
        obs = np.concatenate(
            [np.concatenate(self.obs_history), np.zeros(28, dtype=np.float32)]
        )
        obs = normalize_observation(obs, self.loaded_mean, self.loaded_var, self.clip_obs)
        obs_torch = torch.from_numpy(obs).cpu().reshape(1, -1)

        with torch.no_grad():
            if self.step % self.calc_latent_every_steps== 0:
                self.latent_p = self.prop_loaded_encoder(obs_torch[:,:42*50])
            action_ll = self.loaded_mlp(
                torch.cat([obs_torch[:,42*50:42*(50 + 1)], self.latent_p], 1)
            )
        # normalize action
        push_history(self.act_history, action_ll)
        action = self.act_history[0][0] * 0.4 + self.action_mean
        
        return Command(q=action, Kp=[self.Kp]*12, Kd=[self.Kd]*12), self


class StandState:
    def __init__(self, total_cycles=500):
        self.key_a = None
        self.key_d = None
        self.key_h = None
        self.key_k = None
        
        self.next_state = None
        self.cycles = 0
        self.total_cycles = total_cycles
        self.stand_command = positions.stand_command_2()

    def reset(self):
        self.stand_command = positions.stand_command_2()
        self.cycles = 0

    def press_key(self, key):
        if self.next_state is not None:
            return self
        
        if key.char == 'a':
            self.key_a.reset()
            return self.key_a
        
        if key.char == 'd':
            self.key_d.reset()
            return self.key_d
        
        if key.char == 'h':
            self.key_h.reset()
            return self.key_h
        
        if key.char == 'k':
            self.key_k.reset()
            return self.key_k
        
        return self

    def process(self, state):
        if self.cycles == 0:
            self.init_q = utils.q_vec(state)
            
        q_step = utils.interpolate(self.init_q, self.stand_command.q, self.cycles, total_cycles=self.total_cycles)
        self.cycles += 1

        next_state = self
        if self.cycles >= self.total_cycles and self.next_state is not None:
            self.next_state.reset()
            next_state = self.next_state
        
        return self.stand_command.copy(q = q_step), next_state


def main(args):
    control_freq_hz = 100
    cycle_duration_s = 1.0 / control_freq_hz
    print('Expected cycle duration:', math.ceil(cycle_duration_s * 1000.0), 'ms')

    if args.real and args.aliengo:        
        conn = RealAlienGo()
        # conn.start()   
    elif args.real:
        conn = RealGo1()
    else:
        conn = Simulation(config) 
        if args.standpos:
            conn.set_keyframe(3)
        else:
            conn.set_keyframe(0)
    
    stand = StandState()

    forward_path = Path(os.getcwd()) / 'models/model_16k_dagger_1200'
    backward_path = Path(os.getcwd()) / 'models/back_kv'
    # left_path = Path(os.getcwd()) / 'models/left'
    # right_path = Path(os.getcwd()) / 'models/right'
    left_path = Path(os.getcwd()) / 'models/model_05_03'
    right_path = Path(os.getcwd()) / 'models/model_05_03'
    
    forward = PolicyState(forward_path)
    backward = PolicyState(backward_path)
    left = PolicyState(left_path)
    right = PolicyState(right_path)

    forward_after_stand = StandState(50)
    backward_after_stand = StandState(50)
    right_after_stand = StandState(50)
    left_after_stand = StandState(50)
    
    stand.key_d = forward
    stand.key_a = backward
    stand.key_h = right
    stand.key_k = left

    forward.key_s = stand
    forward.key_a = backward_after_stand

    backward.key_s = stand
    backward.key_d = forward_after_stand

    right.key_s = stand
    right.key_k = right_after_stand

    left.key_s = stand
    left.key_h = left_after_stand

    forward_after_stand.next_state = forward
    backward_after_stand.next_state = backward
    right_after_stand.next_state = right
    left_after_stand.next_state = left

    current_state = stand

    pressed_key = [None]
    def on_release(key):
        pressed_key[0] = key

    listener = keyboard.Listener(on_release=on_release)
    listener.start()

    conn.start()
    if not args.standpos:
        state = standup(conn)
    
    while args.real or conn.viewer.is_running():
        start_time = time.time()
        state = conn.wait_latest_state()
        cmd, current_state = current_state.process(state)
        conn.send(cmd.robot_cmd())

        if pressed_key[0] is not None:
            current_state = current_state.press_key(pressed_key[0])
            pressed_key[0] = None
            
        duration = time.time() - start_time
        if duration < cycle_duration_s:
            time.sleep(cycle_duration_s - duration)
        else:
            print('too slow:', math.ceil(duration * 1000), 'ms')
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--real', action='store_true')
    parser.add_argument('-a', '--aliengo', action='store_true')
    parser.add_argument('-s', '--standpos', action='store_true')
    main(parser.parse_args())
