import os

from utils import *
from src.ecgsig import ECG_Signal

cwd = os.getcwd()
tar_path = f'{cwd}/data/ptt_dataset.tar'
extraction_path = f'{cwd}/data'
file_path = f'{extraction_path}/gt01.csv'

# Start logging
logger = start_logger()

# Extract the tar file
#read_from_tar(tar_path, logger, extraction_path)

df = load_df_from_csv(file_path)
ecg = ECG_Signal(df['chest sternum ECG'], 2000, logger)
plot_signal(ecg.filtered_ecg[:5000], ecg.raw.name)