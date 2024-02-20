import os
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from utils import *
from src.recording import Recording

cwd = os.getcwd()
tar_path = f'{cwd}/data/ptt_dataset.tar'
extraction_path = f'{cwd}/data'
file_path = f'{extraction_path}/gt03.csv'

# Start logging
logger = start_logger()

# Extract the tar file
#read_from_tar(tar_path, logger, extraction_path)

df = load_df_from_csv(file_path)
recording = Recording(df, logger, 10)
idx = slice(2000,7000)
recording.process_ecg()
recording.process_imu()
recording.process_bcg()
recording.process_bp()
recording.process_ppg()
recording.process_systolic_p()
recording.process_diastolic_p()
recording.process_head_ppg()
title  = f'{recording.state}  -- {recording.head_avg_ptt} ms -- {recording.ecg.heart_rate} bpm'
#plot_signals_with_marker(recording.ecg.raw_ecg[idx], recording.processed_head_ppg.filtered_ppg[idx],marker = recording.r_peaks_corrected[idx], title = title)

plt.scatter(recording.bp[recording.ppg.troughs], np.array(recording.ppg.ptts) * 1000 / recording.fs, color='red')

plt.title(f'PTT vs Blood Pressure (ECG R-Peaks and Head PPG) (Corr. {np.corrcoef(recording.bp[recording.IJK[0][:-1]], np.array(recording.processed_head_ppg.ptts) * 1000 / recording.fs)[0,1]:.2f})')
plt.xlabel('Blood Pressure (mmHg)')
plt.ylabel('PTT (ms)')
plt.show()

# Plot the data
#plot_signal_with_markers(recording.bcg.filtered_bcg[idx],recording.I_valleys[idx],recording.J_peaks[idx], recording.K_valleys[idx],title = title)
#plot_signal_with_markers(recording.ecg.raw_ecg[idx], recording.r_peaks_corrected[idx],title = title)
#plot_signals_with_marker(recording.systolic_p[idx],recording.diastolic_p[idx], marker = recording.r_peaks_corrected[idx],title = title)
