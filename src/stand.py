import time
import simulation

import config
import positions


config.ENABLE_SIMULATION = True

sim_conn = simulation.Simulation(config)
sim_conn.set_keyframe(2)

test_command = positions.stand_command()

sim_conn.set_motor_positions(test_command.q)

sim_conn.start()
time.sleep(0.2)

while sim_conn.viewer.is_running():
    cur_state = sim_conn.get_latest_state()
    sim_conn.send(test_command.robot_cmd())
    time.sleep(0.01)
