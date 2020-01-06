import json
import numpy as np
import os
import time
import traceback

from twisted.internet.defer import inlineCallbacks

from conductor.parameter import ConductorParameter

class Recorder(ConductorParameter):
    autostart = False  #You need to reload this in your experiment to get it started.
    priority = 9  # start with smaller priority first..
    data_filename = '{}.pd'
    nondata_filename = '{}/pd'
    pd_name = 'ThorlabsPD'  # Device name

    record_sequences = [
        'pd-v',
        '3p2_probe',
        ]

    def initialize(self, config):
        super(Recorder, self).initialize(config)
        self.connect_to_labrad()
        request = {self.pd_name: {}}
        self.cxn.pd.initialize_devices(json.dumps(request))

    @property
    def value(self):
        try:
            experiment_name = self.server.experiment.get('name')
            shot_number = self.server.experiment.get('shot_number')
            sequence = self.server.parameters.get('sequencer.sequence')
            previous_sequence = self.server.parameters.get('sequencer.previous_sequence')
            
            value = None
            if (experiment_name is not None) and (sequence is not None):
                point_filename = self.data_filename.format(shot_number)
                rel_point_path = os.path.join(experiment_name, point_filename)
            elif sequence is not None:
                rel_point_path = self.nondata_filename.format(time.strftime('%Y%m%d'))
            
            # if sequence.loop:
            #     if np.intersect1d(previous_sequence.value, self.record_sequences):
            #         value = rel_point_path
            # elif np.intersect1d(sequence.value, self.record_sequences):
            #     value = rel_point_path
    
            if np.intersect1d(sequence.value, self.record_sequences):
                value = rel_point_path
                
            return value
        except:
            print('oops!')
            traceback.print_exc()
            raise
        
    @value.setter
    def value(self, x):
        pass
    
    def update(self):
        shot_number = self.server.experiment.get('shot_number')
        is_end = self.server.is_end
        if self.value is not None and shot_number is not None and not is_end:
            request = {self.pd_name: self.value}
            self.cxn.pd.record(json.dumps(request))
            print('PD data recorded, shot#{}.'.format(shot_number))

Parameter = Recorder