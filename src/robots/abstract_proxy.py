from abc import ABC, abstractmethod
import typing
import time

import src.constants as constants
from src.monitoring import Monitoring


class RobotProxy(ABC):

    def __init__(self):
        self.monitoring = Monitoring()

    def check_motor_ranges(self, cmd):
        for no, motor_pos_range in enumerate(constants.motors_mujoco_pos_range):
            q = cmd.motorCmd.motor(no).q
            if q < motor_pos_range[1]:
                print(f'WARNING! Motor command {motor_pos_range[0]} ({no}) q = {q} < {motor_pos_range[1]}')
            elif q > motor_pos_range[2]:
                print(f'WARNING! Motor command {motor_pos_range[0]} ({no}) q = {q} > {motor_pos_range[2]}')

    def send(self, command) -> None:
        cmd = command.robot_cmd()
        self.check_motor_ranges(cmd)
        self.monitoring.send_cmd(time.time_ns(), cmd)
        self.send_impl(cmd)

    def get_latest_state(self):
        states = self.get_states_impl()
        if len(states) > 0:
            self.monitoring.send_states(states)
            return states[-1][1]
        else:
            return None
        
    def wait_latest_state(self):
        state = self.get_latest_state()
        while state is None:
            time.sleep(0.001)
            state = self.get_latest_state()
        return state

    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def send_impl(self, cmd) -> None:
        ...

    @abstractmethod
    def get_states_impl(self):
        ...