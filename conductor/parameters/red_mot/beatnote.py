import json
import pyvisa

from conductor.parameter import ConductorParameter
from update.proxy import UpdateProxy

class Frequency(ConductorParameter):
    priority = 1
    autostart = False
    call_in_thread = True
    rf_devicename = 'Beatnote_689'
    value = None

    def initialize(self, config):
        super(Frequency, self).initialize(config)
        self._update = UpdateProxy('Red-B beatnote')   # Should have the same name as in GUI client..
        self.connect_to_labrad()
    
    def update(self):
        is_end = self.server.is_end
        
        try:    
            parameter_values = self.server.experiment['parameter_values']
            if (not is_end) and ('red_mot.beatnote' in parameter_values) :
                request = {self.rf_devicename: self.value} # ADD
                response_json = self.cxn.rf.frequencies(json.dumps(request))
                self.value = json.loads(response_json)[self.rf_devicename]
                self._update.emit({'frequency': self.value})  # Will update value on client.. in principle..
        except:
            pass
        
Parameter = Frequency
