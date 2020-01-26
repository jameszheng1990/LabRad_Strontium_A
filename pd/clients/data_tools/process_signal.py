import numpy as np
import h5py
import os

from scipy import optimize

def process_signal(sample_rate, rel_data_path, record_type):
    data_dir = os.path.join(os.getenv('LABRADDATA'),'data')
    signal_path = os.path.join(data_dir, rel_data_path) + '.hdf5'
    signals = {}
    signals_h5 = h5py.File(signal_path, "r")
    for key in signals_h5:
        signals[key] = np.array(signals_h5[key], dtype='float64')
    signals_h5.close()
    if record_type == 'loading_rate': 
        return process_loading_rate(sample_rate, signals)

def fit_decay(t, a, R):
    return a*np.exp(-R*t) # R for loss rate
    
def fit_loading(t, L, R):
    return L/R*(1-np.exp(-R*t))

def process_loading_rate(sample_rate, signals):
    """ process signals of loading rate """
    
    volt_to_number = 5e7/0.1  # rough number per volt fluorescence, uncalibrated.
    
    exp = np.array(signals['exp'], dtype='f')
    
    decay = exp[5000:]
    load = exp[:5000]
    x1 = np.linspace(0, len(decay)/sample_rate, len(decay))
    x2 = np.linspace(0, len(load)/sample_rate, len(load))
    
    p1 = [max(decay), 0.05*max(x1)]
    popt1, pcov1 = optimize.curve_fit(fit_decay, x1, decay, p0=p1)
    fit_R = popt1[1]
    
    p2 = [0.5*max(x1), fit_R]
    popt2, pcov2 = optimize.curve_fit(fit_loading, x2, load, p0=p2)
    
    loading_rate = popt2[0]
    loss_rate = popt2[1]
    
    return loading_rate, loss_rate, volt_to_number