import sys
import time

sys.path.append('./submodules/unitree_legged_sdk/lib/python/amd64')
import robot_interface_aliengo as sdk

from src.robots.aliengo import ALIENGO_LOW_WIRED_DEFAULTS, LOWLEVEL, motors_aliengo_pos_range

class RealAlienGo():

    def __init__(self, settings=ALIENGO_LOW_WIRED_DEFAULTS):
        self.udp = sdk.UDP(*settings)
        
    def start(self):        
        self.cmd = sdk.LowCmd()
        self.state = sdk.LowState()
        self.udp.InitCmdData(self.cmd)
        self.cmd.levelFlag = LOWLEVEL           

    def check_motor_ranges(self) -> bool:        
        for no, motor_pos_range in enumerate(motors_aliengo_pos_range):
            q = self.cmd.motorCmd[no].q
            if q < motor_pos_range[1]:
                print(f'WARNING! Motor command {motor_pos_range[0]} ({no}) q = {q} < {motor_pos_range[1]}')
                # return False
            elif q > motor_pos_range[2]:
                print(f'WARNING! Motor command {motor_pos_range[0]} ({no}) q = {q} > {motor_pos_range[2]}')
                # return False
        return True

    def set_cmd(self, motor_state):
        for i in range(12):
            self.cmd.motorCmd[i].q = motor_state.q[i]
            self.cmd.motorCmd[i].dq = motor_state.dq[i]
            self.cmd.motorCmd[i].Kp = motor_state.Kp[i]
            self.cmd.motorCmd[i].Kd = motor_state.Kd[i]
            self.cmd.motorCmd[i].tau = motor_state.tau[i]    

    def send(self, motor_state):        
        self.set_cmd(motor_state)
        
        if self.check_motor_ranges():
            self.udp.SetSend( self.cmd )   
            self.udp.Send()

    def get_latest_state(self):
        state = sdk.LowState()
        self.udp.Recv()
        self.udp.GetRecv(state)
        return state

    def wait_latest_state(self):
        state = self.get_latest_state()
        while state is None:
            time.sleep(0.001)
            state = self.get_latest_state()
        return state
        