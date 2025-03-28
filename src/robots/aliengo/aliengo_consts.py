TARGET_PORT = 8007
LOCAL_PORT = 8082
TARGET_IP = "192.168.123.10"   # target IP address
LOW_CMD_LENGTH = 610
LOW_STATE_LENGTH = 771

ALIENGO_LOW_WIRED_DEFAULTS = (LOCAL_PORT, TARGET_IP, TARGET_PORT, LOW_CMD_LENGTH, LOW_STATE_LENGTH, -1) 

HIGHLEVEL = 0x00
LOWLEVEL  = 0xff

motors_aliengo_pos_range = [
    ('FR_0', -0.873, 1.047),   
    ('FR_1', -0.524, 3.927),   
    ('FR_2', -2.775, -0.611),  
    ('FL_0', -0.873, 1.047),   
    ('FL_1', -0.524, 3.927),   
    ('FL_2', -2.775, -0.611),  
    ('RR_0', -0.873, 1.047),   
    ('RR_1',-0.524, 3.927),   
    ('RR_2', -2.775, -0.611),  
    ('RL_0', -0.873, 1.047),   
    ('RL_1',-0.524, 3.927),   
    ('RL_2', -2.775, -0.611)  
]