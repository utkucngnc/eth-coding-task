import pandas as pd
import logging

from src.utils import *

class IMU_Signal:
    def __init__(self, imu_vals: pd.Series, logger: logging.Logger) -> None:
        self.imu_vals = imu_vals
        self.bcg_raw = self.calculate_shannon_entropy()
        self.logger = logger
    
    def calculate_shannon_entropy(self):
        '''
        Calculate the Shannon entropy of the IMU signal
        Input:
            imu_vals: pd.Series: The IMU signal
        Output:
            pd.Series: The Shannon entropy of the IMU signal
        '''
        y = self.imu_vals.apply(shannon_entropy).rename('Raw BCG')
        return y
    

        