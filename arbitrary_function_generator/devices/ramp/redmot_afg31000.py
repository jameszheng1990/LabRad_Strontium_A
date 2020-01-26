from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import struct
import os, time, pyvisa

class TFW_Read_Error(Exception):
    """general error for TFW file operations"""
    pass

class AFGWorker(object):
    """
    AWG for red mot frequency modulation, this is written only for Tek AFG31000 series.
    This will output an normalized waveform, and the amplitude and offset can be tuned via the AFG.
    """
    def __init__(self):
        self.afg_name = 'AFG31000'
        self.wave = None
        self.wfm_dir = "C:\\LabRad\\SrData\\Red MOT waveform"
        self.wfm_name = "{}.tfwx"
    
    def log_path(self, wfm_name):
        log_folder = os.path.join(self.wfm_dir, self.afg_name, time.strftime('%Y%m%d'))
        if not os.path.isdir(log_folder):
            os.makedirs(log_folder)
        log_path_full = log_folder + "\\" + self.wfm_name.format(wfm_name)
        return log_path_full
    
    def ExpRamp(self, dt1, dt2, tau, amp, phase = np.pi, f = 20e3, fs = 50e3):
        """This will generate an exponentially decay ramping function, in DAC values.
        
        f: frequency of the ramp, default to 20e3 Hz.
        fs: sample frequency, depends on the AWG, basically will be 500e3 Hz.
        dt1: duration of ramp in full amplitude.
        dt2: duration of ramp in exponentially decaying amplitude.
        tau: time constant in exponentially decay.
        amp: max amplitude of ramp.
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
        
        t = np.linspace(0, self.dt1 + self.dt2, int(self.fs))
        
        self.wave1 = self.amp * (signal.sawtooth(2 * np.pi * int(self.f) * t * (t < self.dt1) + self.phase, self.width) - 1)
        
        self.amp2 = self.amp * np.exp(-(t - self.dt1)/(1 * self.tau))
        self.wave2 = self.amp2 * (signal.sawtooth(2 * np.pi * int(self.f) * t * (t> self.dt1) + self.phase, self.width) - 1)
        
        self.wave = self.wave1 + self.wave2

        return t, self.wave
    
    def plotter(self, x, y):
        plt.cla()
        plt.plot(x, y)
    
    def read_tfw(self, target):
        """open target file and return numpy array of digital dac values"""
        with open(target, 'rb') as f:
            h = f.read(512)
            if len(h) != 512:
                raise TFW_Read_Error('file too small')
            m = struct.unpack_from('>9s14x3I', h)
            print(m)
            # if m[0] != b'TEKAFG30K':
            #     raise TFW_Read_Error('missing TFW identifier "TEKAFG30K"') # TODO
            # if m[1] != 20191229:
            #     raise TFW_Read_Error('version not 20191229') # TODO
            samples = m[2]
            dac_values = np.fromfile(f, dtype='>u2', count=samples)
        print('{}.tfw readed.'.format(self.wfm_name))
        return dac_values
    
    def normal_vector(self, vector, ymax=pow(2, 16)-1, ymin=0, dtype='>u2'):
        """normalize vector to integer values between ymin and ymax"""
        if type(vector) == 'list':
            vector = np.asarray(vector)
        m = (ymax - ymin) / (vector.max() - vector.min())
        b = ymax - (m * vector.max())
        n = m * vector + b
        n = np.array(n, dtype=dtype)
        return n
    
    def envelope_vector(self, dac_values):
        """return envelope vector from dac_values"""
        # envelope is maximum 206 uint8 min-max pairs
        n = np.array(dac_values >> 6, dtype=np.uint8)
        if len(dac_values) <= 206:
            upper = n
            lower = n
        else:
            segments = np.array_split(n, 206)
            upper = np.zeros(206, dtype=np.uint8)
            lower = np.zeros(206, dtype=np.uint8)
            for i, s in enumerate(segments):
                upper[i] = s.max()
                lower[i] = s.min()
        c = np.vstack((lower, upper)).reshape(-1, order='F')
        return c
    
    def write_tfw(self, wfm_name, dac_values):
        """write target file in TFW format with dac_values"""
        dac_norm_array = self.normal_vector(dac_values)
        d = np.array((dac_norm_array & 0x3fff), dtype='>u2') # cast and mask, 0x3fff for 14 bit.
        samples = len(d)
        # an envelope vector is used for arb plot on AFG
        envelope = self.envelope_vector(d)
        header = bytearray(512)
        struct.pack_into('>9s6x3I',    # format
                         header,        # buffer
                         0,             # offset
                         b'TEKAFG30K', # magic bytes
                         20191229,      # version
                         samples,       # length
                         1)             # envelope flag
        header[28:28+len(envelope)] = memoryview(envelope)
        with open(self.log_path(wfm_name), 'wb') as f:
            f.write(header)
            f.write(memoryview(d))
        print('{}.tfw with envelope written.'.format(wfm_name))

    def write_tfw_no_envelope(self, wfm_name, dac_values):
        """write target file in TFW format with dac_values omitting envelope"""
        dac_norm_array = self.normal_vector(dac_values)
        d = np.array((dac_norm_array & 0xFFFF), dtype='>u2') # cast and mask, 0x3fff for 14 bit.
        print(d)
        samples = len(d)
        header = bytearray(512)
        struct.pack_into('>9s14x3I',    # format
                         header,        # buffer
                         0,             # offset
                         b'TEKAFG30K', # magic bytes
                         20191229,      # version
                         samples,       # length
                         0)             # envelope flag
        with open(self.log_path(wfm_name), 'wb') as f:
            f.write(header)
            f.write(memoryview(d))
        print('{}.tfw without envelope written.'.format(wfm_name))
        
    def write_to_AFG_user(self):
        visa_address = 'USB0::0x0699::0x0358::C011390::INSTR'
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(visa_address)
        inst

###############################################################################

w = AFGWorker()

# t, wfm = w.ExpRamp(0.1, 0.25, 0.1, 1)
# w.plotter(t, wfm)
# w.write_tfw_no_envelope("RedMOT_A", wfm)

target = "C:\\LabRad\\SrData\\Red MOT waveform\\AFG31000\\20200106\\Waveform15.tfw"
a = w.read_tfw(target)
