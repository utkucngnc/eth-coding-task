class Config:
    # Bandpass Filter Parameters
    BPF_Param = {
        'lowcut': 5,
        'highcut': 20,
        'order': 1
    }

    # Derivative Filter Parameters
    SavGol_Param = {
        'p': 3,
        'w': 5,
        'm': 1
    }