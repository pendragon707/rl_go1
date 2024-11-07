import typing
import time
from threading import Thread, Lock

import mujoco
import mujoco.viewer

from ucl.lowCmd import lowCmd
from ucl.lowState import lowState


class Simulation:
    
    def __init__(self, config):
        self.mj_model = mujoco.MjModel.from_xml_path(config.ROBOT_SCENE)
        self.mj_model.opt.timestep = config.SIMULATE_DT
        self.mj_data = mujoco.MjData(self.mj_model)
        self.states = []
        self.locker = Lock()
        self.cmd = None
        self.config = config
        self.num_motor = self.mj_model.nu
        self.dim_motor_sensor = 3 * self.num_motor

    def set_keyframe(self, key_no: int):
        mujoco.mj_resetDataKeyframe(self.mj_model, self.mj_data, key_no)

    def start(self):
        self.viewer = mujoco.viewer.launch_passive(self.mj_model, self.mj_data)
        self.viewer_thread = Thread(target=self._viewer_loop, name='viewer_py')
        self.simulation_thread = Thread(target=self._simulation_loop, name='simulation_py')

        self.viewer_thread.start()
        self.simulation_thread.start()

    def _simulation_loop(self):
        send_step_start = None
        while self.viewer.is_running():
            step_start = time.perf_counter()

            if self.cmd is not None:
                cmd, self.cmd = self.cmd, None
                self.control(cmd)
            
            with self.locker:
                mujoco.mj_step(self.mj_model, self.mj_data)
                
            if send_step_start is None or (time.perf_counter() - send_step_start) >= self.config.SEND_STATE_DT:
                state = self.make_state()                    
                self.states.append((time.time_ns(), state))
                send_step_start = time.perf_counter()
            
            time_until_next_step = self.mj_model.opt.timestep - (
                time.perf_counter() - step_start
            )
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)

    def _viewer_loop(self):
        while self.viewer.is_running():
            with self.locker:
                self.viewer.sync()
            time.sleep(self.config.VIEWER_DT)

    def set_cmd(self, cmd: lowCmd):
        self.cmd = cmd

    def get_states(self) -> typing.List[typing.Tuple[int, lowState]]:
        states, self.states = self.states, []
        return states

    def make_state(self):
        rslt = lowState()

        for i in range(self.num_motor):
            rslt.motorState[i].q = self.mj_data.sensordata[i]
            rslt.motorState[i].dq = self.mj_data.sensordata[
                i + self.num_motor
            ]
            rslt.motorState[i].tau_est = self.mj_data.sensordata[
                i + 2 * self.num_motor
            ]

        rslt.imu.quaternion[0] = self.mj_data.sensordata[
            self.dim_motor_sensor + 0
        ]
        rslt.imu.quaternion[1] = self.mj_data.sensordata[
            self.dim_motor_sensor + 1
        ]
        rslt.imu.quaternion[2] = self.mj_data.sensordata[
            self.dim_motor_sensor + 2
        ]
        rslt.imu.quaternion[3] = self.mj_data.sensordata[
            self.dim_motor_sensor + 3
        ]

        rslt.imu.gyroscope[0] = self.mj_data.sensordata[
            self.dim_motor_sensor + 4
        ]
        rslt.imu.gyroscope[1] = self.mj_data.sensordata[
            self.dim_motor_sensor + 5
        ]
        rslt.imu.gyroscope[2] = self.mj_data.sensordata[
            self.dim_motor_sensor + 6
        ]

        rslt.imu.accelerometer[0] = self.mj_data.sensordata[
            self.dim_motor_sensor + 7
        ]
        rslt.imu.accelerometer[1] = self.mj_data.sensordata[
            self.dim_motor_sensor + 8
        ]
        rslt.imu.accelerometer[2] = self.mj_data.sensordata[
            self.dim_motor_sensor + 9
        ]

        return rslt

    def control(self, cmd: lowCmd):
         for i in range(self.num_motor):
            mc = cmd.motorCmd.motor(i)
            self.mj_data.ctrl[i] = (
                mc.tau +
                mc.kp * (mc.q - self.mj_data.sensordata[i]) +
                mc.kd * (mc.dq - self.mj_data.sensordata[i + self.num_motor])
            )
