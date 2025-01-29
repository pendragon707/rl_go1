import numpy as np

motors_names = ['FR_0', 'FR_1', 'FR_2',
                'FL_0', 'FL_1', 'FL_2',
                'RR_0', 'RR_1', 'RR_2',
                'RL_0', 'RL_1', 'RL_2']

motors_pos_range = [
    ('FR_0', -0.804, 0.914),
    ('FR_1', -0.676, 3.938),
    ('FR_2', -2.708, -0.872),
    ('FL_0', -0.872, 0.840),
    ('FL_1', -0.669, 3.948),
    ('FL_2', -2.782, -0.881),
    ('RR_0', -0.824, 0.897),
    ('RR_1', -0.685, 4.574),
    ('RR_2', -2.781, -0.873),
    ('RL_0', -0.899, 0.810),
    ('RL_1', -0.662, 4.552),
    ('RL_2', -2.791, -0.877)
]

# motors_mujoco_pos_range = [
#     ('FR_0', -0.863, 0.863),
#     ('FR_1', -0.686, 4.501),
#     ('FR_2', -2.818, -0.888),
#     ('FL_0', -0.863, 0.863),
#     ('FL_1', -0.686, 4.501),
#     ('FL_2', -2.818, -0.888),
#     ('RR_0', -0.863, 0.863),
#     ('RR_1', -0.686, 4.501),
#     ('RR_2', -2.818, -0.888),
#     ('RL_0', -0.863, 0.863),
#     ('RL_1', -0.686, 4.501),
#     ('RL_2', -2.818, -0.888)
# ]

# q_mujoco_min = np.array([e[1] for e in motors_mujoco_pos_range])
# q_mujoco_max = np.array([e[2] for e in motors_mujoco_pos_range])

motor_name_to_no = {name: no for no, name in enumerate(motors_names)}

simulation_qpos_motors = ['FL_0', 'FL_1', 'FL_2', 'FR_0', 'FR_1', 'FR_2',
                          'RL_0', 'RL_1', 'RL_2', 'RR_0', 'RR_1', 'RR_2']