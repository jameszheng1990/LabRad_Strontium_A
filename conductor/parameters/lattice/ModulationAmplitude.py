import json

from conductor.parameter import ConductorParameter
from update.proxy import UpdateProxy

class ModulationAmplitude(ConductorParameter):
    priority = 1
    autostart = False
    call_in_thread = True
    rf_devicename = 'Lattice_Modulation'  # name in /rf/devices
    value = None
    value_type = 'dict'

    def initialize(self, config):
        super(ModulationAmplitude, self).initialize(config)
        self._update = UpdateProxy('Red-B beatnote')   # Should have the same name as in main GUI client..
        self.connect_to_labrad()
    
    def update(self):
        experiment = self.server.experiment
        # is_first = self.server.is_first
        # is_end = self.server.is_end
        
        try:    
            parameter_values = self.server.experiment['parameter_values']
            if (experiment is not None) and ('ModulationAmplitude' in parameter_values['lattice']) :
                
                # if is_first:
                #     request = {self.rf_devicename: True} # True for ON
                #     response_json = self.cxn.rf.states(json.dumps(request))
                #     response = json.loads(response_json)
                #     self._update.emit({'state2': response[self.rf_devicename]}) 
                
                request = {self.rf_devicename: self.value} # ADD
                response_json = self.cxn.rf.amplitudes(json.dumps(request))
                # self.value = json.loads(response_json)[self.rf_devicename]

        except:
            pass
        
        # if is_end and (self.value is not None):
        #     request = {self.rf_devicename: False} # False for OFF
        #     response_json = self.cxn.rf.states(json.dumps(request))
        #     response = json.loads(response_json)
        #     self._update.emit({'state2': response[self.rf_devicename]})
        #     self.value = None
            
        
Parameter = ModulationAmplitude
