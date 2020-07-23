import json
from update.proxy import UpdateProxy
from conductor.parameter import ConductorParameter
import time


class FrequencyModulation(ConductorParameter):
    priority = 9
    autostart = True
    call_in_thread = False
    afg_devicename = 'FM'
    rf_devicename_A = 'MoglabsARF_689A'
    rf_devicename_B = 'MoglabsARF_689B'
    value_type = 'dict'
    
    # Scales are set to 100%, so max output is +- 1V.
    default_waveforms = {
        'red_mot_87': {'A':{'wfm': 'U:/red_mot/RM87A.tfw', 'scale': 100, 'source': 1, 'fm_gain': 4.19e6}, 
                       'B':{'wfm': 'U:/red_mot/RM88B.tfw', 'scale': 100, 'source': 2, 'fm_gain': 0.7e6}},
                      
        'red_mot_88': {'A':{'wfm': 'U:/red_mot/RM88B.tfw', 'scale': 100, 'source': 1, 'fm_gain': 2.5e6},
                       'B':{'wfm': 'U:/red_mot/RM88B.tfw', 'scale': 100, 'source': 2, 'fm_gain': 2.5e6}},
        
        'red_mot_87_fast':
                      {'A':{'wfm': 'U:/red_mot/RM87A.tfw', 'scale': 100, 'source': 1, 'fm_gain': 4.19e6},
                       'B':{'wfm': 'U:/red_mot/RM87B.tfw', 'scale': 100, 'source': 2, 'fm_gain': 0.7e6}},
        
        'red_mot_88_fast': 
                      {'A':{'wfm': 'U:/red_mot/RM88B.tfw', 'scale': 100, 'source': 1, 'fm_gain': 2.5e6},
                       'B':{'wfm': 'U:/red_mot/RM88B.tfw', 'scale': 100, 'source': 2, 'fm_gain': 2.5e6}},
                      
        'in_lattice_cooling_87':
                      {'A':{'wfm': 'U:/in_lattice_cooling/ILC87A.tfw', 'scale': 100, 'source': 1, 'fm_gain': 4.19e6},
                       'B':{'wfm': 'U:/in_lattice_cooling/ILC87B.tfw', 'scale': 100, 'source': 2, 'fm_gain': 0.7e6}},
    
        'in_lattice_cooling_88':
                      {'A':{'wfm': 'U:/in_lattice_cooling/ILC88B_10mV.tfw', 'scale': 100, 'source': 1, 'fm_gain': 2.5e6},
                       'B':{'wfm': 'U:/in_lattice_cooling/ILC88B_10mV.tfw', 'scale': 100, 'source': 2, 'fm_gain': 2.59e6}},    
        }
    
    waveforms = {}
        
    def initialize(self, config):
        super(FrequencyModulation, self).initialize(config)
        self._update_afg = UpdateProxy('Red AFG')
        self._update_rf = UpdateProxy('Moglabs_ARF')   # Should have the same name as in GUI client.
        self.connect_to_labrad()
    
    def update(self):
        sequence = self.server._get_parameter_value('sequencer.sequence')
        # previous_sequence = self.server._get_parameter_value('sequencer.previous_sequence')
        is_first = self.server.is_first
        is_end = self.server.is_end
        experiment = self.server.experiment
        
        if is_first and experiment:
            self.waveforms = self.default_waveforms.copy()
            if self.value is not None: 
            # If self.value is not None, update self.waveforms, default waveform remains unchanged.
            # This allows you to change, ie. fm_gain, from experiment scripts
                for key1, value1 in self.value.items():
                    if key1 in self.waveforms.keys():
                        for key2, value2 in value1.items():
                            self.waveforms[key1][key2].update(value1[key2])
            
            request = {}
            element = 1
            for subsequence in sequence:
                if subsequence in list(self.waveforms.keys()):
                    request[element] = self.waveforms[subsequence]
                    element += 1
            
            if request: 
                # self.cxn.afg.new(json.dumps({self.afg_devicename: True}))
                # self.cxn.afg.reset(json.dumps({self.afg_devicename: True}))
                if self.value is None:
                    self.value = request
                    
                # set up the sequence list
                self.cxn.afg.sequences(json.dumps({self.afg_devicename: request}))
                
                # update scale
                scale = request[1]['A']['scale'] # element should be at least 1
                scale_request1 = {self.afg_devicename: {'source':1, 'scale': scale}}
                scale_request2 = {self.afg_devicename: {'source':2, 'scale': scale}}
                self.cxn.afg.scales(json.dumps(scale_request1))
                self.cxn.afg.scales(json.dumps(scale_request2))
                self._update_afg.emit({'scale1': scale})
                self._update_afg.emit({'scale1': scale})
                
                # set afg stop and run
                self.cxn.afg.stop(json.dumps({self.afg_devicename: True}))
                self.cxn.afg.run(json.dumps({self.afg_devicename: True}))
                
                # update rf fm_gain, this should come from RedMOT sequence in principle..
                fm_gain1 = request[1]['A']['fm_gain']
                fm_gain2 = request[1]['B']['fm_gain']
                rf_request1 = {self.rf_devicename_A: fm_gain1}
                rf_request2 = {self.rf_devicename_B: fm_gain2}
                self.cxn.rf.fm_gains(json.dumps(rf_request1))
                self.cxn.rf.fm_gains(json.dumps(rf_request2))
                self._update_rf.emit({'fm_gain1': fm_gain1})
                self._update_rf.emit({'fm_gain2': fm_gain2})
                
        elif is_end and self.value is not None:
            self.value = None
        
Parameter = FrequencyModulation
