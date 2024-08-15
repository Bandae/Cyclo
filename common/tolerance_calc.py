from typing import Sequence, Tuple, Union
import numpy as np
from scipy.stats import truncnorm


def normal_in_tolerance(main_value: Union[int, float], tolerances: Tuple[float, float], sd: Union[int, float]=1, sample_amount: int=1) -> np.ndarray:
    """Return an array of random values from a truncated normal distribution simulating an engineering clearance.
    
    - main_value - the dimension on which the tolerance is set
    - tolerances - a tuple of two values describing the lower and upper bounds of the tolerance, relative to main_value
    - sd - standard deviation
    - sample_amount - amount of random values to return
    """

    if tolerances[0] == 0 and tolerances[1] == 0:
        return np.array([main_value for _ in range(sample_amount)])
    tol_range = (tolerances[0]+main_value, tolerances[1]+main_value)
    mean = (tol_range[1] - tol_range[0]) / 2 + tol_range[0]
    return truncnorm((tol_range[0] - mean) / sd, (tol_range[1] - mean) / sd, loc=mean, scale=sd).rvs(sample_amount)


def normal_in_tolerance_set(main_values: Sequence[Union[int, float]], tolerances: Tuple[float, float], sd: Union[int, float]=1, sample_amount: int=1) -> np.ndarray:
    """Return an array of random values from a truncated normal distribution for multiple values simulating an engineering clearance.
    Use for a sequence of different values, all tolerated with the same bounds.
    
    - main_values - the base dimensions on which the tolerance is set
    - tolerances - a tuple of two values describing the lower and upper bounds of the tolerance, relative to main_value
    - sd - standard deviation
    - sample_amount - amount of random values to generate for each value in main_values

    Size of returned array == (len(main_values) * sample_amount).

    To get the n-th set of main_values with added deviations:
    returned[(n-1)*len(main_values):n*len(main_values)] (where 1 <= n <= sample_amount).

    To instead get all of the samples for the n-th value of main_values:
    returned[n-1:-1:len(main_values)] (where 1 <= n <= len(main_values)).
    """

    if tolerances[0] == 0 and tolerances[1] == 0:
        return np.array([*main_values] * sample_amount)
    count_in_set = len(main_values)
    mean = (tolerances[1] - tolerances[0]) / 2 + tolerances[0]
    deviations = truncnorm((tolerances[0] - mean) / sd, (tolerances[1] - mean) / sd, loc=mean, scale=sd).rvs(count_in_set*sample_amount)
    for i, value in enumerate(main_values):
        for j in range(sample_amount):
            deviations[i+j*count_in_set] += value
    return deviations
