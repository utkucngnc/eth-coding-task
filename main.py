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
'''
mean_values = {}

for file in os.listdir(extraction_path):
    if file.endswith('.csv'):
        file_path = os.path.join(extraction_path, file)
        df = load_df_from_csv(file_path)
        rec = Recording(df, logger, 10)
        rec.process_ecg()

print(mean_values)
print(np.mean(mean_values.values()))
print(np.std(mean_values.values()))
print(recording.r_peaks_scipy[idx].where(recording.r_peaks_scipy[idx] == True).dropna())
print(recording.r_peaks[idx].where(recording.r_peaks[idx] == True).dropna())
print(recording.r_peaks_corrected[idx].where(recording.r_peaks_corrected[idx] == True).dropna())
'''

df = load_df_from_csv(file_path)
idx = slice(2000,7000)
recording = Recording(df, logger, 10)
recording.process_ecg()
recording.process_imu()
recording.process_bcg()
recording.process_bp()
recording.process_ppg()
recording.process_systolic_p()
recording.process_diastolic_p()
title  = f'{recording.state} -- {recording.ecg.heart_rate} bpm'
#plot_signal(recording.ecg.filtered_ecg[idx])

# Plot the IMU data
plot_signal_with_markers(recording.ecg.raw_ecg[idx], recording.r_peaks_corrected[idx],title = title)
#plot_signals_with_marker(recording.ecg.bb[idx],recording.ecg.dd[idx], marker = recording.r_peaks_corrected[idx], title = title)
