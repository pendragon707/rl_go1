import time
from freedogs2py_bridge import RealGo1, RealAlienGo
import simulation

import config
import positions
import utils

import sys
sys.path.append('./submodules/unitree_legged_sdk/lib/python/amd64')
import robot_interface_aliengo as sdk

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

def standup(cmd, conn, viewer = None, aliengo = True, udp = None):
    phase = 0
    phase_cycles = 0

    stand_command = positions.stand_command_2()
    while viewer is None or viewer.is_running():
        # state = conn.wait_latest_state()

        state = sdk.LowState()
        udp.Recv()
        udp.GetRecv(state)
                
        # for i in range(12):        
        #     print(state.motorState[ i ].q, end = " ") 
        
        if phase == 0:
            if phase_cycles >= 100:
                phase = 1
                phase_cycles = 0
        elif phase == 1:
            if phase_cycles >= 100:
                phase = 2
                phase_cycles = 0
                init_q = utils.q_vec(state)
            if aliengo:     
                # conn.set_cmd( positions.laydown_command().aliengo_cmd() )
                # conn.send( positions.laydown_command().aliengo_cmd() )

                print("fasa 1")

                com = positions.laydown_command()

                for i in range(12):
                    cmd.motorCmd[i].q = com.get_command(i)[0]
                    cmd.motorCmd[i].dq = com.get_command(i)[1]
                    cmd.motorCmd[i].Kp = com.get_command(i)[2]
                    cmd.motorCmd[i].Kd = com.get_command(i)[3]
                    cmd.motorCmd[i].tau = com.get_command(i)[4]

                udp.SetSend( cmd )
                udp.Send()                                
            else:
                conn.send(positions.laydown_command().robot_cmd())
        elif phase == 2:
            print("fasa 2")

            q_step = utils.interpolate(init_q, stand_command.q, phase_cycles, 500)            
            command = stand_command.copy(q = q_step)
            if aliengo:   
                # print( cmd.aliengo_cmd() )             
                # conn.send(cmd.aliengo_cmd())

                # conn.set_cmd( cmd.aliengo_cmd() )
                # conn.send( cmd.aliengo_cmd() )

                for i in range(12):
                    cmd.motorCmd[i].q = command.get_command(i)[0]
                    cmd.motorCmd[i].dq = command.get_command(i)[1]
                    cmd.motorCmd[i].Kp = command.get_command(i)[2]
                    cmd.motorCmd[i].Kd = command.get_command(i)[3]
                    cmd.motorCmd[i].tau = command.get_command(i)[4]

                udp.SetSend( cmd )
                udp.Send() 

            else:
                udp.SetSend( cmd )
                udp.Send() 

                # conn.send(cmd.robot_cmd())

            if phase_cycles == 500:
                return state, cmd        

        phase_cycles += 1
        time.sleep(0.01)

def main():
    config.ENABLE_SIMULATION = True

    real = True
    aliengo = True
    conn = None

    if not real:
        conn = simulation.Simulation(config)
        conn.set_keyframe(0)
        conn.start()
        viewer = conn.viewer
    elif aliengo:        
        # conn = RealAlienGo()
        # conn.start()

        udp = sdk.UDP(LOCAL_PORT, TARGET_IP, TARGET_PORT, LOW_CMD_LENGTH, LOW_STATE_LENGTH, -1)
        
        cmd = sdk.LowCmd()
        state = sdk.LowState()
        udp.InitCmdData(cmd)
        cmd.levelFlag = LOWLEVEL

        viewer = None
    else:
        # TARGET_PORT = 8007
        # LOCAL_PORT = 8082
        # TARGET_IP = "192.168.123.10"   # target IP address
        # LOW_CMD_LENGTH = 610
        # LOW_STATE_LENGTH = 771
        # LOCAL_IP = "192.168.123.200" 

        # TEMP = (LOCAL_PORT, TARGET_IP, TARGET_PORT, LOCAL_IP)

        # conn = RealGo1(TEMP)
        conn = RealGo1()
        conn.start()
        viewer = None

    time.sleep(0.2)

    # _, cmd = standup(conn, viewer, aliengo)
    _, command = standup(cmd, conn, viewer, aliengo, udp)
    # while viewer is None or viewer.is_running():
    #     if aliengo:   
    #         # conn.set_cmd( cmd.aliengo_cmd() )         
    #         # conn.send( cmd.aliengo_cmd() )

    #         print("IM here")

    #         for i in range(12):
    #             cmd.motorCmd[i].q = command.get_command(i)[0]
    #             cmd.motorCmd[i].dq = command.get_command(i)[1]
    #             cmd.motorCmd[i].Kp = command.get_command(i)[2]
    #             cmd.motorCmd[i].Kd = command.get_command(i)[3]
    #             cmd.motorCmd[i].tau = command.get_command(i)[4]

    #         udp.SetSend( cmd )
    #         udp.Send()

    #     else:
    #         udp.SetSend( cmd )
    #         udp.Send() 
            
            # conn.send(lcmd.robot_cmd())

        # time.sleep(0.01)    


if __name__ == '__main__':
    main()