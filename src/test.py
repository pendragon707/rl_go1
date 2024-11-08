import time
import simulation
import config

from ucl.lowCmd import lowCmd
from ucl.complex import motorCmd, motorCmdArray
from ucl.enums import MotorModeLow

from freedogs2py_bridge import MujocoConnectionProxy


sim = simulation.Simulation(config)
sim.set_keyframe(1)

connection = MujocoConnectionProxy(sim)
sim.start()

while sim.viewer.is_running():
    connection.get_latest_state()
    
    lcmd = lowCmd()
    mCmdArr = motorCmdArray()
    mCmdArr.setMotorCmd('FR_1', motorCmd(mode=MotorModeLow.Servo, q=0.0, Kp=3.0))
    lcmd.motorCmd = mCmdArr
    
    connection.send(lcmd)
    time.sleep(0.01)
