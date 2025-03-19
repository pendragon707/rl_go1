from src import command


# laydown_q = [
#     -0.471,  1.17, -2.74, # FR
#     0.471, 1.17, -2.74, # FL
#     -0.471,  1.17, -2.75, # RR
#     0.471, 1.17, -2.75  # RL
# ]

laydown_q = [
    -0.15, 1.18, -2.8, # FR
    -0.15, 1.18, -2.8,# FL
    -0.15, 1.18, -2.8, # RR
    -0.15, 1.18, -2.8  # RL
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

def stand_command_2():
    return command.Command(
        q = [0.05,  0.8, -1.4, -0.05,  0.8, -1.4, 0.05,  0.8, -1.4, -0.05,  0.8, -1.4],        
        Kp = [90]*12,
        Kd = [1]*12
    )


def sit():
    return command.Command(
        # q = [0.05,  1.6, -0.0, -0.05,  1.6, -0.0, 0.05,  2.6, -2.75, -0.05,  2.6, -2.75], # сесть
        q = [0.05,  1.4, -0.9, -0.05,  1.4, -0.9, 0.05,  2.6, -2.75, -0.05,  2.6, -2.75], # сесть
        Kp = [180]*12,
        Kd = [5]*12
    )

def paw():
    return command.Command(
        q = [0.05,  1.5, -0.9, -0.05,  0.8, -1.4, 0.05,  2.6, -2.75, -0.05,  2.6, -2.75], # подать лапу
        Kp = [180]*12,
        Kd = [5]*12
    )

def dance(num):    
    return command.Command(
        q = [0.05,  1.0, -1.7, -0.05,  1.0, -1.7, 0.05,  1.0, -1.1, -0.05,  1.0, -1.1], # перекатываться вперед / назад
        # q = [0.05,  0.8, -1.8, -0.05,  0.8, -1.4, 0.05,  0.8, -1.4,-0.05,  0.8, -1.4], # перекатываться на передних ногах
        Kp = [180]*12,
        Kd = [5]*12
    )

def stand_command_3():
    return command.Command(
        q = [-0.15, 0.3, -1, -0.15, 0.3, -1, -0.15, 1, -1, -0.15, 1, -1],
        Kp = [90]*12,
        Kd = [1]*12
    )


def laydown_command():
    Kd = 2

    hip_Kp, hip_Kd  = 10, Kd
    thig_Kp, thig_Kd = 10, Kd
    calf_Kp, calf_Kd = 25, Kd

    front_legs = [
        (0., hip_Kp, hip_Kd),
        (1.17, thig_Kp, thig_Kd),
        (-2.74, calf_Kp, calf_Kd)
    ]
    back_legs = [
        (0., hip_Kp, hip_Kd),
        (2.5, thig_Kp, thig_Kd),
        (-2.75, calf_Kp, calf_Kd)
    ]

    return command.CommandFromArray3(front_legs*2 + back_legs*2)

def laydown_command_2():
    return command.Command(
        q = [-0.15, 1.18, -2.8, -0.15, 1.18, -2.8, -0.15, 1.18, -2.8, -0.15, 1.18, -2.8],
        Kp = [90]*12,
        Kd = [1]*12
    )