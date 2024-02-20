import pandas as pd
from typing import List, Union
import numpy as np
import logging
from matplotlib import pyplot as plt

from src.config import Config
from src.utils import *
from utils import plot_signal

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
        self.ecg = ECG_Signal(raw_data, logger=self.logger, fs=self.fs, cfg=Config.ECG_Param)
        self.ecg.apply_pan_tompkins(Config.ecg_filter_type)
        self.logger.info(f'ECG signal processed for session {self.session} ({self.state})')
        self.r_peaks = fit_to_index(self.ecg.peak_indices, self.ecg.raw_ecg).rename('R-Peaks')
        self.r_peaks_corrected = fit_to_index(self.ecg.peak_indices_corrected, self.ecg.raw_ecg).rename('R-Peaks Corrected')
        # Uncomment to see the difference between the scipy and the custom peak detection (uncomment in ecg_signal.py as well)
        # self.r_peaks_scipy = fit_to_index(self.ecg.scipy_peaks, self.ecg.raw_ecg).rename('R-Peaks Scipy')
        return self
    
    def process_imu(self) -> None:
        self.imu = pd.Series(self.recording.filter(regex='IMU').values.tolist()).rename('IMU (Z, Y, X)')
        self.imu_processed = self.imu.apply(shannon_entropy).rename('IMU Entropy')
        self.imu_z = self.imu.apply(lambda x: x[0]).rename('IMU Z')
        self.imu_y = self.imu.apply(lambda x: x[1]).rename('IMU Y')
        self.imu_x = self.imu.apply(lambda x: x[2]).rename('IMU X')
        self.logger.info(f'IMU values stored for session {self.session} ({self.state})')
        return self
    
    def process_bcg(self) -> None:
        from src.bcg_signal import BCG_Signal
        raw_data = self.recording.filter(regex='BCG').iloc[:,0].rename('Force Plate BCG')
        self.bcg = BCG_Signal(raw_data, fs=self.fs, logger=self.logger, cfg=Config.BCG_Param)
        self.logger.info(f'BCG (Force Plate) values stored for session {self.session} ({self.state})')
        I_valleys, J_peaks, K_valleys = self.bcg.process(self.ecg.peak_indices_corrected)
        self.IJK = [I_valleys, J_peaks, K_valleys]
        self.J_peaks = fit_to_index(J_peaks,self.bcg.raw_bcg).rename('J')
        self.I_valleys = fit_to_index(I_valleys,self.bcg.raw_bcg).rename('I')
        self.K_valleys = fit_to_index(K_valleys,self.bcg.raw_bcg).rename('K')
        self.IJK_fitted = pd.concat([self.I_valleys, self.J_peaks, self.K_valleys], axis=1)
        return self

    def process_bp(self) -> None:
        self.bp = self.recording.filter(regex='BP').iloc[:,0].rename('Blood Pressure')
        self.logger.info(f'BP values stored for session {self.session} ({self.state})')
        return self
    
    def process_ppg(self) -> None:
        from src.ppg_signal import PPG_Signal
        self.ppg = self.recording.filter(regex='PPG').iloc[:,0].rename('PPG')
        self.logger.info(f'PPG values stored for session {self.session} ({self.state})')
        self.ppg = PPG_Signal(self.ppg, self.fs, self.logger, Config.BCG_Param)
        self.finger_avg_ptt = self.ppg.process(self.IJK, self.ecg.peak_indices_corrected)
        self.troughs = fit_to_index(self.ppg.troughs, self.ppg.filtered_ppg).rename('Troughs')
        return self
    
    def process_systolic_p(self) -> None:
        self.systolic_p = self.recording['finapres systolic']
        self.logger.info(f'Systolic Pressure values stored for session {self.session} ({self.state})')
        return self
    
    def process_diastolic_p(self) -> None:
        self.diastolic_p = self.recording['finapres diastolic']
        self.logger.info(f'Diastolic Pressure values stored for session {self.session} ({self.state})')
        return self
    
    def process_head_ppg(self) -> None:
        from src.ppg_signal import PPG_Signal
        raw_data = pd.Series(self.recording.filter(regex='head forehead PPG').values.tolist()).rename('Head PPG (IR, R, G)')
        self.logger.info(f'Head PPG values stored for session {self.session} ({self.state})')
        self.processed_head_ppg = raw_data.apply(shannon_entropy).rename('Head PPG Entropy')
        self.processed_head_ppg = PPG_Signal(self.processed_head_ppg, self.fs, self.logger, Config.BCG_Param)
        self.head_avg_ptt = self.processed_head_ppg.process(self.IJK, self.ecg.peak_indices_corrected)
        return self