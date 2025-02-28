from abc import ABC, abstractmethod
import typing
import time

import sys

sys.path.append("./submodules/free-dog-sdk/")
from ucl.lowCmd import lowCmd
from ucl.lowState import lowState
from ucl.unitreeConnection import unitreeConnection, LOW_WIRED_DEFAULTS

sys.path.append('./submodules/unitree_legged_sdk/lib/python/amd64')
import robot_interface_aliengo as sdk

from src import constants
from src import monitoring


class RobotProxy(ABC):

    def __init__(self):
        self.monitoring = monitoring.Monitoring()

    def check_motor_ranges(self, cmd):
        for no, motor_pos_range in enumerate(constants.motors_mujoco_pos_range):
            q = cmd.motorCmd.motor(no).q
            if q < motor_pos_range[1]:
                print(f'WARNING! Motor command {motor_pos_range[0]} ({no}) q = {q} < {motor_pos_range[1]}')
            elif q > motor_pos_range[2]:
                print(f'WARNING! Motor command {motor_pos_range[0]} ({no}) q = {q} > {motor_pos_range[2]}')

    def send(self, cmd: lowCmd) -> None:
        # self.check_motor_ranges(cmd)
        self.monitoring.send_cmd(time.time_ns(), cmd)
        self.send_impl(cmd)

    def get_latest_state(self) -> lowState:
        states = self.get_states_impl()
        if len(states) > 0:
            self.monitoring.send_states(states)
            return states[-1][1]
        else:
            return None
        
    def wait_latest_state(self) -> lowState:
        state = self.get_latest_state()
        while state is None:
            time.sleep(0.001)
            state = self.get_latest_state()
        return state

    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def send_impl(self, cmd: lowCmd) -> None:
        ...

    @abstractmethod
    def get_states_impl(self) -> list[typing.Tuple[int, lowState]]:
        ...


class RealGo1(RobotProxy):
    def __init__(self, settings=LOW_WIRED_DEFAULTS):
        super().__init__()
        self.conn = unitreeConnection(settings)

    def start(self):
        self.conn.startRecv()

        lcmd = lowCmd()
        cmd_bytes = lcmd.buildCmd(debug=False)
        self.conn.send(cmd_bytes)

    def send_impl(self, cmd: lowCmd) -> None:
        self.conn.send(cmd.buildCmd(debug=False))

    def get_states_impl(self) -> list[typing.Tuple[int, lowState]]:
        rslt = []
        for ts, packet in self.conn.getTimedData():
            state = lowState()
            assert state.parseData(packet)
            rslt.append((ts, state))
        return rslt


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
        self.conn = sdk.UDP(*settings)

        # if safe:
        #     self.safe = sdk.Safety(sdk.LeggedType.Aliengo)

    # def check_motor_ranges(self, cmd):
    #     for no, motor_pos_range in enumerate(constants.motors_mujoco_pos_range):
    #         q = cmd.motorCmd[no].q
    #         if q < motor_pos_range[1]:
    #             print(f'WARNING! Motor command {motor_pos_range[0]} ({no}) q = {q} < {motor_pos_range[1]}')
    #         elif q > motor_pos_range[2]:
    #             print(f'WARNING! Motor command {motor_pos_range[0]} ({no}) q = {q} > {motor_pos_range[2]}')

    def start(self, level = LOWLEVEL):
        self.cmd = sdk.LowCmd()        
        self.conn.InitCmdData(self.cmd)
        self.cmd.levelFlag = level 

    def set_cmd(self, cmd):
        self.cmd = cmd

    def send(self, cmd) -> None:
        # self.check_motor_ranges(cmd)        
        # self.monitoring.send_cmd(time.time_ns(), cmd)

        # print(cmd.bandWidth)
        # print(cmd.motorCmd[0].q)

        self.send_impl(self.cmd)

    def send_impl(self, cmd) -> None:       
        self.conn.SetSend(self.cmd)
        self.conn.Send()        
        

    def get_states_impl(self):    
        rslt = []

        state = sdk.LowState()
        self.conn.Recv()
        self.conn.GetRecv(state)

        # to do: add parse_data for state.motorState and assert
        
        rslt.append((time.time_ns(), state))  # optional to do: get time another way, patch for sdk?
        return rslt
