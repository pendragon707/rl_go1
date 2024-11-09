import math
import numpy as np
from ucl.lowState import lowState


def q_vec(state: lowState) -> np.array:
    r = np.full(12, 0.0)
    for no, motorState in enumerate(state.motorState[:12]):
        r[no] = motorState.q
    return r


def quatToEuler(quat):
    qw, qx, qy, qz = quat
    # roll (x-axis rotation)
    sinr_cosp = 2 * (qw * qx + qy * qz)
    cosr_cosp = 1 - 2 * (qx * qx + qy * qy)

    r = []
    r.append(math.atan2(sinr_cosp, cosr_cosp))

    # pitch (y-axis rotation)
    sinp = 2 * (qw * qy - qz * qx)
    if abs(sinp) >= 1:
    # use 90 degrees if out of range
        if sinp > 0:
            r.append(math.pi / 2)
        else:
            r.append(-math.pi / 2)
    else:
        r.append(math.asin(sinp))

    # yaw (z-axis rotation)
    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
    r.append(math.atan2(siny_cosp, cosy_cosp))
    return r


def interpolate(src, dst, cycle, total_cycles):
    if cycle >= total_cycles:
        return dst

    alpha = cycle / total_cycles
    return dst * alpha + src * (1 - alpha)
