import logging
import pandas as pd
import numpy as np
from typing import Any
from scipy.stats import zscore

from src.utils import *

class ECG_Signal:
    def __init__(self, raw_ecg_signal: pd.Series, fs: int, logger: logging.Logger, cfg: Any) -> None:
        self.raw_ecg = remove_outliers(raw_ecg_signal)
        self.fs = fs
        self.logger = logger
        self.cfg = cfg
    
    def __len__(self) -> int:
        return len(self.filtered_ecg)
    
    def apply_pan_tompkins(self, filter_type: str) -> None:
        '''
        Apply the Pan-Tompkins algorithm to the ECG signal
        1. Bandpass filter
        2. Derivative filter
        3. Moving average filter
        4. Entropy calculation
        5. Peak detection
        6. Peak correction
        7. Heart rate calculation
        '''

        self.logger.info(f'Applying Pan-Tompkins algorithm to {self.raw_ecg.name}')
        assert filter_type.lower() in ['ma', 'ema'], 'Filter type must be either "ma" or "ema"'
        self.filtered_ecg = apply_bp_filter(signal = self.raw_ecg, **self.cfg.BPF_Param, fs=self.fs)
        self.filtered_ecg[np.abs(zscore(self.filtered_ecg)) > 2] = np.median(self.filtered_ecg)
        self.filtered_ecg = apply_derivative_filter(signal = self.filtered_ecg, **self.cfg.SavGol_Param)
        if filter_type.lower() == 'ma':
            self.filtered_ecg = apply_rolling(self.filtered_ecg, fs=self.fs, **self.cfg.MA_Param)
        else:
            self.filtered_ecg = apply_rolling_ema(self.filtered_ecg, **self.cfg.EMA_Param)
        self.filtered_ecg.rename(f'{self.raw_ecg.name} (Averaged)', inplace=True)
        self.filtered_ecg.fillna(0.0, inplace=True)
        self.filtered_ecg = self.filtered_ecg.apply(shannon_entropy)
        self.peak_indices = calculate_peak_indices(self.filtered_ecg, fs=self.fs)
        self.peak_indices_corrected = corrected_peaks(self.raw_ecg, self.peak_indices, self.fs)
        self.heart_rate = self.__calculate_heart_rate().__round__(1)

        # Uncomment to see the difference between the scipy and the custom peak detection
        # from scipy.signal import find_peaks
        # self.scipy_peaks = find_peaks(self.filtered_ecg, distance=int(0.2 * self.fs), height=self.filtered_ecg.mean() + 0.5 * self.filtered_ecg.std())[0]
        
    
    def __calculate_heart_rate(self) -> float:
        '''
        Calculate the heart rate from the peak indices
        Output:
            float: The heart rate
        '''
        intervals = np.diff(self.peak_indices_corrected)

        return 60 / (intervals.mean() / self.fs)