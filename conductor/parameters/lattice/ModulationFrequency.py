import json

from conductor.parameter import ConductorParameter
from update.proxy import UpdateProxy

class Frequency(ConductorParameter):
    priority = 1
    autostart = False
    call_in_thread = True
    rf_devicename = 'Lattice_Modulation'  # name in /rf/devices
    value = None

    def initialize(self, config):
        super(Frequency, self).initialize(config)
        # self._update = UpdateProxy('')   # Should have the same name as in GUI client..
        self.connect_to_labrad()
    
    def update(self):
        experiment = self.server.experiment
        
        try:    
            parameter_values = self.server.experiment['parameter_values']
            if (experiment is not None) and ('lattice.ModulationFrequency' in parameter_values) :
                request = {self.rf_devicename: self.value} # ADD
                response_json = self.cxn.rf.frequencies(json.dumps(request))
                self.value = json.loads(response_json)[self.rf_devicename]
                # self._update.emit({'frequency': self.value})  # Will update value on current controller.. in principle..
        except:
            pass
        
Parameter = Frequency
