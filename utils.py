import pandas as pd
import numpy as np
import os
import shutil
import tarfile
import logging
from tqdm import tqdm
import matplotlib.pyplot as plt
from itertools import cycle

def start_logger(logger_name: str = 'logger'):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info('Logging started succesfully!')
    return logger

def read_from_tar(tar_path: str, logger: logging.Logger,  extraction_path: str, save_space: bool = False):
    with tarfile.open(tar_path, 'r') as tar:
        pbar = tqdm(tar.getmembers())
        for _,member in enumerate(pbar):
            if member.isreg():
                member.name = os.path.basename(member.name)
                pbar.set_description(f'Extracting {member.name}')
                tar.extract(member, extraction_path)
    tar.close()
    logger.info(f'Extracted {tar_path} to {extraction_path}')

def read_from_file(parent_dir: str, logger: logging.Logger):
    pass

def load_df_from_csv(file_path: str, delimiter: str = ',') -> pd.DataFrame:
    assert file_path.endswith('.csv'), 'File must be a csv file'
    return pd.read_csv(file_path, delimiter=delimiter)

def plot_signal(*signals, xlabel: str = 'Time (s)', ylabel: str = 'Amplitude', sampling_rate: int = 2000, by_time: bool = True):
    colors = cycle(["aqua", "black", "blue", "fuchsia", "gray", "green", "lime", "maroon", "navy", "olive", "purple", "red", "silver", "teal", "yellow"])
    for signal in signals:
        if by_time:
            time_index = np.arange(0, len(signal)/sampling_rate, 1/sampling_rate)
            plt.plot(time_index, signal, label = signal.name, color=next(colors))
        else:
            plt.plot(signal, label = signal.name, color=next(colors))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(loc="best")
    plt.show()
