
import csv
import random
import time

fieldnames = ["x_value", 
            "FL0_torque", "FR0_torque", "RL0_torque", "RR0_torque", 
            "FL1_torque", "FR1_torque", "RL1_torque", "RR1_torque", 
            "FL2_torque", "FR2_torque", "RL2_torque", "RR2_torque", 
            "FL0_pos", "FR0_pos", "RL0_pos", "RR0_pos", 
            "FL1_pos", "FR1_pos", "RL1_pos", "RR1_pos", 
            "FL2_pos", "FR2_pos", "RL2_pos", "RR2_pos"]

# maybe this should be outside func
with open('motorstate.csv', 'w') as csv_file: #w - clear/create file and write
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()

def csv_fill(torque: list, position: list, x_value = 0): #add 1row data in motorstate.csv
    #this func must be in mainprog while True

    #x_value = 0
    FL0_torque = 0
    FR0_torque, RL0_torque, RR0_torque = 0, 0, 0
    FL1_torque, FR1_torque, RL1_torque, RR1_torque = 0, 0, 0, 0
    FL2_torque, FR2_torque, RL2_torque, RR2_torque = 0, 0, 0, 0
    FL0_pos, FR0_pos, RL0_pos, RR0_pos = 0, 0, 0, 0
    FL1_pos, FR1_pos, RL1_pos, RR1_pos = 0, 0, 0, 0
    FL2_pos, FR2_pos, RL2_pos, RR2_pos = 0, 0, 0, 0

    # fieldnames = ["x_value", 
    #             "FL0_torque", "FR0_torque", "RL0_torque", "RR0_torque", 
    #             "FL1_torque", "FR1_torque", "RL1_torque", "RR1_torque", 
    #             "FL2_torque", "FR2_torque", "RL2_torque", "RR2_torque", 
    #             "FL0_pos", "FR0_pos", "RL0_pos", "RR0_pos", 
    #             "FL1_pos", "FR1_pos", "RL1_pos", "RR1_pos", 
    #             "FL2_pos", "FR2_pos", "RL2_pos", "RR2_pos"]

    with open('motorstate.csv', 'a') as csv_file: #a - write data in tail
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        #x_value += 1
        #0-2FR 3-5FL 6-8RR 9-11RL
        print(torque[3])
        FL0_torque = torque[3]
        FR0_torque = torque[0]
        RL0_torque = torque[9]
        RR0_torque = torque[6]
        FL1_torque = torque[4]
        FR1_torque = torque[1]
        RL1_torque = torque[7]
        RR1_torque = torque[10]
        FL2_torque = torque[5]
        FR2_torque = torque[2]
        RL2_torque = torque[11]
        RR2_torque = torque[8]
        
        FL0_pos = position[3]
        FR0_pos = position[0]
        RL0_pos = position[9]
        RR0_pos = position[6]
        FL1_pos = position[4]
        FR1_pos = position[1]
        RL1_pos = position[7]
        RR1_pos = position[10]
        FL2_pos = position[5]
        FR2_pos = position[2]
        RL2_pos = position[11]
        RR2_pos = position[8]

        info = {
            "x_value": x_value,
            "FL0_torque": FL0_torque,
            "FR0_torque": FR0_torque,
            "RL0_torque": RL0_torque,
            "RR0_torque": RR0_torque,
            "FL1_torque": FL1_torque,
            "FR1_torque": FR1_torque,
            "RL1_torque": RL1_torque,
            "RR1_torque": RR1_torque,
            "FL2_torque": FL2_torque,
            "FR2_torque": FR2_torque,
            "RL2_torque": RL2_torque,
            "RR2_torque": RR2_torque,
            "FL0_pos": FL0_pos,
            "FR0_pos": FR0_pos,
            "RL0_pos": RL0_pos,
            "RR0_pos": RR0_pos,
            "FL1_pos": FL1_pos,
            "FR1_pos": FR1_pos,
            "RL1_pos": RL1_pos,
            "RR1_pos": RR1_pos,
            "FL2_pos": FL2_pos,
            "FR2_pos": FR2_pos,
            "RL2_pos": RL2_pos,
            "RR2_pos": RR2_pos
        }

        csv_writer.writerow(info)
        print(x_value, FL0_torque, FL0_pos) 

        # x_value += 1
        # #0-2FR 3-5FL 6-8RR 9-11RL
        # print(torque[3])
        # FL0_torque = torque[3]
        # FR0_torque = torque[0]
        # RL0_torque = torque[9]
        # RR0_torque = torque[6]
        # FL1_torque = torque[4]
        # FR1_torque = torque[1]
        # RL1_torque = torque[7]
        # RR1_torque = torque[10]
        # FL2_torque = torque[5]
        # FR2_torque = torque[2]
        # RL2_torque = torque[11]
        # RR2_torque = torque[8]
        
        # FL0_pos = position[3]
        # FR0_pos = position[0]
        # RL0_pos = position[9]
        # RR0_pos = position[6]
        # FL1_pos = position[4]
        # FR1_pos = position[1]
        # RL1_pos = position[7]
        # RR1_pos = position[10]
        # FL2_pos = position[5]
        # FR2_pos = position[2]
        # RL2_pos = position[11]
        # RR2_pos = position[8]

#csv_fill([0]*12, [1]*12)