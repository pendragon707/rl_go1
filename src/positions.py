def stand_position():
    Kd = 2

    hip_Kp, hip_Kd  = 10, Kd
    thig_Kp, thig_Kd = 10, Kd
    calf_Kp, calf_Kd = 25, Kd

    front_legs = [
        (0, hip_Kp, hip_Kd),     # Hip
        (0.3, thig_Kp, thig_Kd), # Thig
        (-1, calf_Kp, calf_Kd)   # Calf
    ]

    back_legs = [
        (0, hip_Kp, hip_Kd),  # Hip
        (1, thig_Kp, thig_Kd), # Thig
        (-1, calf_Kp, calf_Kd)  # Calf
    ]

    return front_legs*2 + back_legs*2


def laydown_position():
    return [
        -0.471,  1.17, -2.74, # FR
        0.471, 1.17, -2.74, # FL
        -0.471,  1.17, -2.75, # RR
        0.471, 1.17, -2.75  # RL
    ]

def laydown_position_2():
    front_legs = [0, 0.3, -2.5]
    back_legs = [0, 1.84, -2.5]
    
    return front_legs*2 + back_legs*2
