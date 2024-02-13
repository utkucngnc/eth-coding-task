import logging
import pandas as pd
import numpy as np
from scipy.signal import butter, lfilter, savgol_filter, sosfiltfilt
from typing import List, Any

from utils import plot_signal

class ECG_Signal:
    def __init__(self, raw_ecg_signal: pd.Series, fs: int, logger: logging.Logger, cfg: Any) -> None:
        self.raw = raw_ecg_signal
        self.fs = fs
        self.logger = logger

        # Pan - Tompkins algorithm
        # 1. Bandpass filter
        # 2. Derivative filter
        # 3. Squaring
        # 4. Moving average filter
        # 5. Peak detection
        # 6. Heart rate calculation
        
        self.filtered_ecg = self.__apply_bp_filter(signal = self.raw, **cfg.BPF_Param)
        self.filtered_ecg = self.__apply_derivative_filter(signal = self.filtered_ecg, **cfg.SavGol_Param)
        self.filtered_ecg = self.__square_signal(self.filtered_ecg)
        self.filtered_ecg = self.__apply_moving_average(self.filtered_ecg)
        self.filtered_ecg.rename(f'{self.raw.name} (Filtered)', inplace=True)
        self.peak_indices = self.__calculate_peak_indices(self.filtered_ecg)
        self.heart_rate = self.__calculate_heart_rate().__round__(1)

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
        sos = butter(order, normalized_cutoffs, btype='bandpass', output='sos')
        return sos

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
        sos = self.__butter_bandpass(lowcut, highcut, order)
        y = sosfiltfilt(sos, signal)
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
    
    def __apply_moving_average(self, signal: pd.Series) -> pd.Series:
        '''
        Apply a moving average filter to the signal
        Input:
            signal: pd.Series: The input signal
            window_size: int: The window size
        Output:
            pd.Series: The filtered signal
        '''
        window_size = int(0.005 * self.fs)
        return signal.rolling(window=window_size).mean()

    def __calculate_peak_indices(self, signal: pd.Series) -> List[int]:
        '''
        Calculate the peak indices of the signal
        Input:
            signal: pd.Series: The input signal
        Output:
            List[int]: The peak indices
        '''
        distance = int(0.2 * self.fs) # value based on the refractory period of the human cardiac cells
        min_height = signal.mean()
        peak_vals = []
        start = 0
        while True:
            if start > len(signal):
                break
            if start + distance < len(signal):
                peak = signal[start:start+distance].idxmax()
                if signal[peak] < min_height:
                    start += distance
                    continue
                delta = int(distance / 2)
                if peak + delta > len(signal):
                    peak = signal[peak - delta:].idxmax()
                else:
                    peak = signal[peak-delta:peak+delta].idxmax()
                peak_vals.append(peak)
                start = peak + distance
            else:
                peak = signal[start:].idxmax()
                peak_vals.append(peak) if signal[peak] > min_height else None
                break
                
        return peak_vals
    
    def __calculate_heart_rate(self) -> float:
        '''
        Calculate the heart rate from the peak indices
        Output:
            float: The heart rate
        '''
        intervals = np.diff(self.peak_indices)

        return 60 / (intervals.mean() / self.fs)