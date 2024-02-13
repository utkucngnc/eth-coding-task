import os

from utils import *
from src.recording import Recording
from src.ecg_signal import ECG_Signal
from src.config import Config

cwd = os.getcwd()
tar_path = f'{cwd}/data/ptt_dataset.tar'
extraction_path = f'{cwd}/data'
file_path = f'{extraction_path}/gt03.csv'

# Start logging
logger = start_logger()

# Extract the tar file
#read_from_tar(tar_path, logger, extraction_path)

df = load_df_from_csv(file_path)

recording = Recording(df, logger, 6)
plot_signal(recording.ecg.raw[:25000])
