import torch
from collections import deque
import mujoco
import mujoco.viewer
import time
import config
import numpy as np
import utils


class PolicyController:
    def __init__(self):
        self.action_mean = np.array([0.05,  0.8, -1.4, -0.05,  0.8, -1.4, 0.05,  0.8, -1.4,-0.05,  0.8, -1.4])
        self.Kp = 35
        self.Kd = 0.6
        self.act_history = deque([np.zeros((1, 12)) for _ in range(4)], maxlen=4)
        self.obs_history = deque(maxlen=51)

        # policy
        self.device = 'cpu'

        prop_enc_pth = 'src/models/prop_encoder_1200.pt'
        mlp_pth = 'src/models/mlp_1200.pt'
        mean_file = 'src/models/mean1200.csv'
        var_file = 'src/models/var1200.csv'

        self.prop_loaded_encoder = torch.jit.load(prop_enc_pth).to(self.device)
        self.loaded_mlp = torch.jit.load(mlp_pth).to(self.device)
        self.loaded_mean = np.loadtxt(mean_file, dtype=np.float32)
        self.loaded_var = np.loadtxt(var_file, dtype=np.float32)
        self.clip_obs = 10

        self.step = 0

    def init_control(self, mj_data):
        self.control(
            mj_data, self.action_mean, np.zeros(12)
        )

    def update_observation(self, mj_data):
        gc = mj_data.sensordata[:12]
        gv = mj_data.sensordata[12:24]
        imu = mj_data.sensordata[36:40]
        eu = utils.quatToEuler(imu)
        obs = np.concatenate([eu[:2], gc, gv, self.act_history[-1][0], np.zeros(4)])

        if len(self.obs_history) == 51:
            self.obs_history.popleft()
        self.obs_history.append(obs)
        
    def observe(self):
        return np.concatenate(
            [np.concatenate(self.obs_history), np.zeros(28)]
        )
    
    def action(self, obs, mj_data):
        # normalize obs
        obs = self._normalize_observation(obs).reshape(1, -1).astype(np.float32)
        # get action
        obs_torch = torch.from_numpy(obs).cpu()
        with torch.no_grad():
            if self.step%2 == 0:
                self.latent_p = self.prop_loaded_encoder(obs_torch[:,:42*50])
            action_ll = self.loaded_mlp(
                torch.cat([obs_torch[:,42*50:42*(50 + 1)], self.latent_p], 1)
            )
        # normalize action
        if len(self.act_history) == 4:
            self.act_history.popleft()
        self.act_history.append(action_ll)
        action = self.act_history[0] * 0.4 + self.action_mean
        self.control(mj_data, action[0], np.zeros(12))
        self.step += 1

    def control(self, mj_data, gc: np.array, gv: np.array):
        q_state = np.array([mj_data.sensordata[i] for i in range(12)])
        v_state = np.array([mj_data.sensordata[i + 12] for i in range(12)])

        ctrl = self.Kp * (gc - q_state) + self.Kd * (gv - v_state)

        for i in range(12):
            mj_data.ctrl[i] = ctrl[i]

    def _normalize_observation(self, obs):
        return np.clip(
            (obs - self.loaded_mean[0]) / np.sqrt(self.loaded_var[0] + 1e-8),
            -self.clip_obs,
            self.clip_obs)


def main():
    mj_model = mujoco.MjModel.from_xml_path(config.ROBOT_SCENE)
    mj_model.opt.timestep = config.SIMULATE_DT
    mj_data = mujoco.MjData(mj_model)
    mujoco.mj_resetDataKeyframe(mj_model, mj_data, 3)

    viewer = mujoco.viewer.launch_passive(mj_model, mj_data)
    policy_controller = PolicyController()

    # reset
    policy_controller.init_control(mj_data)
    for _ in range(50):
        mujoco.mj_step(mj_model, mj_data)
    viewer.sync()
    for _ in range(104):
        policy_controller.update_observation(mj_data)

    control_dt = 0.01
    steps_per_control = int(control_dt / config.SIMULATE_DT + 1e-10)
    
    # observe / step
    while viewer.is_running():
        time.sleep(0.01)
        obs = policy_controller.observe()
        policy_controller.action(obs, mj_data)
        
        for _ in range(steps_per_control):
            mujoco.mj_step(mj_model, mj_data)
        policy_controller.update_observation(mj_data)
        viewer.sync()


if __name__ == '__main__':
    main()