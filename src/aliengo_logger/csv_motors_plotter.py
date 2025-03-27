from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

#plt.style.use('fivethirtyeight')

x_vals = []
y_vals = []

index = count()

fig, (ax0, ax1, ax2) = plt.subplots(nrows = 3, ncols= 2, sharex = True)



def animate(i):
    data = pd.read_csv('motorstate.csv')
    x = data['x_value']

    torque_data = {
        "FR": [data['FR0_torque'].tolist(), data['FR1_torque'].tolist(), data['FR2_torque'].tolist()],
        "FL": [data['FL0_torque'].tolist(), data['FL1_torque'].tolist(), data['FL2_torque'].tolist()],
        "RR": [data['RR0_torque'].tolist(), data['RR1_torque'].tolist(), data['RR2_torque'].tolist()],
        "RL": [data['RL0_torque'].tolist(), data['RL1_torque'].tolist(), data['RL2_torque'].tolist()],
    }

    position_data = {
        "FR": [data['FR0_pos'].tolist(), data['FR1_pos'].tolist(), data['FR2_pos'].tolist()],
        "FL": [data['FL0_pos'].tolist(), data['FL1_pos'].tolist(), data['FL2_pos'].tolist()],
        "RR": [data['RR0_pos'].tolist(), data['RR1_pos'].tolist(), data['RR2_pos'].tolist()],
        "RL": [data['RL0_pos'].tolist(), data['RL1_pos'].tolist(), data['RL2_pos'].tolist()],
    }

    # TORQUE (COL 1)
    ax0[0].plot(x, torque_data['FL'][0], c = 'red', label = 'FL')
    ax0[0].plot(x, torque_data['FR'][0], c = 'green', label = 'FR')
    ax0[0].plot(x, torque_data['RL'][0], c = 'blue', label = 'RL')
    ax0[0].plot(x, torque_data['RR'][0], c = 'black', label = 'RR')

    ax1[0].plot(x, torque_data['FL'][1], c = 'red', label = 'FL')
    ax1[0].plot(x, torque_data['FR'][1], c = 'green', label = 'FR')
    ax1[0].plot(x, torque_data['RL'][1], c = 'blue', label = 'RL')
    ax1[0].plot(x, torque_data['RR'][1], c = 'black', label = 'RR')

    ax2[0].plot(x, torque_data['FL'][2], c = 'red', label = 'FL')
    ax2[0].plot(x, torque_data['FR'][2], c = 'green', label = 'FR')
    ax2[0].plot(x, torque_data['RL'][2], c = 'blue', label = 'RL')
    ax2[0].plot(x, torque_data['RR'][2], c = 'black', label = 'RR')

   # POSITION (COL 1)
    ax0[1].plot(x, position_data['FL'][0], c = 'red', label = 'FL')
    ax0[1].plot(x, position_data['FR'][0], c = 'green', label = 'FR')
    ax0[1].plot(x, position_data['RL'][0], c = 'blue', label = 'RL')
    ax0[1].plot(x, position_data['RR'][0], c = 'black', label = 'RR')

    ax1[1].plot(x, position_data['FL'][1], c = 'red', label = 'FL')
    ax1[1].plot(x, position_data['FR'][1], c = 'green', label = 'FR')
    ax1[1].plot(x, position_data['RL'][1], c = 'blue', label = 'RL')
    ax1[1].plot(x, position_data['RR'][1], c = 'black', label = 'RR')

    ax2[1].plot(x, position_data['FL'][2], c = 'red', label = 'FL')
    ax2[1].plot(x, position_data['FR'][2], c = 'green', label = 'FR')
    ax2[1].plot(x, position_data['RL'][2], c = 'blue', label = 'RL')
    ax2[1].plot(x, position_data['RR'][2], c = 'black', label = 'RR')
    
    #ax2.plot(x, y2, label='Channel 2')

    ax0[0].grid(True)
    ax1[0].grid(True)
    ax2[0].grid(True)

    ax0[0].set_title('Hip motor')
    ax1[0].set_title('Arm motor')
    ax2[0].set_title('Knee motor')

    #ax1.legend(loc='upper left')    

ani = FuncAnimation(fig, animate, interval=1000)

plt.tight_layout()
plt.show()