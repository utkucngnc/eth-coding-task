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
        self.J_peaks = calculate_peak_indices_conditioned(self.filtered_bcg, fs=self.fs, r_peaks=r_peaks)
        self.I_valleys, self.K_valleys = calculate_valleys(self.filtered_bcg, self.J_peaks, self.fs)
        
        return self.I_valleys, self.J_peaks, self.K_valleys