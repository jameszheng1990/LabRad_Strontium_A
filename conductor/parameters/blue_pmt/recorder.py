import json
import numpy as np
import os
import time
import traceback

from twisted.internet.defer import inlineCallbacks

from conductor.parameter import ConductorParameter

class Recorder(ConductorParameter):
    autostart = False
    priority = 2
    data_filename = '{}.blue_pmt'
    nondata_filename = '{}/blue_pmt'
    pmt_name = 'BluePMT'

    record_sequences = [
        'pmt_lattice',
        ]

    def initialize(self, config):
        super(Recorder, self).initialize(config)
        self.connect_to_labrad()
        request = {self.pmt_name: {}}
        self.cxn.pmt.initialize_devices(json.dumps(request))

    @property
    def value(self):
        # try:
            experiment_name = self.server.experiment.get('name')
            shot_number = self.server.experiment.get('shot_number')
            sequence = self.server.parameters.get('sequencer.sequence')
    
            value = None
            if (experiment_name is not None) and (sequence.value is not None):
                point_filename = self.data_filename.format(shot_number)
                rel_point_path = os.path.join(experiment_name, point_filename)
                if np.intersect1d(sequence.value, self.record_sequences):
                    value = rel_point_path
                
            # elif sequence is not None:
            #     rel_point_path = self.nondata_filename.format(time.strftime('%Y%m%d'))
                
            #     if np.intersect1d(sequence.value, self.record_sequences):
            #         value = rel_point_path
            return value
        # except:
        #     print('oops!')
        #     traceback.print_exc()
        #     raise
        
    @value.setter
    def value(self, x):
        pass
    
    def update(self):
        is_end = self.server.is_end
        parameter_values = self.server.experiment.get('parameter_values')
        
        if (self.value is not None) and (not is_end) and ('blue_pmt.recorder' in parameter_values) :
            request = {self.pmt_name: self.value}
            self.cxn.pmt.record(json.dumps(request))

Parameter = Recorder
