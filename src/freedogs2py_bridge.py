from abc import ABC, abstractmethod
import time

from simulation import Simulation

from ucl.lowCmd import lowCmd
from ucl.lowState import lowState

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

    def send(self, cmd: lowCmd) -> None:
        # log
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
        