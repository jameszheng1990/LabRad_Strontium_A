import json

import pyvisa

from conductor.parameter import ConductorParameter


class FrequencyModulation(ConductorParameter):
    priority = 1
    autostart = True
    call_in_thread = True
    afg_devicename = 'FM'
    
    waveforms = {
        'red_mot_87': {'A':{'wfm': 'U:/RedMOT_87_A.tfw', 'scale': 150, 'source': 1}, 
                       'B':{'wfm': 'U:/RedMOT_87_B.tfw', 'scale': 350, 'source': 2}},
        
        'red_mot_88': {'A':{'wfm': None,                 'scale':None, 'source': 1},
                       'B':{'wfm': 'U:/RedMOT_88_B.tfw', 'scale': 500, 'source': 2}},
        }

    def initialize(self, config):
        super(FrequencyModulation, self).initialize(config)
        self.connect_to_labrad()
    
    def update(self):
        sequence = self.server._get_parameter_value('sequencer.sequence')
        previous_sequence = self.server._get_parameter_value('sequencer.previous_sequence')
        is_end = self.server.is_end
        is_first = self.server.is_first
        
        if (is_first) and (not is_end):
            for subsequence, req in self.waveforms.items():
                if subsequence in sequence:
                    requestA = {self.afg_devicename: req['A']}
                    self.cxn.afg.waveforms(json.dumps(requestA))
                    self.cxn.afg.scales(json.dumps(requestA))
                    
                    requestB = {self.afg_devicename: req['B']}
                    self.cxn.afg.waveforms(json.dumps(requestB))
                    self.cxn.afg.scales(json.dumps(requestB))
                    
        if (sequence != previous_sequence):
            self.cxn.afg.run(json.dumps({self.afg_devicename: None}))

Parameter = FrequencyModulation
