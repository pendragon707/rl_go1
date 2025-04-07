import pandas as pd
import matplotlib.pyplot as plt
from itertools import count
from matplotlib.animation import FuncAnimation


import subprocess # for read file tail
import io

def read_last_n_lines_with_tail(filename, n=0, delimiter=','):
    """
    Return DataFrame with n last strings from file. Uses tail.

    Args:
        filename (str)
        n (int): number of tail strings
        delimiter (str): delimiter cols in CSV-file (',' by default).

    Returns:
        pandas.DataFrame: DataFrame with n string. If error or no file returns empty DataFrame.
    """
    try:
        # count number of strings in file
        process_count = subprocess.Popen(['wc', '-l', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE) #wc -l counts lines
        output_count, error_count = process_count.communicate()
        if error_count:
            print(f"Error with executind wc -l: {error_count.decode()}")
            return pd.read_csv(filename, delimiter=delimiter)  # try to read all file
        
        total_lines = int(output_count.decode().split()[0])  # extract the line count

        if n == 0 or n >= total_lines:
            # read all file
            return pd.read_csv(filename, delimiter=delimiter)
        process = subprocess.Popen(['tail', '-n', str(n), filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if error:
            print(f"Error with executing tail: {error.decode()}")
            return pd.DataFrame()  # empty DataFrame

        try: # read n-string tail file, need for correct work with header when we read part of table
            header = pd.read_csv(filename, delimiter=delimiter, nrows=0)  # read only header row
            data = pd.read_csv(io.StringIO(output.decode()), delimiter=delimiter, header=None, names=header.columns) # don't treat first line as header

            #data = pd.read_csv(io.StringIO(output.decode()), delimiter=delimiter)
            return data

        except pd.errors.EmptyDataError:
            print("Tail output is empty.")
            return pd.DataFrame()
    
    except FileNotFoundError:
        print(f"Not found file: {filename}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

def build_graph_from_csv(csvfilename = 'motorstate.csv', time_window = 0, mode = 'all'):
    '''
    Args: mode = 'all', 'torque', 'pos'.

    Return:
    '''
    index = count()

    fig, (ax0, ax1, ax2) = plt.subplots(nrows = 3, ncols= 2, sharex = True) #subplot init

    def animate(i):

        ax0[0].cla() #clear all axis
        ax0[1].cla()
        ax1[0].cla()
        ax1[1].cla()
        ax2[0].cla()
        ax2[1].cla()

        data = read_last_n_lines_with_tail('motorstate.csv', 700) # read only n strings (time window)
        #data = pd.read_csv('motorstate.csv') # read full file always
 
        data['relative_time'] = (data['tick'] - data['tick'].iloc[-1]) / 1000.0 #from absolute tick to relative time
        x = data['relative_time']

        #x = data['tick']
        #x = data['x_value']

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

    # TORQUE (COL 0)
        ax0[0].plot(x, torque_data['FL'][0], c = 'orange', label = 'FL')
        ax0[0].plot(x, torque_data['FR'][0], c = 'red', label = 'FR')
        ax0[0].plot(x, torque_data['RL'][0], c = 'blue', label = 'RL')
        ax0[0].plot(x, torque_data['RR'][0], c = 'black', label = 'RR')

        ax1[0].plot(x, torque_data['FL'][1], c = 'orange', label = 'FL')
        ax1[0].plot(x, torque_data['FR'][1], c = 'red', label = 'FR')
        ax1[0].plot(x, torque_data['RL'][1], c = 'blue', label = 'RL')
        ax1[0].plot(x, torque_data['RR'][1], c = 'black', label = 'RR')

        ax2[0].plot(x, torque_data['FL'][2], c = 'orange', label = 'FL')
        ax2[0].plot(x, torque_data['FR'][2], c = 'red', label = 'FR')
        ax2[0].plot(x, torque_data['RL'][2], c = 'blue', label = 'RL')
        ax2[0].plot(x, torque_data['RR'][2], c = 'black', label = 'RR')

    # POSITION (COL 1)
        ax0[1].plot(x, position_data['FL'][0], c = 'orange', label = 'FL')
        ax0[1].plot(x, position_data['FR'][0], c = 'red', label = 'FR')
        ax0[1].plot(x, position_data['RL'][0], c = 'blue', label = 'RL')
        ax0[1].plot(x, position_data['RR'][0], c = 'black', label = 'RR')

        ax1[1].plot(x, position_data['FL'][1], c = 'orange', label = 'FL')
        ax1[1].plot(x, position_data['FR'][1], c = 'red', label = 'FR')
        ax1[1].plot(x, position_data['RL'][1], c = 'blue', label = 'RL')
        ax1[1].plot(x, position_data['RR'][1], c = 'black', label = 'RR')

        ax2[1].plot(x, position_data['FL'][2], c = 'orange', label = 'FL')
        ax2[1].plot(x, position_data['FR'][2], c = 'red', label = 'FR')
        ax2[1].plot(x, position_data['RL'][2], c = 'blue', label = 'RL')
        ax2[1].plot(x, position_data['RR'][2], c = 'black', label = 'RR')
        
        #ax2.plot(x, y2, label='Channel 2')

        ax0[0].grid(True)
        ax1[0].grid(True)
        ax2[0].grid(True)

        ax0[0].set_title('Hip motor torque') #left graphs
        ax1[0].set_title('Arm motor')
        ax2[0].set_title('Knee motor')

        ax0[1].grid(True)
        ax1[1].grid(True)
        ax2[1].grid(True)

        ax0[1].set_title('Hip motor position') #right graphs
        ax1[1].set_title('Arm motor')
        ax2[1].set_title('Knee motor')

        # legend with motor definition
        ax0[0].legend(loc='upper left')    

    interval = 500 # mils, plot update period
    MAX_FRAMES = (60 * 1000 // interval) * 5 # = 5 min of plotting with cache
    ani = FuncAnimation(fig, animate, interval=interval, save_count=MAX_FRAMES) # save_count for cache limit

    plt.tight_layout()
    plt.show()

build_graph_from_csv()