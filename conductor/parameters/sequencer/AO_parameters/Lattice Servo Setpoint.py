import json
import numpy as np
import os
import time
import traceback

from twisted.internet.defer import inlineCallbacks

from conductor.parameter import ConductorParameter

class Lattice_Servo_Setpoint(ConductorParameter):
    autostart = False
    priority = 1
    call_in_thread = True
    value = None
    value_type = 'single'

    def initialize(self, config):
        super(Lattice_Servo_Setpoint, self).initialize(config)

    def update(self):
        experiment = self.server.experiment
        is_end = self.server.is_end 
        parameter_values = self.server.experiment.get('parameter_values')
        # print(parameter_values)
        try:
            if (experiment is not None) and  (not is_end) and ('Lattice Servo Setpoint' in parameter_values.get('sequencer.AO_parameters')) :
                pass
            else:
                self.value = None
        except:
            self.value = None
        
Parameter = Lattice_Servo_Setpoint
