import time
import argparse

import os
import sys
print(os.getcwd())
sys.path.append(os.getcwd())

import src.config as config
import src.utils as utils
import src.positions as positions

# from src.plots import csv_fill 

from src.robots import RealAlienGo, RealGo1
from src.robots.simulation.simulation import Simulation

def standup(conn, viewer = None):
    phase = 0
    phase_cycles = 0
    
    while viewer is None or viewer.is_running():
        state = conn.wait_latest_state()
        
        if phase == 0:
            if phase_cycles >= 100:
                phase = 1   
                phase_cycles = 0

        elif phase == 1:
            if phase_cycles >= 100:
                print("go to 2")
                phase = 2
                phase_cycles = 0 
                init_q = utils.q_vec(state)             

            conn.send(positions.laydown_command())

        elif phase == 2:  
            # init_q = utils.q_vec(state)
            stand_command = positions.stand_command_2()            

            q_step, flag = utils.interpolate(init_q, stand_command.q, phase_cycles, 500)            
            command = stand_command.copy(q = q_step)

            conn.send(command)        

            if flag:            
                return state, command   

        phase_cycles += 1
        time.sleep(0.01)

    return state

def standup_2(conn : RealAlienGo, viewer = None):
    phase = 0
    phase_cycles = 0
    
    while viewer is None or viewer.is_running():
        state = conn.wait_latest_state()
        
        if phase == 0:
            if phase_cycles >= 100:
                phase = 1  
                phase_cycles = 0

        elif phase == 1:  
            init_q = utils.q_vec(state)            
            stand_command = positions.stand_command_2()

            q_step, flag = utils.interpolate(init_q, stand_command.q, phase_cycles, 500)            
            command = stand_command.copy(q = q_step)

            conn.send(command)        

            if flag:            
                return state, command       

        phase_cycles += 1
        time.sleep(0.01)

    return state

def main(args):
    config.ENABLE_SIMULATION = True

    if not args.real:
        conn = Simulation(config)
        conn.set_keyframe(0)
        conn.start()        
        
        viewer = conn.viewer
    elif args.aliengo:        
        conn = RealAlienGo()
        conn.start()             

        viewer = None
    else:
        conn = RealGo1()
        conn.start()
        viewer = None    

    time.sleep(0.2)
    
    _, command = standup(conn, viewer)

    while viewer is None or viewer.is_running():
        conn.send(command)

        time.sleep(0.01)  


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--real', action='store_true')
    parser.add_argument('-a', '--aliengo', action='store_true')    
    main(parser.parse_args())