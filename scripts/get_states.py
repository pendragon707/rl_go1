import time
import argparse

import os
import sys
print(os.getcwd())
sys.path.append(os.getcwd())

import src.config as config

from src.robots import RealAlienGo, RealGo1
from src.robots.simulation.simulation import Simulation


motor_names = ['FR_0', 'FR_1', 'FR_2',
               'FL_0', 'FL_1', 'FL_2', 
               'RR_0', 'RR_1', 'RR_2', 
               'RL_0', 'RL_1', 'RL_2']

def main(args):
    config.ENABLE_SIMULATION = True



    if not args.real:
        pass
        # conn = Simulation(config)
        # conn.set_keyframe(0)
        # conn.start()
        
        # viewer = conn.viewer
    elif args.aliengo:        
        conn = RealAlienGo()
        conn.start()

        viewer = None
    else:
        conn = RealGo1()
        conn.start()
        viewer = None    

    time.sleep(0.2)

    while True:
        state = conn.wait_latest_state()

        [print(name, state.motorState[num].q, state.motorState[num].tauEst) for num, name in enumerate(motor_names)]

        time.sleep(100)  


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--real', action='store_true')
    parser.add_argument('-a', '--aliengo', action='store_true')    
    main(parser.parse_args())