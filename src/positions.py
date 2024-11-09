import command


laydown_q = [
    -0.471,  1.17, -2.74, # FR
    0.471, 1.17, -2.74, # FL
    -0.471,  1.17, -2.75, # RR
    0.471, 1.17, -2.75  # RL
]


def stand_command():
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

    return command.CommandFromArray3(front_legs*2 + back_legs*2)


def laydown_command():
    Kd = 2

    hip_Kp, hip_Kd  = 10, Kd
    thig_Kp, thig_Kd = 10, Kd
    calf_Kp, calf_Kd = 25, Kd

    hipR = (0., hip_Kp, hip_Kd)
    hipL = (0., hip_Kp, hip_Kd)

    front_legs = [
        (1.17, thig_Kp, thig_Kd),
        (-2.74, calf_Kp, calf_Kd)
    ]
    back_legs = [
        (2.5, thig_Kp, thig_Kd),
        (-2.75, calf_Kp, calf_Kd)
    ]
    
    return command.CommandFromArray3(
        [hipR] + front_legs +
        [hipL] + front_legs +
        [hipR] + back_legs +
        [hipL] + back_legs
    )
