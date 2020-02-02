import json

import pyvisa

from conductor.parameter import ConductorParameter


class FrequencyModulation(ConductorParameter):
    priority = 1
    autostart = True
    call_in_thread = True
    afg_devicename = 'A_FM'
    
    waveforms = {
        'red_mot_88': 'U:/RedMOT_88_A.tfw',
        }

    def initialize(self, config):
        super(FrequencyModulation, self).initialize(config)
        self.connect_to_labrad()
    
    def update(self):
        sequence = self.server._get_parameter_value('sequencer.sequence')
        
        for subsequence, waveform in self.waveforms.items():
            if subsequence in sequence:
                request = {self.afg_devicename: waveform}
                self.cxn.afg.waveforms(json.dumps(request))
            
        self.cxn.afg.run(json.dumps({self.afg_devicename: None}))

Parameter = FrequencyModulation
