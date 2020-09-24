import json
import numpy as np
import os
import time
import traceback

from twisted.internet.defer import inlineCallbacks

from conductor.parameter import ConductorParameter

class lattice_accelerate(ConductorParameter):
    autostart = False
    priority = 1
    call_in_thread = True
    value = None
    setting = None
    
    def initialize(self, config):
        super(lattice_accelerate, self).initialize(config)

    def update(self):
        experiment = self.server.experiment
        is_end = self.server.is_end 
        parameter_values = self.server.experiment.get('parameter_values')
        
        try:
            if (experiment is not None) and  (not is_end) and ('lattice_accelerate' in parameter_values.get('sequencer.DO_parameters')):
                
                column = 0
                self.setting = {'column': column}
                if type(self.value).__name__ == 'int' or type(self.value).__name__ == 'float':
                    pass
                elif self.value == True:
                    accelerate_parameter_values = parameter_values['lattice']['accelerate']
                    params = accelerate_parameter_values['entry_accelerate']
                    dts = [i.get('dt') for i in params if not i is None]
                    t = sum(dts) if dts else None
                    if t < 10e-6:
                        t = 10e-6 # make sure at least 10e-6 or 1e-6
                    self.value = t
            else:
                self.value = None
        except Exception as e:
            print(e)
            self.value = None
        
Parameter = lattice_accelerate
