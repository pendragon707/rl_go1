import typing

import sys
# sys.path.append("../../submodules/free-dog-sdk/")
sys.path.append("./submodules/free-dog-sdk/")
from ucl.lowCmd import lowCmd
from ucl.lowState import lowState
from ucl.unitreeConnection import unitreeConnection, LOW_WIRED_DEFAULTS

import sys
sys.path.append("./src/robots")
from src.robots.abstract_proxy import RobotProxy

from src.robots.go import motors_pos_range

class RealGo1(RobotProxy):
    def __init__(self, settings=LOW_WIRED_DEFAULTS):
        super().__init__()
        self.conn = unitreeConnection(settings)

    def check_motor_ranges(self, cmd):
        for no, motor_pos_range in enumerate(motors_pos_range):
            q = cmd.motorCmd.motor(no).q
            if q < motor_pos_range[1]:
                print(f'WARNING! Motor command {motor_pos_range[0]} ({no}) q = {q} < {motor_pos_range[1]}')
            elif q > motor_pos_range[2]:
                print(f'WARNING! Motor command {motor_pos_range[0]} ({no}) q = {q} > {motor_pos_range[2]}')

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