from abc import ABC, abstractmethod
import time

from simulation import Simulation

from ucl.lowCmd import lowCmd
from ucl.lowState import lowState


class RobotProxy(ABC):
    @abstractmethod
    def send(self, cmd: lowCmd) -> None:
        ...
    
    @abstractmethod
    def get_latest_state(self) -> lowState:
        ...

    

class MujocoConnectionProxy(RobotProxy):
    def __init__(self, simulation: Simulation, monitoring = None, logger = None):
        self.simulation = simulation

    def send(self, cmd: lowCmd) -> None:
        # log
        # monitor
        self.simulation.set_cmd(cmd)

    def get_latest_state(self) -> lowState:
        states = self.simulation.get_states()
        if len(states) > 0:
            return states[-1][1]
        else:
            return None
        # log
        # monitor
        