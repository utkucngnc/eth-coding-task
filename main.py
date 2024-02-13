import os

from utils import *
from src.recording import Recording

cwd = os.getcwd()
tar_path = f'{cwd}/data/ptt_dataset.tar'
extraction_path = f'{cwd}/data'
file_path = f'{extraction_path}/gt01.csv'

# Start logging
logger = start_logger()

# Extract the tar file
#read_from_tar(tar_path, logger, extraction_path)

df = load_df_from_csv(file_path)
exg = df['chest sternum ECG']
recording = Recording(df, logger)
plot_signal(recording.ecg_raw[:5000], xlabel='Time (s)', ylabel='Amplitude', sampling_rate=recording.fs)
print(f'Heart rate: {recording.heart_rate} bpm')