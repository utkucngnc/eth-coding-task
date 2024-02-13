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
                session: int,
                fs: int = 2000) -> None:
        self.logger = logger
        self.fs = fs
        assert session in list(range(0, 11)), 'Session must be an integer between 0 and 10'
        self.session = session
        self.recording = recording[recording['session'] == self.session]
        self.recording.reset_index(drop=True, inplace=True)
        self.state = 'During Activity' if self.session % 2 == 1 else 'Resting'
        self.logger.info(f'Processing recording for session {self.session} ({self.state})')
        self.ecg = ECG_Signal(self.recording['chest sternum ECG'], self.fs, self.logger, Config)
        print(f'Heart rate: {self.ecg.heart_rate} bpm')


