import math
import numpy as np
from typing import List

x = np.random.randn(10, size=(3,3))

def shannon_entropy(list_values: List[float]) -> float:
    '''
    Calculate the Shannon entropy for the given data
    Input:
        list_values: list: The input data
    Output:
        float: The Shannon entropy of the input data
    '''
    # Initialize the variables
    shannon_entropy = 0
    for i in list_values:
        shannon_entropy = abs(i) * math.log(abs(i))
    return -1 * shannon_entropy

for i in range(x.shape[0]):
    print(shannon_entropy(x[i]))