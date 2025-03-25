import sys
import time
import math
#from mstate_func import csv_fill # fill motorstate.csv
from motors_data_logger import csv_fill # fill motorstate.csv
import random

if __name__ == '__main__':

    d = {'FR_0':0, 'FR_1':1, 'FR_2':2,
         'FL_0':3, 'FL_1':4, 'FL_2':5, 
         'RR_0':6, 'RR_1':7, 'RR_2':8, 
         'RL_0':9, 'RL_1':10, 'RL_2':11 }

    dt = 0.002

    position = [0] * 12
    torque = [0] * 12
    motiontime = 0
    x_value = 0

    while True:
        
        time.sleep(0.002)
        motiontime += 1    
        if motiontime % 10 == 0:
            for i in range(len(position)):
                position[i] = random.randint(-4, 4)
            for i in range(len(torque)):
                torque[i] = random.randint(-14, 14)
    
        csv_fill(torque, position)
        print('\n==time', motiontime*50)
            
