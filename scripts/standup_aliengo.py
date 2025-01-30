import time

import os
import sys
print(os.getcwd())
sys.path.append(os.getcwd())

import src.config as config
import src.utils as utils
import src.positions as positions

from src.robots import RealAlienGo, RealGo1
from src.robots.simulation.simulation import Simulation

def standup(conn : RealAlienGo, viewer = None, aliengo = True):
    phase = 0
    phase_cycles = 0

    stand_command = positions.stand_command_2()
    while viewer is None or viewer.is_running():
        state = conn.wait_latest_state()
        
        if phase == 0:
            if phase_cycles >= 100:
                phase = 1
                phase_cycles = 0

        elif phase == 1:
            if phase_cycles >= 100:
                phase = 2
                phase_cycles = 0
                init_q = utils.q_vec(state)

            if aliengo:     
                conn.set_cmd(positions.laydown_command())
                conn.send()

            else:
                conn.send(positions.laydown_command().robot_cmd())

        elif phase == 2:            
            q_step = utils.interpolate(init_q, stand_command.q, phase_cycles, 500)            
            command = stand_command.copy(q = q_step)
            if aliengo:                            
                conn.set_cmd(command)
                conn.send()

            else:
                conn.send(command.robot_cmd())

            if phase_cycles == 500:
                return state, command       

        phase_cycles += 1
        time.sleep(0.01)

def main():
    config.ENABLE_SIMULATION = True

    real = True
    aliengo = True
    conn = None

    if not real:
        conn = Simulation(config)
        conn.set_keyframe(0)
        
        viewer = conn.viewer
    elif aliengo:        
        conn = RealAlienGo()

        viewer = None
    else:
        conn = RealGo1()
        viewer = None

    conn.start()

    time.sleep(0.2)
    
    _, command = standup(conn, viewer, aliengo)

    while viewer is None or viewer.is_running():
        if aliengo:   
            conn.set_cmd( command )         
            conn.send( )
        else:
            conn.send(command.robot_cmd())

        time.sleep(0.01)  


if __name__ == '__main__':
    main()