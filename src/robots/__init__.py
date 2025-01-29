from aliengo.aliengo_proxy import RealAlienGo
from go.go_proxy import RealGo1
from simulation.simulation import Simulation

from abstract_proxy import RobotProxy

from aliengo.aliengo_consts import ALIENGO_LOW_WIRED_DEFAULTS, LOWLEVEL
import go.go_constants
import simulation.simulation

robot_proxy = [RealGo1, RealAlienGo, Simulation]