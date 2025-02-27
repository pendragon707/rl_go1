import math
import numpy as np

import sys
sys.path.append("./submodules/free-dog-sdk/")

from ucl.lowState import lowState


def q_vec(state: lowState) -> np.array:
    r = np.full(12, 0.0)
    for no, motorState in enumerate(state.motorState[:12]):
        r[no] = motorState.q
    return r


def quatToEuler(quat):
    qw, qx, qy, qz = quat[0], quat[1], quat[2], quat[3]
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
    return np.array(r)


def interpolate(src, dst, cycle, total_cycles):
    if cycle >= total_cycles:
        return dst, True

    alpha = cycle / total_cycles
    return dst * alpha + src * (1 - alpha), False


class RunningMeanStd(object):
    def __init__(self, epsilon=1e-4, shape=()):
        """
        calulates the running mean and std of a data stream
        https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Parallel_algorithm

        :param epsilon: (float) helps with arithmetic issues
        :param shape: (tuple) the shape of the data stream's output
        """
        self.mean = np.zeros(shape, 'float32')
        self.var = np.ones(shape, 'float32')
        self.count = epsilon

    def update(self, arr):
        batch_mean = np.mean(arr[:,self.mean.shape[1]//2:], axis=0)
        batch_var = np.var(arr[:,self.var.shape[1]//2:], axis=0)
        batch_count = arr.shape[0]
        self.update_from_moments(batch_mean, batch_var, batch_count)

    def update_from_moments(self, batch_mean, batch_var, batch_count):
        half_mean = self.mean[:,self.mean.shape[1]//2:]
        half_var = self.var[:,self.var.shape[1]//2:]
        delta = batch_mean - half_mean
        tot_count = self.count + batch_count

        new_mean = half_mean + delta * batch_count / tot_count
        m_a = half_var * self.count
        m_b = batch_var * batch_count
        m_2 = m_a + m_b + np.square(delta) * (self.count * batch_count / (self.count + batch_count))
        new_var = m_2 / (self.count + batch_count)

        new_count = batch_count + self.count

        self.mean[:,self.mean.shape[1]//2:] = new_mean
        self.var[:,self.var.shape[1]//2:] = new_var
        # account for the slope information
        self.mean[:,-1] = 0
        self.var[:,-1] = 1
        # duplicate future and present geometry
        self.mean[:,-5:-3] = self.mean[:,-3:-1]
        self.var[:,-5:-3] = self.var[:,-3:-1]
        self.count = new_count

