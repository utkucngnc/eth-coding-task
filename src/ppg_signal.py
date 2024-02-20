import pandas as pd
import numpy as np
from logging import Logger
from typing import Any, List

from src.utils import *

class PPG_Signal:
    def __init__(self, raw_signal: pd.Series, fs: int, logger: Logger, cfg: Any) -> None:
        self.raw_ppg = remove_outliers(raw_signal)
        self.logger = logger
        self.fs = fs
        self.cfg = cfg
    
    def process(self, peak_indices: List, r_peaks) -> float:
        self.filtered_ppg = apply_bp_filter(signal=self.raw_ppg, fs = self.fs, **self.cfg.BPF_Param).rename(f'{self.raw_ppg.name} (Filtered)')
        self.filtered_ppg = apply_rolling_ema(self.filtered_ppg, **self.cfg.EMA_Param).rename(f'{self.filtered_ppg.name} (Smoothed)')
        self.filtered_ppg = apply_derivative_filter(self.filtered_ppg, **self.cfg.SavGol_Param).rename(f'{self.filtered_ppg.name} (Derivative)')
        self.troughs = calculate_peak_indices_conditioned(self.filtered_ppg, self.fs, peak_indices[1][:-1], lbound=0.01, ubound=0.2)
        self.ptts = np.array(self.calculate_ptts(self.troughs, r_peaks)) * 1000 / self.fs # in ms
        self.avg_ptt = np.mean(self.ptts)
        return self.avg_ptt
    
    def calculate_ptts(self, troughs, r_peaks):
        ptts = []
        for i in range(len(troughs)):
            ptts.append(troughs[i] - r_peaks[i])
        return ptts