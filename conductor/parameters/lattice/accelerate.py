import json

from conductor.parameter import ConductorParameter
from update.proxy import UpdateProxy

class accelerate(ConductorParameter):
    priority = 1
    autostart = False
    call_in_thread = True
    rf_devicename = 'MoglabsXRF_813C'  # name in /rf/devices
    value = None
    value_type = 'dict'

    def initialize(self, config):
        super(accelerate, self).initialize(config)
        # self._update = UpdateProxy('Moglabs_XRF')   # Should have the same name as in main GUI client..
        self.connect_to_labrad()
    
    def update(self):
        experiment = self.server.experiment
        is_end = self.server.is_end
        # is_first = self.server.is_first
        
        try:    
            parameter_values = self.server.experiment.get('parameter_values')
            if (not is_end) and (experiment is not None) and ('accelerate' in parameter_values['lattice']) :
                
                request = {self.rf_devicename: self.value}
                self.cxn.rf.tables(json.dumps(request))
                # self.value = json.loads(response_json)[self.rf_devicename]
        except:
            pass
        # if is_end and (self.value is not None):
        #     request = {self.rf_devicename: False} # False for OFF
        #     response_json = self.cxn.rf.states(json.dumps(request))
        #     response = json.loads(response_json)
        #     self._update.emit({'state2': response[self.rf_devicename]})
        #     self.value = None
            
        
Parameter = accelerate
