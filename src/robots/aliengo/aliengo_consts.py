TARGET_PORT = 8007
LOCAL_PORT = 8082
TARGET_IP = "192.168.123.10"   # target IP address
LOW_CMD_LENGTH = 610
LOW_STATE_LENGTH = 771

ALIENGO_LOW_WIRED_DEFAULTS = (LOCAL_PORT, TARGET_IP, TARGET_PORT, LOW_CMD_LENGTH, LOW_STATE_LENGTH, -1) 

HIGHLEVEL = 0x00
LOWLEVEL  = 0xff

# Эти значения надо уточнить
motors_aliengo_pos_range = [
    ('FR_0', -1.168, 1.218),    # hip 
    ('FR_1', 0.001, 6.098),    # arm 
    ('FR_2', -2.801, -0.674),   # knee
    ('FL_0', -1.2, 1.199),    # hip 
    ('FL_1', 1.193, 5.518),    # arm 
    ('FL_2', -2.801, -0.673),   # knee
    ('RR_0', -1.203, 1.216),    # hip 
    ('RR_1', 1.176, 3.66),    # arm 
    ('RR_2', -2.809, -0.671),   # knee
    ('RL_0', -1.206, 0.198),    # hip 
    ('RL_1', 1.163, 3.664),    # arm 
    ('RL_2', -2.806, -0.663)   # knee
]

# motors_pos_range = [
#     ('FR_0', -0.804, 0.914),
#     ('FR_1', -0.676, 3.938),
#     ('FR_2', -2.708, -0.872),
#     ('FL_0', -0.872, 0.840),
#     ('FL_1', -0.669, 3.948),
#     ('FL_2', -2.782, -0.881),
#     ('RR_0', -0.824, 0.897),
#     ('RR_1', -0.685, 4.574),
#     ('RR_2', -2.781, -0.873),
#     ('RL_0', -0.899, 0.810),
#     ('RL_1', -0.662, 4.552),
#     ('RL_2', -2.791, -0.877)
# ]