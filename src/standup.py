import time
import simulation
import numpy as np

import config
import positions
import utils


config.ENABLE_SIMULATION = True

sim_conn = simulation.Simulation(config)

sim_conn.set_keyframe(0)
sim_conn.set_motor_positions(positions.laydown_q)
sim_conn.start()


time.sleep(0.2)

cycles = 0
phase = 0
phase_cycles = 0

stand_command = positions.stand_command()


while sim_conn.viewer.is_running():
    cur_state = sim_conn.get_latest_state()
    if cur_state is not None:
        state = cur_state
    
    if phase == 0:
        if phase_cycles >= 100:
            phase = 1
            phase_cycles = 0
    elif phase == 1:
        if phase_cycles >= 100:
            phase = 2
            phase_cycles = 0
            init_q = utils.q_vec(state)
        sim_conn.send(positions.laydown_command().robot_cmd())
    elif phase == 2:
        q_step = utils.interpolate(init_q, stand_command.q, phase_cycles, 500)
        sim_conn.send(stand_command.copy(q = q_step).robot_cmd())

    phase_cycles += 1
    time.sleep(0.01)
