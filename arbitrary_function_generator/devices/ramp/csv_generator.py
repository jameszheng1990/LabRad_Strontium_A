import csv
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import struct
import os, time, pyvisa

class AFGWorker(object):
    """
    AWG for red mot frequency modulation, this is written only for Tek AFG31000 series.
    This will output an normalized waveform, and the amplitude and offset can be tuned via the AFG.
    """
    def __init__(self):
        self.afg_name = 'AFG31000'
        self.wave = None
        self.wfm_dir = "C:\\LabRad\\SrData\\Red MOT waveform"
        self.wfm_name = "{}.csv"
    
    def log_path(self, wfm_name):
        log_folder = os.path.join(self.wfm_dir, self.afg_name, time.strftime('%Y%m%d'))
        if not os.path.isdir(log_folder):
            os.makedirs(log_folder)
        log_path_full = log_folder + "\\" + self.wfm_name.format(wfm_name)
        return log_path_full
    
    def ExpRamp(self, dt1, dt2, tau, amp, phase = np.pi, f = 20e3, fs = 1e6):
        """This will generate an exponentially decay ramp waveform in DAC values.
        
        f: frequency of the ramp, default to 20e3 Hz.
        fs: sample frequency, depends on the AWG, basically will be 500e3 Hz.
        dt1: duration of ramp in full amplitude.
        dt2: duration of ramp in exponentially decaying amplitude.
        tau: time constant in exponentially decay.
        amp: amplitude of ramp.
        phase: phase of ramp, default to np.pi, such that it start at zero, and ramps negative.
        """
        self.f = f
        self.fs = fs
        self.dt1 = dt1
        self.dt2 = dt2
        self.tau = tau
        self.amp = amp/2
        self.phase = phase
        
        self.width = 0.5 # width = 0.5 means symmetric triangle ramp.
        
        t = np.linspace(0, self.dt1 + self.dt2, int((self.dt1 + self.dt2)*self.fs))
        
        wave1 = self.amp * (signal.sawtooth(2 * np.pi * int(self.f) * t * (t < self.dt1) + self.phase, self.width) - 1)
        
        self.amp2 = self.amp * np.exp(-(t - self.dt1)/(1 * self.tau))
        wave2 = self.amp2 * (signal.sawtooth(2 * np.pi * int(self.f) * t * (t> self.dt1) + self.phase, self.width) - 1)
        
        wave = wave1 + wave2
        
        return t, wave

    def SawTooth(self, width, phase = 0, amp = 0.5, offset = 0.5, dt = 50e-6, f = 20e3, fs = 5*20e5):
        """This will generate a saw tooth ramp waveform in DAC values.
        
        f: frequency of the ramp, default to 20e3 Hz.
        fs: sample frequency, depends on the AWG, basically will be 20e5 Hz.
        dt: duration of ramp, default to 100 us.
        amp: amplitude of ramp, default to 1 V.
        phase: phase of ramp.
        width: 1 for rising ramp, 0 for falling ramp, 0.5 for triangle ramp. 
        """
        t = np.linspace(0, dt, int(dt*fs))
        wave = amp* (signal.sawtooth(2*np.pi*int(f)*t + phase, width) )+ offset

        return t, wave
    
    def plotter(self, x, y):
        plt.cla()
        plt.plot(x, y)
        
    def write_csv(self, wfm_name, time, dac):
        header = ['TIME', 'ARB']
        rows = []
        num_rows = len(dac)
        for i in range(num_rows):
            rows.append([time[i], dac[i]])
        with open(self.log_path(wfm_name), 'wt', newline = '') as file:
            writer = csv.writer(file, delimiter = ',')
            writer.writerow(i for i in header) # write header first
            for i in range(num_rows):
                writer.writerow(j for j in rows[i])

w=AFGWorker()

# t, wfm = w.ExpRamp(0.1, 0.25, 0.1, 1)
# w.plotter(t, wfm)
# w.write_csv("RedMOT_A", t, wfm)

t2, wfm2 = w.SawTooth(1)
w.plotter(t2, wfm2)
w.write_csv("SWAP_MOT_rise", t2, wfm2)

t3, wfm3 = w.SawTooth(0, offset = -0.5)
w.plotter(t3, wfm3)
w.write_csv("SWAP_MOT_fall", t3, wfm3)
