import socket
import cbor2
import constants


class Monitoring:
    def __init__(self, host='127.0.0.1', port=9870):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port

    def motors_state_dict(self, motorsState):
        rslt = {}
        for no, motorState in enumerate(motorsState[:12]):
            rslt[constants.motors_names[no]] = {
                'q': motorState.q,
                'dq': motorState.dq
            }

        return rslt
    
    def motors_cmd_dict(self, motorCmd):
        rslt = {}
        for no, motor_name in enumerate(constants.motors_names):
            rslt[motor_name] = {
                'q': motorCmd.motor(no).q,
                'dq': motorCmd.motor(no).dq,
                'Kp': motorCmd.motor(no).Kp,
                'Kd': motorCmd.motor(no).Kd,
            }

        return rslt

    def send_states(self, states):
        if len(states) == 0:
            return

        for state in states:
            data = {
                'timestamp': state[0],
                'state': {
                    'motors': self.motors_state_dict(state[1].motorState)
                }
            }
        
        self.sock.sendto(cbor2.dumps(data), (self.host, self.port))
    
    def send_cmd(self, timestamp, cmd):
        data = {
            'timestamp': timestamp,
            'command': {
                'motors': self.motors_cmd_dict(cmd.motorCmd)
            }
        }
    

        self.sock.sendto(cbor2.dumps(data), (self.host, self.port))
