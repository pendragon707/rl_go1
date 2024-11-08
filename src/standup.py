import time
import simulation
import numpy as np

from ucl.lowCmd import lowCmd
from ucl.complex import motorCmd, motorCmdArray
from ucl.enums import MotorModeLow

import config
import constants
import positions
import utils
from freedogs2py_bridge import MujocoConnectionProxy


config.ENABLE_SIMULATION = True

sim = simulation.Simulation(config)
sim.set_keyframe(0)

#sim.set_motor_positions([p[0] for p in positions.stand_position()])
sim.set_motor_positions(positions.laydown_position())

connection = MujocoConnectionProxy(sim)
sim.start()


def make_position_cmd(position):
    lcmd = lowCmd()
    mCmdArr = motorCmdArray()
    for no, pos in enumerate(position):
        mCmdArr.setMotorCmd(constants.motors_names[no], motorCmd(mode=MotorModeLow.Servo, q=pos[0], Kp=pos[1], Kd=pos[2]))
    lcmd.motorCmd = mCmdArr
    return lcmd

time.sleep(0.2)

cycles = 0
phase = 0
phase_cycles = 0

stand_position = positions.stand_position()
stand_position_vec = np.array([p[0] for p in stand_position])

def interpolate(src, dst, cycle, total_cycles):
    if cycle >= total_cycles:
        return dst

    alpha = cycle / total_cycles
    return dst * alpha + src * (1 - alpha)

def make_position_cmd_2(q, dq, Kp, Kd):
    lcmd = lowCmd()
    mCmdArr = motorCmdArray()
    for i in range(12):
        mCmdArr.setMotorCmd(constants.motors_names[i], motorCmd(mode=MotorModeLow.Servo, q=q[i], dq=dq[i], Kp=Kp[i], Kd=Kd[i], tau=0))
    lcmd.motorCmd = mCmdArr
    return lcmd

stand_dq = [0] * 12
stand_Kp = [p[1] for p in stand_position]
stand_Kd = [p[2] for p in stand_position]

while sim.viewer.is_running():
    cur_state = connection.get_latest_state()
    if cur_state is not None:
        state = cur_state
    
    if phase == 0:
        if phase_cycles >= 100:
            phase = 1
            phase_cycles = 0
            init_position_vec = np.array(utils.get_pos_vector(state))
    elif phase == 1:
        if phase_cycles >= 100:
            phase = 2
            phase_cycles = 0
            init_position_vec = np.array(utils.get_pos_vector(state))
        connection.send(make_position_cmd(positions.laydown_position_2()))
    elif phase == 2:
        position_step_vec = interpolate(init_position_vec, stand_position_vec, phase_cycles, 500)
        connection.send(make_position_cmd_2(position_step_vec, stand_dq, stand_Kp, stand_Kd))

    phase_cycles += 1
    time.sleep(0.01)
