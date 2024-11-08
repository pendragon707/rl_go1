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
#sim.set_motor_positions(positions.laydown_position_2())

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


stand_position = positions.laydown_position_2()

while sim.viewer.is_running():
    cur_state = connection.get_latest_state()
    connection.send(make_position_cmd(stand_position))
    time.sleep(0.01)
