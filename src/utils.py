from scipy.signal import butter, sosfiltfilt, savgol_filter
import pandas as pd
import numpy as np
from typing import List, Union

def remove_outliers(signal: pd.Series):
    '''
    Remove the outliers from the signal
    Input:
        signal: pd.Series: The input signal
    Output:
        pd.Series: The signal without outliers
    '''
    y = signal[signal.between(signal.quantile(0.01), signal.quantile(0.98))]
    y.reset_index(drop=True, inplace=True)
    y.rename(signal.name, inplace=True)
    return y

def butter_bandpass(lowcut: int, highcut: int, order: int, fs: int):
    '''
    Create a bandpass filter (Butterworth filter)
    Input:
        lowcut: int: The lower cutoff frequency
        highcut: int: The higher cutoff frequency
        order: int: The filter order
    Output:
        tuple: The filter coefficients
    '''
    nyq = 0.5 * fs
    normalized_cutoffs = [lowcut / nyq, highcut / nyq]
    sos = butter(order, normalized_cutoffs, btype='bandpass', output='sos')
    return sos

def apply_bp_filter(lowcut: int, highcut: int, order: int, fs: int, signal: pd.Series) -> pd.Series:
    '''
    Apply a bandpass filter to the signal (Butterworth filter)
    Input:
        signal: pd.Series: The input signal
        lowcut: int: The lower cutoff frequency
        highcut: int: The higher cutoff frequency
        order: int: The filter order
    Output:
        pd.Series: The filtered signal
    '''
    sos = butter_bandpass(lowcut, highcut, order, fs)
    y = sosfiltfilt(sos, signal)
    return pd.Series(y)

def apply_derivative_filter(signal: pd.Series, p: int, w: int, m: int) -> pd.Series:
    '''
    Apply a derivative filter to the signal (Savitzky-Golay filter)
    Input:
        signal: pd.Series: The input signal
        p: int: The polynomial order
        w: int: The window size
        m: int: The derivative order
    Output:
        pd.Series: The filtered signal
    '''
    y = savgol_filter(signal, polyorder=p, window_length=w, deriv=m)
    return pd.Series(y)

def apply_rolling(signal: pd.Series, fs: int, window_ms: int, win_type: str = None, rolling_type: str = ['mean' or 'median']) -> pd.Series:
    '''
    Apply a moving average filter to the signal
    Input:
        signal: pd.Series: The input signal
        window_size: int: The window size
    Output:
        pd.Series: The filtered signal
    '''
    window_size = int(window_ms * fs * 1e-3)
    obs = signal.rolling(window=window_size, win_type = win_type if win_type else None)
    return obs.mean() if rolling_type == 'mean' else obs.median()

def calculate_peak_indices(signal: pd.Series, fs: int) -> List[int]:
    '''
    Calculate the peak indices of the signal
    Input:
        signal: pd.Series: The input signal
    Output:
        List[int]: The peak indices
    '''
    distance = int(0.2 * fs) # value based on the refractory period of the human cardiac cells, 200 ms
    min_height = signal.mean() + 1.5 * signal.std()
    peak_vals = []
    start = int(0.01 * fs) # 10ms offset
    while True:
        if start > len(signal):
            break
        if start + distance < len(signal):
            peak = signal[start:start+distance].idxmax()
            if signal[peak] < min_height:
                start += distance
                continue
            delta = int(distance / 2)
            if peak + delta > len(signal):
                peak = signal[peak:].idxmax()
            else:
                peak = signal[peak:peak+delta].idxmax()
            peak_vals.append(peak)
            start = peak + distance
        else:
            peak = signal[start:].idxmax()
            peak_vals.append(peak) if signal[peak] > min_height else None
            break
            
    return peak_vals

def corrected_peaks(signal: pd.Series, peaks: List[int], fs: int) -> List[int]:
    '''
    Correct the peak indices based on the signal
    Input:
        signal: pd.Series: The input signal
        peaks: List[int]: The peak indices
    Output:
        List[int]: The corrected peak indices
    '''
    corrected_peaks = []
    for peak in peaks:
        window = slice(int(peak - 0.07 * fs), int(peak + 0.07 * fs))
        local_max = signal[window].idxmax()
        if peak != local_max:
            corrected_peaks.append(local_max)
        else:
            corrected_peaks.append(peak)
    return corrected_peaks

def shannon_entropy(val: Union[List[float],float]) -> float:
    '''
    Calculate the Shannon entropy for the given data
    Input:
        list_values: list: The input data
    Output:
        float: The Shannon entropy of the input data
    '''
    # Initialize the variables
    shannon_entropy = 0
    if isinstance(val, list):
        for i in val:
            shannon_entropy = abs(i) * np.log(abs(i), where=i>0)
    else:
        shannon_entropy = abs(val) * np.log(abs(val), where=val>0)
    return -1 * shannon_entropy

def fit_to_index(indices: List[int], signal: pd.Series) -> pd.Series:
    '''
    Fit the indices to the signal
    Input:
        indices: List[int]: The indices to fit
        signal: pd.Series: The signal
    Output:
        List[int]: The fitted indices
    '''
    y = [False] * len(signal)
    for i in indices:
        y[i] = True
    return pd.Series(y)

def apply_threshold(signal: pd.Series, threshold: Union[List[float] , float]) -> pd.Series:
    '''
    Apply a threshold to the signal to eliminate outliers
    Input:
        signal: pd.Series: The input signal
        threshold: float: The threshold value
    Output:
        pd.Series: The thresholded signal
    '''
    if isinstance(threshold, list):
        threshold.sort()
        func = lambda x: x if x > threshold[0] and x < threshold[1] else np.nan
    else:
        func = lambda x: x if abs(x) < threshold else np.nan
    y = signal.apply(func)
    y.dropna(inplace=True)
    y.reset_index(drop=True, inplace=True)
    return y

def min_max_scale(signal: pd.Series, threshold: Union[List[float], float] = None) -> pd.Series:
    '''
    Normalize the signal
    Input:
        signal: pd.Series: The signal to normalize
    Output:
        pd.Series: The normalized signal
    '''
    y = signal.copy()
    if threshold:
        if isinstance(threshold, list):
            threshold.sort()
            y = (y - threshold[0]) / (threshold[1] - threshold[0])
        else:
            y = (y + threshold) / (2 * threshold)
    else:
        y = (y - y.min()) / (y.max() - y.min())
    return y