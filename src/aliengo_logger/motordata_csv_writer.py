import csv

fieldnames = ["x_value", "tick", 
            "FL0_torque", "FR0_torque", "RL0_torque", "RR0_torque", 
            "FL1_torque", "FR1_torque", "RL1_torque", "RR1_torque", 
            "FL2_torque", "FR2_torque", "RL2_torque", "RR2_torque", 
            "FL0_pos", "FR0_pos", "RL0_pos", "RR0_pos", 
            "FL1_pos", "FR1_pos", "RL1_pos", "RR1_pos", 
            "FL2_pos", "FR2_pos", "RL2_pos", "RR2_pos"]

with open('motorstate.csv', 'w') as csv_file: #create new file when import
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()

def append_motor_state_to_csv(tick, torque, position, csvfilename = 'motorstate.csv'):
    ''' Appends new motorstate row in CSV file
    Args:
        tick (int): internal robot time in mils.
        torque (list of float): 12 motor torques (N*m): FR[0-2] FL[3-5] RR[6-8] RL[9-11].
        position (list of float): 12 motor positions (rad): FR[0-2] FL[3-5] RR[6-8] RL[9-11].

    Return:
        None: that function does not return any value. It appends a row in CSV file.
    '''

    with open(csvfilename, 'r') as f:
        x_value = (sum(1 for line in f)//2 -1)/5

    with open(csvfilename, 'a') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        torque_data = { #0-2FR 3-5FL 6-8RR 9-11RL
            "FR": [torque[0], torque[1], torque[2]],
            "FL": [torque[3], torque[4], torque[5]],
            "RR": [torque[6], torque[7], torque[8]],
            "RL": [torque[9], torque[10], torque[11]],
        }
        #print(torque_data["FL"][0])

        position_data = {
            "FR": [position[0], position[1], position[2]],
            "FL": [position[3], position[4], position[5]],
            "RR": [position[6], position[7], position[8]],
            "RL": [position[9], position[10], position[11]],
        }
        
        header = { #csv header
            "x_value": x_value,
            "tick": tick,
            "FL0_torque": torque_data["FL"][0], "FR0_torque": torque_data["FR"][0],"RL0_torque": torque_data["RL"][0], "RR0_torque": torque_data["RR"][0],
            "FL1_torque": torque_data["FL"][1], "FR1_torque": torque_data["FR"][1], "RL1_torque": torque_data["RL"][1], "RR1_torque": torque_data["RR"][1],
            "FL2_torque": torque_data["FL"][2], "FR2_torque": torque_data["FR"][2], "RL2_torque": torque_data["RL"][2], "RR2_torque": torque_data["RR"][2],
            "FL0_pos": position_data["FL"][0], "FR0_pos": position_data["FR"][0], "RL0_pos": position_data["RL"][0], "RR0_pos": position_data["RR"][0],
            "FL1_pos": position_data["FL"][1], "FR1_pos": position_data["FR"][1], "RL1_pos": position_data["RL"][1], "RR1_pos": position_data["RR"][1],
            "FL2_pos": position_data["FL"][2], "FR2_pos": position_data["FR"][2], "RL2_pos": position_data["RL"][2], "RR2_pos": position_data["RR"][2] 
        }

        csv_writer.writerow(header)

#csv_fill(0, [0]*12, [1]*12)