import json
import h5py
import numpy as np
import os
from scipy.optimize import curve_fit
import time

from twisted.internet.reactor import callInThread

from pd.devices.niai.device import NIAI

# TAU = 1e3
def fit_function(x, a, b, TAU):
    return a * np.exp(-x / TAU) + b

class ThorlabsPD(NIAI):
    autostart = True
    niai_servername = 'ni'
    samp_rate = 1e4
    n_samples = 1e4
    verbose = False
    recording = False
    
    data_format = {
        '0': {          # port number, default to 0
            'exp': 0,   # Fit in exp
            # 'bac': 1,   # Background, not used for now
            },
        }

    p0 = [1]
    
    data_path = os.path.join(os.getenv('LABRADDATA'), 'data')

    def record(self, rel_data_path):
        self.recording_name = rel_data_path
        if self.recording:
            raise Exception('already recording')
        callInThread(self.do_record_data, rel_data_path)
    
    def do_record_data(self, rel_data_path):
        self.recording = True
        
        data = {}
        for port, segments in self.data_format.items():
            data[port] = {}
            for label, i in segments.items():
#                data[channel][label] = self.ps.getDataV(channel, 50000, 
#                                                        segmentIndex=i)
                data[port][label] = json.loads(self.niai.Read_PD_AI(port, self.samp_rate, self.n_samples))
        
        self.recording = False
        
        raw_data = data['0']
        raw_sums = {label: sum(raw_counts) for label, raw_counts in raw_data.items()}
        raw_fits = {}

        # for label, raw_counts in raw_data.items():
        #     counts = np.array(raw_counts)
        #     popt, pcov = curve_fit(fit_function, range(len(counts)), counts, p0=self.p0)
        #     raw_fits[label] = popt[0]

        tot_sum = raw_sums['exp']
        # tot_fit = raw_fits['exp']

        processed_data = {
            'tot_sum': tot_sum,
            # 'tot_fit': tot_fit,
            }
         
        abs_data_dir = os.path.join(self.data_path, os.path.dirname(rel_data_path))
        if not os.path.isdir(abs_data_dir):
            os.makedirs(abs_data_dir)
    
        abs_data_path = os.path.join(self.data_path, rel_data_path)
        if self.verbose:
            print("saving processed data to {}".format(abs_data_path))

        json_path = abs_data_path + '.json'
        with open(json_path, 'w') as outfile:
            json.dump(processed_data, outfile, default=lambda x: x.tolist())
        
        h5py_path = abs_data_path + '.hdf5'
        h5f = h5py.File(h5py_path, 'w')
        for k, v in raw_data.items():
            h5f.create_dataset(k, data=np.array(v), compression='gzip')
        h5f.close()
        
        """ temporairly store data """
        if len(self.record_names) > self.max_records:
            oldest_name = self.record_names.popleft()
            if oldest_name not in self.record_names:
                _ = self.records.pop(oldest_name)
        self.record_names.append(rel_data_path)
        self.records[rel_data_path] = processed_data
        
        if rel_data_path:
            message = {'record': {self.name: rel_data_path}}
            self.server._send_update(message)

Device = ThorlabsPD
