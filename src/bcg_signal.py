import pandas as pd
from logging import Logger
from typing import Any, List

from src.utils import *

class BCG_Signal:
    def __init__(self, raw_signal: pd.Series, fs: int, logger: Logger, cfg: Any) -> None:
        self.raw_bcg = remove_outliers(raw_signal)
        self.logger = logger
        self.fs = fs
        self.cfg = cfg
    
    def process(self, r_peaks: List[int]) -> pd.Series:
        self.filtered_bcg = apply_bp_filter(signal=self.raw_bcg, fs = self.fs, **self.cfg.BPF_Param).rename(f'{self.raw_bcg.name} (Filtered)')
        self.filtered_bcg = apply_rolling_ema(self.filtered_bcg, **self.cfg.EMA_Param).rename(f'{self.filtered_bcg.name} (Smoothed)')
        self.filtered_bcg = apply_derivative_filter(self.filtered_bcg, **self.cfg.SavGol_Param).rename(f'{self.filtered_bcg.name} (SavGol)')
        self.filtered_bcg = apply_derivative_filter(self.filtered_bcg, **self.cfg.SavGol_Param)
        self.peak_indices = calculate_peak_indices_conditioned(self.filtered_bcg, fs=self.fs, r_peaks=r_peaks)
        self.peak_indices_corrected = corrected_peaks(self.raw_bcg, self.peak_indices, self.fs)
    
    def __extract_IK_points(self, r_peak: int):
        time_margin = slice(int(0.1 * self.fs + r_peak), int(0.3 * self.fs + r_peak), 1) # J - peak is searched in this window after R - peak [Kim+18]
        J = self.raw_bcg[time_margin].idxmax()
        return J

