class Config:
    # Activities
    activities = {
        0: 'rest inital',
        1: 'Sustained grip challenge stand',
        2: 'rest after grip',
        3: 'Mental AR stand',
        4: 'rest after mental',
        5: 'Cold Pressor stand',
        6: 'rest after cold pres',
        7: 'ValsalvaManeuverstand',
        8: 'rest after Valsalva',
        9: 'Exercise',
        10: 'rest after exert'
    }

    ecg_filter_type = 'ema'

    class ECG_Param:
        # Bandpass Filter Parameters
        BPF_Param = {
            'lowcut': 10,
            'highcut': 30,
            'order': 1
        }

        # Derivative Filter Parameters
        SavGol_Param = {
            'p': 4,
            'w': 21,
            'm': 1
        }

        # Moving Average Filter Parameters
        MA_Param = {
            'window_ms': 5,
            'rolling_type': 'mean',
            'win_type': 'triang'
        }

        # Exponential Moving Average Filter Parameters
        EMA_Param = {
            'span': 10 # alpha = 2 / (span + 1) [Etemadi+11]
        }
    
    class BCG_Param:
        # Bandpass Filter Parameters
        BPF_Param = {
            'lowcut': 10,
            'highcut': 30,
            'order': 1
        }

        # Derivative Filter Parameters
        SavGol_Param = {
            'p': 4,
            'w': 21,
            'm': 1
        }

        # Exponential Moving Average Filter Parameters
        EMA_Param = {
            'span': 10 # alpha = 2 / (span + 1) [Etemadi+11]
        }

        