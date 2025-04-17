#!/usr/bin/python

import sys
import time
import math

#from motor_data_csv_writer import csv_fill # fill motorstate.csv
#from plotter_func import build_graph_from_csv

sys.path.append('../lib/python/amd64')
import robot_interface_aliengo as sdk

TARGET_PORT = 8007
LOCAL_PORT = 8082
TARGET_IP = "192.168.123.10"   # target IP address

LOW_CMD_LENGTH = 610
LOW_STATE_LENGTH = 771

def jointLinearInterpolation(initPos, targetPos, rate):

    #rate = np.fmin(np.fmax(rate, 0.0), 1.0)
    if rate > 1.0:
        rate = 1.0
    elif rate < 0.0:
        rate = 0.0

    p = initPos*(1-rate) + targetPos*rate
    return p

def setup_motor(cmd, num_motor, q, dq, Kp, Kd, tau):
    cmd.motorCmd[num_motor].q = q
    cmd.motorCmd[num_motor].dq = dq
    cmd.motorCmd[num_motor].Kp = Kp
    cmd.motorCmd[num_motor].Kd = Kd
    cmd.motorCmd[num_motor].tau = tau

def setup_feet(cmd, lists_motors):
    assert all(len(lists_motors[0]) == len(l) for l in lists_motors[1:]), "not valid motor data"

    for motor in lists_motors:
        setup_motor(cmd, motor[0], motor[1], motor[2], motor[3], motor[4], motor[5] )

if __name__ == '__main__':

    from motor_data_csv_writer import csv_fill # fill motorstate.csv

    d = {'FR_0':0, 'FR_1':1, 'FR_2':2,
         'FL_0':3, 'FL_1':4, 'FL_2':5, 
         'RR_0':6, 'RR_1':7, 'RR_2':8, 
         'RL_0':9, 'RL_1':10, 'RL_2':11 }

         
    PosStopF  = math.pow(10,9)
    VelStopF  = 16000.0
    HIGHLEVEL = 0x00
    LOWLEVEL  = 0xff
    start_q = [-0.15, 1.18, -2.8] * 4
    end_q = [0.0, 0.3, -1.5, 0.0, 1, -1.5] #[0.0, 0.3, -1, 0.0, 1, -1]
    dt = 0.002
    qInit = [0] * 12
    qDes = [0] * 12
    sin_count = 0
    rate_count = 0
    Kp = [0] * 12
    Kd = [0] * 12

    udp = sdk.UDP(LOCAL_PORT, TARGET_IP, TARGET_PORT, LOW_CMD_LENGTH, LOW_STATE_LENGTH, -1)
    #udp = sdk.UDP(8082, "192.168.123.10", 8007, 610, 771)
    safe = sdk.Safety(sdk.LeggedType.Aliengo)
    
    cmd = sdk.LowCmd()
    state = sdk.LowState()
    udp.InitCmdData(cmd)
    cmd.levelFlag = LOWLEVEL

    count = 0
    count2 = 0
    Tpi = 0
    motiontime = 0

    while True:
        time.sleep(0.002)
        motiontime += 1
        
        udp.Recv()
        udp.GetRecv(state)
        
        if( motiontime >= 0):            
            if( motiontime >= 0 and motiontime < 10):

                for num, value in enumerate(d.values()):
                    qInit[num] = state.motorState[value].q

                print("Front: ", qInit[0], qInit[1], qInit[2])
                print("Rear: ", qInit[6], qInit[7], qInit[8])
            
            if( motiontime >= 10 and motiontime < 400):
                rate_count += 1
                rate = rate_count/200.0                      
                
                Kp = [90] * 12
                Kd = [1] * 12

                for num, value in enumerate(d.values()):
                    qDes[num] = jointLinearInterpolation(qInit[num], start_q[num], rate)
                                                        
            if(motiontime >= 400):                    
                alpha = min(count /  1000, 1)
                alpha2 = min(count2 / 1000, 1)
                if motiontime <= 2500:
                    
                    for i in range( 0, len(d) - 6 , 3):
                        qDes[i] = start_q[0]
                        qDes[i + 1] =  alpha * end_q[1] + (1-alpha) * start_q[1]
                        qDes[i + 2] = alpha * end_q[2] + (1-alpha) * start_q[2]
                        qDes[i + 6] = start_q[0]
                        qDes[i + 7] =  alpha * end_q[4] + (1-alpha) * start_q[1]
                        qDes[i + 8] = alpha * end_q[5] + (1-alpha) * start_q[2]
                    count += 1
                else:
                    for i in range( 0, len(d) - 6 , 3):
                        qDes[i] = start_q[0]
                        qDes[i + 1] =  (1-alpha2) * end_q[1] + alpha2 * start_q[1]
                        qDes[i + 2] = (1-alpha2) * end_q[2] + alpha2 * start_q[2]
                        qDes[i + 6] = start_q[0]
                        qDes[i + 7] =  (1-alpha2) * end_q[4] + alpha2 * start_q[1]
                        qDes[i + 8] = (1-alpha2) * end_q[5] + alpha2 * start_q[2]
                    count2 += 1

            for i in range( 0, len(d) ):
                setup_motor(cmd, i, qDes[i], 0, Kp[i], Kd[i], 0.0)
            
            if motiontime % 10 == 0:                
                print("Torque :   ", end = "")
                for num, value in enumerate(d.values()):
                    print(int(state.motorState[ value ].tauEst * 100), end = " ")
        # logger
        tick = state.tick
        torque_vector_real = [state.motorState[i].tauEst for i in range(12)]
        position_vector_real = [state.motorState[i].q for i in range(12)]

        if motiontime % 10 == 0: #0.02
            csv_fill(tick, torque_vector_real, position_vector_real)

                                    
        if(motiontime > 10):
             safe.PowerProtect(cmd, state, 1)

        udp.SetSend(cmd)
        udp.Send()
