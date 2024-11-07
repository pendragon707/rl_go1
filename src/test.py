import time
import simulation
import config

from freedogs2py_bridge import MujocoConnectionProxy


sim = simulation.Simulation(config)
sim.set_keyframe(1)

connection = MujocoConnectionProxy(sim)
sim.start()

while sim.viewer.is_running():
    connection.get_latest_state()
    time.sleep(0.01)
