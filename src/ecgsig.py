import pandas as pd
from scipy.signal import butter, lfilter, savgol_filter
from typing import List
import numpy as np
import matplotlib.pyplot as plt
import logging

from src.config import BPF_Param, SavGol_Param, MA_Param


class ECG_Signal:
    def __init__(self, raw_ecg_signal: pd.Series, fs: int, logger: logging.Logger) -> None:
        self.raw = raw_ecg_signal
        self.fs = fs
        self.logger = logger
        self.filtered_ecg = self.__apply_bp_filter(signal = self.raw, **BPF_Param)
        self.filtered_ecg = self.__apply_derivative_filter(signal = self.filtered_ecg, **SavGol_Param)
        self.filtered_ecg = self.__square_signal(self.filtered_ecg)
        self.filtered_ecg = self.__apply_moving_average(self.filtered_ecg, **MA_Param)

    def __butter_bandpass(self, lowcut: int, highcut: int, order: int):
        '''
        Create a bandpass filter (Butterworth filter)
        Input:
            lowcut: int: The lower cutoff frequency
            highcut: int: The higher cutoff frequency
            order: int: The filter order
        Output:
            tuple: The filter coefficients
        '''
        nyq = 0.5 * self.fs
        normalized_cutoffs = [lowcut / nyq, highcut / nyq]
        b, a = butter(order, normalized_cutoffs, btype='bandpass')[:2]
        return b, a

    def __apply_bp_filter(self, signal: pd.Series, lowcut: int, highcut: int, order: int) -> pd.Series:
        '''
        Apply a bandpass filter to the signal (Butterworth filter)
        Input:
            signal: pd.Series: The input signal
            lowcut: int: The lower cutoff frequency
            highcut: int: The higher cutoff frequency
            order: int: The filter order
        Output:
            pd.Series: The filtered signal
        '''
        b, a = self.__butter_bandpass(lowcut, highcut, order)
        y = lfilter(b, a, lfilter(b,a,signal))
        return pd.Series(y)
    
    def __apply_derivative_filter(self, signal: pd.Series, p: int, w: int, m: int) -> pd.Series:
        '''
        Apply a derivative filter to the signal (Savitzky-Golay filter)
        Input:
            signal: pd.Series: The input signal
            p: int: The polynomial order
            w: int: The window size
            m: int: The derivative order
        Output:
            pd.Series: The filtered signal
        '''
        y = savgol_filter(signal, polyorder=p, window_length=w, deriv=m)
        return pd.Series(y)
    
    def __square_signal(self, signal: pd.Series) -> pd.Series:
        '''
        Square the signal to maximize difference between peaks and valleys
        Input:
            signal: pd.Series: The input signal
        Output:
            pd.Series: The squared signal
        '''
        return signal**2
    
    def __apply_moving_average(self, signal: pd.Series, window_size: int) -> pd.Series:
        '''
        Apply a moving average filter to the signal
        Input:
            signal: pd.Series: The input signal
            window_size: int: The window size
        Output:
            pd.Series: The filtered signal
        '''
        return signal.rolling(window=window_size).mean()

    def calculate_peak_indices(signal: pd.Series, sampling_rate: int = 2000) -> List[bool]:
        pass