import json
import numpy as np
import os
import time
import traceback

from twisted.internet.defer import inlineCallbacks

from conductor.parameter import ConductorParameter

class blue_mot(ConductorParameter):
    autostart = False
    priority = 1
    call_in_thread = True
    value = None
    
    def initialize(self, config):
        super(blue_mot, self).initialize(config)

    def update(self):
        experiment = self.server.experiment
        is_end = self.server.is_end 
        parameter_values = self.server.experiment.get('parameter_values') 
        
        try:
            if (experiment is not None) and  (not is_end) and ('blue_mot' in parameter_values.get('sequencer.DO_parameters') ) :
                column = 1
                self.setting = {'column': column}
                
            else:
                self.value = None
        except:
            self.value = None
        
Parameter = blue_mot
