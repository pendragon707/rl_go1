import typing
import time
import sys

sys.path.append('./submodules/unitree_legged_sdk/lib/python/amd64')
import robot_interface_aliengo as sdk

# to do: move to _config_ or to unitree_legged_sdk 
TARGET_PORT = 8007
LOCAL_PORT = 8082
TARGET_IP = "192.168.123.10"   # target IP address
LOW_CMD_LENGTH = 610
LOW_STATE_LENGTH = 771

ALIENGO_LOW_WIRED_DEFAULTS = (LOCAL_PORT, TARGET_IP, TARGET_PORT, LOW_CMD_LENGTH, LOW_STATE_LENGTH, -1) 

# to do: move this values to unitree_legged_sdk 
HIGHLEVEL = 0x00
LOWLEVEL  = 0xff

class RealAlienGo(RobotProxy):
    def __init__(self, settings=ALIENGO_LOW_WIRED_DEFAULTS, safe = True):
        super().__init__()        
        self.conn = sdk.UDP(settings)

        # if safe:
        #     self.safe = sdk.Safety(sdk.LeggedType.Aliengo)

    def start(self, level = LOWLEVEL):
        self.cmd = sdk.LowCmd()
        state = sdk.LowState()
        self.conn.InitCmdData(self.cmd)
        self.cmd.levelFlag = level

    def send_impl(self, cmd) -> None:        
        self.conn.SetSend(cmd)
        self.conn.Send()

    def get_states_impl(self):    
        rslt = []

        state = sdk.LowState()
        self.conn.Recv()
        self.conn.GetRecv(state)

        # to do: add parse_data for state.motorState and assert
        
        rslt.append((time.time_ns(), state))  # optional to do: get time another way, patch for sdk?
        return rslt