import sys
# sys.path.append('../../submodules/unitree_legged_sdk/lib/python/amd64')
sys.path.append('./submodules/unitree_legged_sdk/lib/python/amd64')
import robot_interface_aliengo as sdk

from aliengo.aliengo_consts import ALIENGO_LOW_WIRED_DEFAULTS, LOWLEVEL
from safety import Safety

class RealAlienGo():

    def __init__(self, settings=ALIENGO_LOW_WIRED_DEFAULTS, safe = True):
        self.udp = sdk.UDP(*settings)
        
        self.cmd = sdk.LowCmd()
        self.state = sdk.LowState()
        self.udp.InitCmdData(self.cmd)
        self.cmd.levelFlag = LOWLEVEL

        self.safety = Safety()
        
    def start(self):        
        # self.cmd = sdk.LowCmd()
        # self.state = sdk.LowState()
        # self.udp.InitCmdData(self.cmd)
        # self.cmd.levelFlag = LOWLEVEL
    
        pass

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

    # def recv(self):
    #     # state = sdk.LowState()
    #     self.udp.Recv()
    #     # self.udp.GetRecv(state)

    def wait_latest_state(self):
        self.udp.Recv()
        return self.udp.GetRecv(self.state)