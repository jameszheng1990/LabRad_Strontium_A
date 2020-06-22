import json
import numpy as np
import os
import time
import traceback

from twisted.internet.defer import inlineCallbacks

from conductor.parameter import ConductorParameter

class lattice_hold(ConductorParameter):
    autostart = False
    priority = 1
    call_in_thread = True
    value = None
    
    def initialize(self, config):
        super(lattice_hold, self).initialize(config)

    def update(self):
        experiment = self.server.experiment
        is_end = self.server.is_end 
        try:    
            parameter_values = self.server.experiment['parameter_values']
            if (experiment is not None) and  (not is_end) and ('lattice_hold' in parameter_values['sequencer.DO_parameters']) :
                pass
            else:
                self.value = None
        except:
            self.value = None

Parameter = lattice_hold
