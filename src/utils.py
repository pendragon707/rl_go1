import numpy as np
import ucl


def q_vec(state: ucl.lowState) -> np.array:
    r = np.full(12, 0.0)
    for no, motorState in enumerate(state.motorState[:12]):
        r[no] = motorState.q
    return r


def interpolate(src, dst, cycle, total_cycles):
    if cycle >= total_cycles:
        return dst

    alpha = cycle / total_cycles
    return dst * alpha + src * (1 - alpha)
