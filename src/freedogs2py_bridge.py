from abc import ABC, abstractmethod
import time

from simulation import Simulation

from ucl.lowCmd import lowCmd
from ucl.lowState import lowState

import constants
import monitoring


class RobotProxy(ABC):
    @abstractmethod
    def send(self, cmd: lowCmd) -> None:
        ...
    
    @abstractmethod
    def get_latest_state(self) -> lowState:
        ...

    

class MujocoConnectionProxy(RobotProxy):
    def __init__(self, simulation: Simulation):
        self.simulation = simulation
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
        self.simulation.set_cmd(cmd)

    def get_latest_state(self) -> lowState:
        states = self.simulation.get_states()
        self.monitoring.send_states(states)

        if len(states) > 0:
            return states[-1][1]
        else:
            return None
        # log
        # monitor
    