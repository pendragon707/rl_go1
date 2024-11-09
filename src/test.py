import time
import simulation
import config


sim_conn = simulation.Simulation(config)
sim_conn.set_keyframe(1)
sim_conn.start()

while sim_conn.viewer.is_running():
    sim_conn.get_latest_state()
    time.sleep(0.01)
