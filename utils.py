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

def plot_signal_with_markers(signal: pd.Series, *markers, title: str = None, xlabel: str = 'Time (s)', ylabel: str = 'Amplitude', sampling_rate: int = 2000):
    color_markers = cycle(["maroon", "navy", "olive", "purple", "red", "silver", "teal", "yellow"])
    time_index = np.arange(0, len(signal)/sampling_rate, 1/sampling_rate)
    plt.plot(time_index, signal / signal.max(), label = signal.name, color='black')
    for marker in markers:
        plt.scatter(time_index[marker], signal[marker] / signal.max(), label = marker.name, color=next(color_markers))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if title:
        plt.title(title)
    plt.legend(loc="best")
    plt.show()

def plot_signals_with_marker(*signals, marker: pd.Series, title: str = None, xlabel: str = 'Time (s)', ylabel: str = 'Amplitude', sampling_rate: int = 2000):
    assert len(signals) > 0, 'At least one signal must be provided'
    color_signals = cycle(["black", "blue", "fuchsia", "gray", "green", "lime"])
    time_index = np.arange(0, len(signals[0])/sampling_rate, 1/sampling_rate)
    for signal in signals:
        plt.plot(time_index, signal / signal.max(), label = signal.name, color=next(color_signals))
        print(signal.name)
    plt.scatter(time_index[marker], signals[0][marker] / signals[0].max(), label = marker.name, color='red')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if title:
        plt.title(title)
    plt.legend(loc="best")
    plt.show()


def plot_signal(*signals, xlabel: str = 'Time (s)', ylabel: str = 'Amplitude', sampling_rate: int = 2000, by_time: bool = True):
    colors = cycle(["aqua", "black", "blue", "fuchsia", "gray", "green", "lime", "maroon", "navy", "olive", "purple", "red", "silver", "teal", "yellow"])
    for signal in signals:
        label = signal.name if isinstance(signal, pd.Series) else 'Signal'
        if by_time:
            time_index = np.arange(0, len(signal)/sampling_rate, 1/sampling_rate)
            plt.plot(time_index, signal, label = label, color=next(colors))
        else:
            plt.plot(signal, label = label, color=next(colors))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(loc="best")
    plt.show()
