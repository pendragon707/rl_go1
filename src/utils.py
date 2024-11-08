import ucl


def get_pos_vector(state: ucl.lowState) -> list[float]:
    r = [0]*12
    for no, motorState in enumerate(state.motorState[:12]):
        r[no] = motorState.q
    return r
