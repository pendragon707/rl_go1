from datetime import datetime

import os
import math
import time
import torch
import sys
import numpy as np
from collections import deque

from ucl.common import byte_print, decode_version, decode_sn, getVoltage, pretty_print_obj, lib_version
from ucl.lowState import lowState
from ucl.lowCmd import lowCmd
from ucl.unitreeConnection import unitreeConnection, LOW_WIFI_DEFAULTS, LOW_WIRED_DEFAULTS
from ucl.enums import GaitType, SpeedLevel, MotorModeLow
from ucl.complex import motorCmd, motorCmdArray

import pickle


motors_names = [
    'FR_0', 'FR_1', 'FR_2',
    'FL_0', 'FL_1', 'FL_2',
    'RR_0', 'RR_1', 'RR_2',
    'RL_0', 'RL_1', 'RL_2'
]


def quatToEuler(quat):
    qw, qx, qy, qz = quat
    # roll (x-axis rotation)
    sinr_cosp = 2 * (qw * qx + qy * qz)
    cosr_cosp = 1 - 2 * (qx * qx + qy * qy)

    r = []
    r.append(math.atan2(sinr_cosp, cosr_cosp))

    # pitch (y-axis rotation)
    sinp = 2 * (qw * qy - qz * qx)
    if abs(sinp) >= 1:
    # use 90 degrees if out of range
        if sinp > 0:
            r.append(math.pi / 2)
        else:
            r.append(-math.pi / 2)
    else:
        r.append(math.asin(sinp))

    # yaw (z-axis rotation)
    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
    r.append(math.atan2(siny_cosp, cosy_cosp))
    return r


class GO1Connection:

    def __init__(self):
        self.conn = unitreeConnection(LOW_WIRED_DEFAULTS)
        self.conn.startRecv()

    def sendInitCmd(self):
        lcmd = lowCmd()
        cmd_bytes = lcmd.buildCmd(debug=False)
        self.conn.send(cmd_bytes)
        time.sleep(0.2)

    def getState(self):
        data = self.conn.getData()
        if len(data) > 0:
            lstate = lowState()
            lstate.parseData(data[-1])
            return lstate

        return None

    def getObservation(self, state, last_action = None):
        obs = []

        imu_quaternion = state.imu.quaternion  # TODO Check Euler angles from dog
        obs += quatToEuler(imu_quaternion)[:2]

        for i in range(12):
            obs.append(state.motorState[i].q)

        for i in range(12):
            obs.append(state.motorState[i].dq)

        if last_action is not None:
           obs += last_action.tolist()
        else:
           obs += [0] * 12

        obs += [0] * 4  # delta speed_vec
        return np.array(obs, dtype=np.float32)

    def positionAction(self, position, pgain, dgain):
        lstate = lowState()
        lcmd = lowCmd()

        mCmdArr = motorCmdArray()

        clamps = [
            (-0.804595, 0.914805),
            (-0.676763, 3.938925),
            (-2.708668, -0.872154),
            (-0.872175, 0.840383),
            (-0.669436, 3.948008),
            (-2.782182, -0.881157),
            (-0.824942, 0.897850),
            (-0.685604, 4.574027),
            (-2.781213, -0.873002),
            (-0.899243, 0.810772),
            (-0.662957, 4.552348),
            (-2.791306, -0.877725)
        ]

        for i, name in enumerate(motors_names):
            p = position[0][i]
            if p < clamps[i][0]:
                p = clamps[i][0]
            elif p > clamps[i][1]:
                p = clamps[i][1]

            mCmdArr.setMotorCmd(i,  motorCmd(mode=MotorModeLow.Servo, q=p, dq=0, Kp = pgain, Kd = dgain, tau = 0.0))

        lcmd.motorCmd = mCmdArr
        cmd_bytes = lcmd.buildCmd(debug=False)
        self.conn.send(cmd_bytes)
        return lstate


def log(log_of, step, step_time, send_action_ns, state, obs, action, calc_env):
    data = pickle.dumps((step, step_time, send_action_ns, state, obs, action, calc_env))
    size = len(data)
    log_of.write(size.to_bytes(4, 'big') + data)


def main(log_of):
    device = 'cpu'

    prop_enc_pth = 'models/prop_encoder_1200.pt'
    mlp_pth = 'models/mlp_1200.pt'

    prop_loaded_encoder = torch.jit.load(prop_enc_pth).to(device)
    loaded_mlp = torch.jit.load(mlp_pth).to(device)

    calc_latent_every_steps = 2
    control_freq_hz = 100
    cycle_duration_s = 1.0 / control_freq_hz

    print('Expected cycle duration:', math.ceil(cycle_duration_s * 1000.0), 'ms')

    t_steps = 50

    # Test on emulator!!!!
    pid_coeff = 5 # May be too much?
    dgain = 0.6 # unnecessary constant

    conn = GO1Connection()

    conn.sendInitCmd()
    state = conn.getState()
    assert state is not None
    obs = conn.getObservation(state)

    log(log_of, -1, time.time(), None, state, obs, None, False)

    history = deque([obs]*t_steps, maxlen=t_steps)

    step = 0
    latent_p = None
    with torch.no_grad():
        while True:
            start_time = time.time()

            state = conn.getState()
            if state is not None:
                obs = conn.getObservation(state)

                # calculate latent vec
                if step % calc_latent_every_steps == 0 or latent_p is None:
                    history_vec = np.array(history, dtype=np.float32).flatten().reshape(1, -1)
                    history_vec = torch.tensor(history_vec, device=device, requires_grad=False)
                    latent_p = prop_loaded_encoder(history_vec)
                    calc_env = True
                else:
                    calc_env = False

                # calc action
                obs_torch = torch.tensor(obs.reshape(1, -1), device=device)
                action = loaded_mlp(torch.cat([obs_torch, latent_p], 1))
                action = action.cpu().detach().numpy()

                # history deque push, pop
                history.popleft()
                history.append(obs)
                # send action
                log(log_of, step, start_time, time.time_ns(), state, obs, action, calc_env)
                conn.positionAction(action, pgain = pid_coeff, dgain = dgain)

            duration = time.time() - start_time
            if duration < cycle_duration_s:
                time.sleep(duration)
            else:
                print('too slow:', math.ceil(duration * 1000), 'ms')
            step += 1


if __name__ == '__main__':
    now_s = datetime.now().strftime("%y%m%dT%H%M%S")
    with open(f'log_{now_s}.txt', 'wb') as of:
        main(of)
