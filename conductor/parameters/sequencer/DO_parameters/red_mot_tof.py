import json
import numpy as np
import os
import time
import traceback

from twisted.internet.defer import inlineCallbacks

from conductor.parameter import ConductorParameter

class red_mot_tof(ConductorParameter):
    autostart = False
    priority = 1
    call_in_thread = True
    value = None
    
    def initialize(self, config):
        super(red_mot_tof, self).initialize(config)

    def update(self):
        experiment = self.server.experiment
        is_end = self.server.is_end 
        try:    
            parameter_values = self.server.experiment['parameter_values']
            if (experiment is not None) and  (not is_end) and ('red_mot_tof' in parameter_values['sequencer.DO_parameters']) :
                pass
            else:
                self.value = None
        except:
            self.value = None

Parameter = red_mot_tof
