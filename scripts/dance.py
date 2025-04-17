import argparse
import math
import time

import os
import sys
print(os.getcwd())
sys.path.append(os.getcwd())

from src import utils
from src.command import Command

import src.positions as positions
from src.robots import RealAlienGo, RealGo1
from src.robots.simulation import Simulation, config

def dance_1(conn : RealAlienGo, viewer = None):
    phase = 0
    phase_cycles = 0
    num_steps = 500

    while viewer is None or viewer.is_running():
        state = conn.wait_latest_state()
        
        if phase == 0:
            if phase_cycles >= 100:
                print("Go to phase 1") 
                phase = 1
                phase_cycles = 0

        elif phase == 1:    
            if phase_cycles >= 100:
                print("Go to phase 2")   

                phase = 2
                phase_cycles = 0
                num_steps = 500    

                init_q = utils.q_vec(state)            

            conn.send(positions.laydown_command())

        elif phase == 2:             
            stand_command = positions.stand_command_2()        
            q_step, flag = utils.interpolate(init_q, stand_command.q, phase_cycles, num_steps)            
            command = stand_command.copy(q = q_step)

            conn.send(command)     
            # conn.send(stand_command)            

            if flag:
                print("Go to phase 3")
                phase_cycles = 0
                phase = 3

                init_q = utils.q_vec(state)

        elif phase == 3:                                    
            dance_command = Command(                 
                # q = [0.05,  0.8, -1.8, -0.05,  0.8, -1.8, 0.05,  0.8, -1.4, -0.05,  0.8, -1.4],
                q = [0.05,  0.8, -1.4, -0.05,  0.8, -1.4, 0.2,  0.8, -1.4, 0.2,  0.8, -1.4],  
                # q = [0.05,  1.4, -0.9, -0.05,  1.4, -0.9, -0.7,  3.9, -2.75, -0.7,  3.9, -2.75],                
                Kp = [90]*12,
                Kd = [1]*12
            )
            
            q_step, flag = utils.interpolate(init_q, dance_command.q, phase_cycles, 100)                          

            command = dance_command.copy(q = q_step)
            conn.send(command)

            if flag:                         
                print("Go to phase 4")
                phase_cycles = 0                
                phase = 4   

                init_q = utils.q_vec(state)

        elif phase == 4:                        
            init_q = utils.q_vec(state)
            dance_command = Command(
                # q = [0.05,  0.8, -1.4, -0.05,  0.8, -1.4, 0.05,  0.8, -1.7, -0.05,  0.8, -1.7], 
                q = [0.05,  0.8, -1.4, -0.05,  0.8, -1.4, -0.2,  0.8, -1.4, -0.2,  0.8, -1.4],
                # q = [0.05,  1.2, -0.9, -0.05,  1.2, -1.4, 0.7,  3.9, -2.75, 0.7,  3.9, -2.75],
                Kp = [90]*12,
                Kd = [1]*12
            )
            q_step, flag = utils.interpolate(init_q, dance_command.q, phase_cycles, 100)            
            command = dance_command.copy(q = q_step)
            conn.send(command)

            if flag:            
                print("Go to phase 3")
                phase_cycles = 0
                phase = 3   

                init_q = utils.q_vec(state)    

        phase_cycles += 1
        time.sleep(0.01)

    return state

def main(args):
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

    _, command = dance_1(conn, viewer)

    while viewer is None or viewer.is_running():
        conn.send(command)

        time.sleep(0.01)  



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--real', action='store_true')
    parser.add_argument('-a', '--aliengo', action='store_true')    
    main(parser.parse_args())