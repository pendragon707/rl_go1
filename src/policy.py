import config

import math
import time
import torch
import numpy as np
from collections import deque
import utils

import time
import simulation
import command
import positions
from freedogs2py_bridge import RealGo1


def to_observation(state, last_action=None):
    obs = []
    imu_quaternion = state.imu.quaternion  # TODO Check Euler angles from dog
    obs += utils.quatToEuler(imu_quaternion)[:2]

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


def main():
    device = 'cpu'

    prop_enc_pth = 'src/models/prop_encoder_1200.pt'
    mlp_pth = 'src/models/mlp_1200.pt'

    prop_loaded_encoder = torch.jit.load(prop_enc_pth).to(device)
    loaded_mlp = torch.jit.load(mlp_pth).to(device)

    calc_latent_every_steps = 2
    control_freq_hz = 100
    cycle_duration_s = 1.0 / control_freq_hz

    print('Expected cycle duration:', math.ceil(cycle_duration_s * 1000.0), 'ms')

    t_steps = 50

    pgain = 35 # May be too much?
    dgain = 3 # unnecessary constant
    real = True

    if not real:
        conn = simulation.Simulation(config)
        conn.set_keyframe(2)
        conn.set_motor_positions(positions.stand_command().q)
    else:
        conn = RealGo1()

    conn.start() # TODO SendInitCmd

    state = conn.get_latest_state()
    while state is None:
        state = conn.get_latest_state()
        time.sleep(0.1)

    obs = to_observation(state)
    history = deque([obs]*t_steps, maxlen=t_steps)

    step = 0
    latent_p = None
    with torch.no_grad():
        while True:
            start_time = time.time()

            state = conn.get_latest_state()
            if state is not None:
                obs = to_observation(state)

                # calculate latent vec
                if step % calc_latent_every_steps == 0 or latent_p is None:
                    history_vec = np.array(history, dtype=np.float32).flatten().reshape(1, -1)
                    history_vec = torch.tensor(history_vec, device=device, requires_grad=False)
                    latent_p = prop_loaded_encoder(history_vec)

                # calc action
                obs_torch = torch.tensor(obs.reshape(1, -1), device=device)
                action = loaded_mlp(torch.cat([obs_torch, latent_p], 1))
                action = action.cpu().detach().numpy()

                # history deque push, pop
                history.popleft()
                history.append(obs)
                # send action
                cmd = command.Command(action[0], Kp=[pgain]*12, Kd=[dgain]*12)
                cmd.clamp_q()
                conn.send(cmd.robot_cmd())

            duration = time.time() - start_time
            if duration < cycle_duration_s:
                time.sleep(duration)
            else:
                print('too slow:', math.ceil(duration * 1000), 'ms')
            step += 1


if __name__ == '__main__':
    main()
