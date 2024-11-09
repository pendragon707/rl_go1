from abc import ABC, abstractmethod
import typing
import time

from ucl.lowCmd import lowCmd
from ucl.lowState import lowState

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

    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def send_impl(self, cmd: lowCmd) -> None:
        ...
    
    @abstractmethod
    def get_states_impl(self) -> list[typing.Tuple[int, lowState]]:
        ...
