
import random
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

#plt.style.use('fivethirtyeight')

x_vals = []
y_vals = []

index = count()

fig, (ax0, ax1, ax2) = plt.subplots(nrows = 3, ncols= 1, sharex = True)



def animate(i):
    data = pd.read_csv('motorstate.csv')
    x = data['x_value']
    fl_0t = data['FL0_torque']
    fr_0t = data['FR0_torque']
    rl_0t = data['RL0_torque']
    rr_0t = data['RR0_torque']
    fl_1t = data['FL1_torque']
    fr_1t = data['FR1_torque']
    rl_1t = data['RL1_torque']
    rr_1t = data['RR1_torque']
    fl_2t = data['FL2_torque']
    fr_2t = data['FR2_torque']
    rl_2t = data['RL2_torque']
    rr_2t = data['RR2_torque']
    #y2 = data['total_2']

    #fig.clf()

    #====
    #fig, (ax0, ax1, ax2) = plt.subplots(nrows = 3, ncols= 1, sharex = True)
    #====
    ax0.plot(x, fl_0t, c = 'red', label = 'FL')
    ax0.plot(x, fr_0t, c = 'green', label = 'FR')
    ax0.plot(x, rl_0t, c = 'blue', label = 'RL')
    ax0.plot(x, rr_0t, c = 'black', label = 'RR')

    ax1.plot(x, fl_1t, c = 'red', label = 'FL')
    ax1.plot(x, fr_1t, c = 'green', label = 'FR')
    ax1.plot(x, rl_1t, c = 'blue', label = 'RL')
    ax1.plot(x, rr_1t, c = 'black', label = 'RR')

    ax2.plot(x, fl_2t, c = 'red', label = 'FL')
    ax2.plot(x, fr_2t, c = 'green', label = 'FR')
    ax2.plot(x, rl_2t, c = 'blue', label = 'RL')
    ax2.plot(x, rr_2t, c = 'black', label = 'RR')
    
    #ax2.plot(x, y2, label='Channel 2')

    ax0.grid(True)
    ax1.grid(True)
    ax2.grid(True)

    ax0.set_title('Hip motor')
    ax1.set_title('Arm motor')
    ax2.set_title('Knee motor')

    #ax1.legend(loc='upper left')    


ani = FuncAnimation(fig, animate, interval=500)

plt.tight_layout()
plt.show()