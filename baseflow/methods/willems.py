import numpy as np
from numba import njit


@njit
def willems(Q, a, w, initial_method='Q0', return_exceed=False):
    """digital filter (Willems, 2009)

    Args:
        Q (np.array): streamflow
        a (float): recession coefficient
        w (float): case-speciﬁc average proportion of the quick ﬂow
                   in the streamflow, calibrated in baseflow.param_estimate
        initial_method (str or float, optional): method to calculate the initial baseflow value.
            Accepted string values are:
            - 'Q0': Use Q[0] as the initial baseflow value.
            - 'min': Use np.min(Q) as the initial baseflow value.
            - 'LH': Calculate the initial baseflow value using the LH method.
            Alternatively, a float value can be provided to directly set the initial baseflow value.
            Default is 'Q0'.
        return_exceed (bool, optional): if True, returns the number of times the
            baseflow exceeds the streamflow.
    """
    if return_exceed:
        b = np.zeros(Q.shape[0] + 1)
    else:
        b = np.zeros(Q.shape[0])

    # Set initial value for b based on the specified method
    if isinstance(initial_method, str):
        if initial_method == 'Q0':
            b[0] = Q[0]
        elif initial_method == 'min':
            b[0] = np.min(Q)
        elif initial_method == 'LH':
            b[0] = lh(Q)[0]  # Calculate the initial value using the LH method
        else:
            raise ValueError(f"Invalid initial_method: {initial_method}")
    else:
        b[0] = initial_method

    v = (1 - w) * (1 - a) / (2 * w)
    for i in range(Q.shape[0] - 1):
        b[i + 1] = (a - v) / (1 + v) * b[i] + v / (1 + v) * (Q[i] + Q[i + 1])
        if b[i + 1] > Q[i + 1]:
            b[i + 1] = Q[i + 1]
            if return_exceed:
                b[-1] += 1
    return b

@njit
def lh(Q, beta=0.925):
    """LH digital filter (Lyne & Hollick, 1979)

    Args:
        Q (np.array): streamflow
        beta (float): filter parameter, 0.925 recommended by (Nathan & McMahon, 1990)
    """
    b = np.zeros(Q.shape[0])
    b[0] = Q[0]
    for i in range(Q.shape[0] - 1):
        b[i + 1] = beta * b[i] + (1 - beta) / 2 * (Q[i] + Q[i + 1])
        if b[i + 1] > Q[i + 1]:
            b[i + 1] = Q[i + 1]
    return b