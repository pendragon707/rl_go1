import time

import os
import sys

print(os.getcwd())
sys.path.append(os.getcwd())

# from freedogs2py_bridge import RealGo1, RealAlienGo
from src.freedogs2py_bridge import RealGo1
from src import simulation
from src import config
from src import positions
from src import utils

sys.path.append('./submodules/unitree_legged_sdk/lib/python/amd64')
import robot_interface_aliengo as sdk


# TARGET_PORT = 8007
# LOCAL_PORT = 8082
# TARGET_IP = "192.168.123.10"   # target IP address
# LOW_CMD_LENGTH = 610
# LOW_STATE_LENGTH = 771

# ALIENGO_LOW_WIRED_DEFAULTS = (LOCAL_PORT, TARGET_IP, TARGET_PORT, LOW_CMD_LENGTH, LOW_STATE_LENGTH, -1) 

# HIGHLEVEL = 0x00
# LOWLEVEL  = 0xff


# from robots.aliengo.aliengo_consts import ALIENGO_LOW_WIRED_DEFAULTS, LOWLEVEL
from src.robots.aliengo import ALIENGO_LOW_WIRED_DEFAULTS, LOWLEVEL
from src.safety import Safety

class RealAlienGo():

    def __init__(self, settings=ALIENGO_LOW_WIRED_DEFAULTS, safe = True):
        self.udp = sdk.UDP(*settings)
        
        self.cmd = sdk.LowCmd()
        self.state = sdk.LowState()
        self.udp.InitCmdData(self.cmd)
        self.cmd.levelFlag = LOWLEVEL

        # self.safety = Safety()

    def start(self):        
        self.cmd = sdk.LowCmd()
        self.state = sdk.LowState()
        self.udp.InitCmdData(self.cmd)
        self.cmd.levelFlag = LOWLEVEL

    def check_motor_ranges(self):
        pass

    def set_cmd(self, motor_state):
        for i in range(12):
            self.cmd.motorCmd[i].q = motor_state.get_command(i)[0]
            self.cmd.motorCmd[i].dq = motor_state.get_command(i)[1]
            self.cmd.motorCmd[i].Kp = motor_state.get_command(i)[2]
            self.cmd.motorCmd[i].Kd = motor_state.get_command(i)[3]
            self.cmd.motorCmd[i].tau = motor_state.get_command(i)[4]

    def send(self):
        self.udp.SetSend( self.cmd )   
        self.udp.Send()

    def wait_latest_state(self):
        self.state = sdk.LowState()
        self.udp.Recv()
        return self.udp.GetRecv(self.state)





# def standup(cmd, conn, viewer = None, aliengo = True, udp = None):
def standup(conn : RealAlienGo, viewer = None, aliengo = True):
    phase = 0
    phase_cycles = 0

    stand_command = positions.stand_command_2()
    while viewer is None or viewer.is_running():        
        state = conn.wait_latest_state()
        print(state)

        """
        state = sdk.LowState()
        udp.Recv()
        udp.GetRecv(state)
        """        
        
        if phase == 0:
            if phase_cycles >= 100:
                phase = 1
                phase_cycles = 0

        elif phase == 1:
            if phase_cycles >= 100:
                phase = 2
                phase_cycles = 0
                init_q = utils.q_vec(state)

            if aliengo:      
                conn.set_cmd(positions.laydown_command())
                conn.send()

                """
                com = positions.laydown_command()

                for i in range(12):
                    self.cmd.motorCmd[i].q = com.get_command(i)[0]
                    self.cmd.motorCmd[i].dq = com.get_command(i)[1]
                    self.cmd.motorCmd[i].Kp = com.get_command(i)[2]
                    self.cmd.motorCmd[i].Kd = com.get_command(i)[3]
                    self.cmd.motorCmd[i].tau = com.get_command(i)[4]

                udp.SetSend( cmd )
                udp.Send()   
                """

            else:
                conn.send(positions.laydown_command().robot_cmd())

        elif phase == 2:            
            q_step, _ = utils.interpolate(init_q, stand_command.q, phase_cycles, 500)            
            command = stand_command.copy(q = q_step)
            if aliengo:                            
                conn.set_cmd(command)
                conn.send()

                """
                for i in range(12):
                    cmd.motorCmd[i].q = command.get_command(i)[0]
                    cmd.motorCmd[i].dq = command.get_command(i)[1]
                    cmd.motorCmd[i].Kp = command.get_command(i)[2]
                    cmd.motorCmd[i].Kd = command.get_command(i)[3]
                    cmd.motorCmd[i].tau = command.get_command(i)[4]

                udp.SetSend( cmd )
                udp.Send() 
                """

            else:
                """
                udp.SetSend( cmd )
                udp.Send() 
                """
                conn.send(command.robot_cmd())

            if phase_cycles == 500:
                return state, command       

        phase_cycles += 1
        time.sleep(0.01)

def main():
    config.ENABLE_SIMULATION = True

    real = True
    aliengo = True
    conn = None

    if not real:
        conn = simulation.Simulation(config)
        conn.set_keyframe(0)
        conn.start()
        viewer = conn.viewer
    elif aliengo:        
        conn = RealAlienGo()
        conn.start()

        """
        # udp = sdk.UDP(LOCAL_PORT, TARGET_IP, TARGET_PORT, LOW_CMD_LENGTH, LOW_STATE_LENGTH, -1)
        udp = sdk.UDP(*ALIENGO_LOW_WIRED_DEFAULTS)
        
        cmd = sdk.LowCmd()
        state = sdk.LowState()
        udp.InitCmdData(cmd)
        cmd.levelFlag = LOWLEVEL
        """

        viewer = None
    else:
        conn = RealGo1()
        conn.start()
        viewer = None

    time.sleep(0.2)

    # _, cmd = standup(conn, viewer, aliengo)
    # _, command = standup(cmd, conn, viewer, aliengo, udp)
    _, command = standup(conn, viewer, aliengo)

    while viewer is None or viewer.is_running():
        if aliengo:   
            conn.set_cmd( command )         
            conn.send( )
        else:
            conn.send(command.robot_cmd())

        time.sleep(0.01)  


if __name__ == '__main__':
    main()