import numpy as np
from numba import njit, prange


def ukih(Q, b_LH, return_exceed=False):
    """graphical method developed by UK Institute of Hydrology (UKIH, 1980)
    Aksoy, Hafzullah, Ilker Kurt, and Ebru Eris. “Filtered Smoothed Minima Baseflow Separation Method.” Journal of Hydrology 372, no. 1 (June 15, 2009): 94–101. https://doi.org/10.1016/j.jhydrol.2009.03.037.

    Args:
        Q (np.array): streamflow
        return_exceed (bool, optional): if True, returns the number of times the
            baseflow exceeds the streamflow.
    """
    N = 5
    block_end = Q.shape[0] // N * N
    idx_min = np.argmin(Q[:block_end].reshape(-1, N), axis=1)
    idx_min = idx_min + np.arange(0, block_end, N)
    idx_turn = ukih_turn(Q, idx_min)
    if idx_turn.shape[0] < 3:
        raise IndexError('Less than 3 turning points found')
    b = linear_interpolation(Q, idx_turn, return_exceed=return_exceed)
    b[:idx_turn[0]] = b_LH[:idx_turn[0]]
    b[idx_turn[-1] + 1:] = b_LH[idx_turn[-1] + 1:]
    return b


@njit
def ukih_turn(Q, idx_min):
    idx_turn = np.zeros(idx_min.shape[0], dtype=np.int64)
    for i in prange(idx_min.shape[0] - 2):
        if ((0.9 * Q[idx_min[i + 1]] < Q[idx_min[i]]) &
                (0.9 * Q[idx_min[i + 1]] < Q[idx_min[i + 2]])):
            idx_turn[i] = idx_min[i + 1]
    return idx_turn[idx_turn != 0]


@njit
def linear_interpolation(Q, idx_turn, return_exceed=False):
    if return_exceed:
        b = np.zeros(Q.shape[0] + 1)
    else:
        b = np.zeros(Q.shape[0])

    n = 0
    for i in range(idx_turn[0], idx_turn[-1] + 1):
        if i == idx_turn[n + 1]:
            n += 1
            b[i] = Q[i]
        else:
            b[i] = Q[idx_turn[n]] + (Q[idx_turn[n + 1]] - Q[idx_turn[n]]) / \
                (idx_turn[n + 1] - idx_turn[n]) * (i - idx_turn[n])
        if b[i] > Q[i]:
            b[i] = Q[i]
            if return_exceed:
                b[-1] += 1
    return b
