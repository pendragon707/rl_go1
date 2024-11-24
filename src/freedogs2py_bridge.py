from abc import ABC, abstractmethod
import typing
import time

from ucl.lowCmd import lowCmd
from ucl.lowState import lowState
from ucl.unitreeConnection import unitreeConnection, LOW_WIRED_DEFAULTS

import constants
import monitoring


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
        self.check_motor_ranges(cmd)
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
