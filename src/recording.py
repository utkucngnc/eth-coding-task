import pandas as pd
from scipy.signal import butter, lfilter, savgol_filter, find_peaks
from typing import List
import numpy as np
import matplotlib.pyplot as plt
import logging

from src.config import Config
from src.ecg_signal import ECG_Signal

class Recording:
    def __init__(
                self, 
                recording: pd.DataFrame, 
                logger: logging.Logger,
                fs: int = 2000) -> None:
        self.recording = recording
        self.logger = logger
        self.fs = fs
        self.ecg_raw = self.recording['chest sternum ECG']
        self.ecg = ECG_Signal(self.ecg_raw, self.fs, self.logger, Config)
        self.filtered_ecg = self.ecg.filtered_ecg
        self.peak_indices = self.ecg.peak_indices
        self.heart_rate = self.ecg.heart_rate
        self.logger.info('ECG Signal processed successfully!')


