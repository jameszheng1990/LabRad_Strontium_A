import json
import numpy as np
import os
import time
import traceback

from twisted.internet.defer import inlineCallbacks

from conductor.parameter import ConductorParameter

class image_raw(ConductorParameter):
    autostart = False
    priority = 1
    call_in_thread = True
    value = None
    
    def initialize(self, config):
        super(image_raw, self).initialize(config)

    def update(self):
        experiment = self.server.experiment
        is_end = self.server.is_end 
        parameter_values = self.server.experiment.get('parameter_values') 
        
        try:
            if (experiment is not None) and  (not is_end) and ('image_raw' in parameter_values.get('sequencer.DO_parameters') ) :
                column = 2
                self.value = [self.value, column]
                
            else:
                self.value = None
        except:
            self.value = None
        
Parameter = image_raw
