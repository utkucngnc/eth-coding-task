import pandas as pd
from typing import List, Union
import numpy as np
import logging

from src.config import Config
from src.utils import fit_to_index

class Recording:
    def __init__(
                self, 
                recording: pd.DataFrame, 
                logger: logging.Logger,
                session: int,
                fs: int = 2000) -> None:
        self.logger = logger
        self.fs = fs
        assert session in Config.activities.keys(), 'Session must be an integer between 0 and 10'
        self.session = session
        self.recording = recording[recording['session'] == self.session]
        self.recording.reset_index(drop=True, inplace=True)
        self.state = Config.activities[self.session]
        self.logger.info(f'Processing recording for session {self.session} ({self.state})')

    def process_ecg(self) -> None:
        from src.ecg_signal import ECG_Signal
        raw_data = self.recording['chest sternum ECG'].copy()
        self.ecg = ECG_Signal(raw_data, logger=self.logger, fs=self.fs, cfg=Config)
        self.ecg.apply_pan_tompkins()
        self.logger.info(f'ECG signal processed for session {self.session} ({self.state})')
        self.r_peaks = fit_to_index(self.ecg.peak_indices, self.ecg.raw_ecg).rename('R-Peaks')
        self.r_peaks_corrected = fit_to_index(self.ecg.corrected_peak_indices, self.ecg.raw_ecg).rename('R-Peaks Corrected')
        # Uncomment to see the difference between the scipy and the custom peak detection (uncomment in ecg_signal.py as well)
        # self.r_peaks_scipy = fit_to_index(self.ecg.scipy_peaks, self.ecg.raw_ecg).rename('R-Peaks Scipy')
        return self
    
    def process_imu(self) -> None:
        from src.imu_signal import IMU_Signal
        self.imu = pd.Series(self.recording.filter(regex='IMU').values.tolist()).rename('IMU (Z, Y, X)')
        self.imu = IMU_Signal(self.imu, self.logger)
        self.logger.info(f'IMU values stored for session {self.session} ({self.state})')
        return self
    
    def process_bcg(self) -> None:
        self.bcg = self.recording.filter(regex='BCG')
        self.logger.info(f'BSC values stored for session {self.session} ({self.state})')
        return self

    def process_bp(self) -> None:
        self.bp = self.recording.filter(regex='BP').rename(columns=lambda x: x.split(' ')[-1])
        self.logger.info(f'BP values stored for session {self.session} ({self.state})')
        return self
    
    def process_ppg(self) -> None:
        self.ppg = self.recording.filter(regex='PPG').rename(columns=lambda x: x.split(' ')[-1])
        self.logger.info(f'PPG values stored for session {self.session} ({self.state})')
        return self
    
    def process_systolic_p(self) -> None:
        self.systolic_p = self.recording.filter(regex='systolic').rename(columns=lambda x: x.split(' ')[-1])
        self.logger.info(f'Systolic Pressure values stored for session {self.session} ({self.state})')
        return self
    
    def process_diastolic_p(self) -> None:
        self.diastolic_p = self.recording.filter(regex='diastolic').rename(columns=lambda x: x.split(' ')[-1])
        self.logger.info(f'Diastolic Pressure values stored for session {self.session} ({self.state})')
        return self