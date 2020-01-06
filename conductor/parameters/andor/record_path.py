import json
import numpy as np
import time
import os

from conductor.parameter import ConductorParameter

class RecordPath(ConductorParameter):
    autostart = False
    priority = 2
    record_sequences = {
        'image': 'g',
        'image_OSGtransfer': 'g',
        'image_3P1_excitation': 'g',
        'image_3P1_excitation-405': 'g',
        'image_v2': 'g',
        'image_clock': 'eg',
        'image_ft': 'eg',
        'image-fast': 'fast-g',
        'image-clock-fast': 'fast-eg',
        'image-clock-fast-side': 'fast-eg',
        }

    data_filename = '{}.ikon'
    nondata_filename = '{}/ikon'

    record_settings = {}

    def initialize(self, config):
        super(RecordPath, self).initialize(config)
        self.connect_to_labrad()

        request = {'microscope': {}}
        self.cxn.camera.initialize_devices(json.dumps(request))
    
    @property
    def value(self):
        experiment_name = self.server.experiment.get('name')
        shot_number = self.server.experiment.get('shot_number')
        sequence = self.server.parameters.get('sequencer.sequence')
        previous_sequence = self.server.parameters.get('sequencer.previous_sequence')

        value = None
        rel_point_path = None
        self.record_type = None
        if (experiment_name is not None) and (sequence is not None):
            point_filename = self.data_filename.format(shot_number)
            rel_point_path = os.path.join(experiment_name, point_filename)
        elif sequence is not None:
            rel_point_path = self.nondata_filename.format(time.strftime('%Y%m%d'))
        
        if sequence.loop:
            if np.intersect1d(previous_sequence.value, self.record_sequences.keys()):
                intersection = np.intersect1d(previous_sequence.value, self.record_sequences.keys())
                value = rel_point_path
                self.record_type = self.record_sequences[intersection[-1]]
        elif np.intersect1d(sequence.value, self.record_sequences.keys()):
            intersection = np.intersect1d(sequence.value, self.record_sequences.keys())
            value = rel_point_path
            self.record_type = self.record_sequences[intersection[-1]]

        return value
    
    @value.setter
    def value(self, x):
        pass
    
    def update(self):
        if self.value is not None:
            request = {
                'microscope': {
                    'record': {
                        'kwargs': {
                            'record_path': self.value,
                            'record_type': self.record_type,
                            'record_settings': self.record_settings,
                            },
                        },
                    },
                }
            self.cxn.camera.call_in_thread(json.dumps(request))

#class RecordPath(ConductorParameter):
#    autostart = False
#    priority = 2
#    record_sequences = {
#        'image': 'record_g',
#        'image_OSGtransfer': 'record_g',
#        'image_3P1_excitation': 'record_g',
#        'image_3P1_excitation-405': 'record_g',
#        'image_v2': 'record_g',
#        'image_clock': 'record_eg',
#        'image_ft': 'record_eg',
#        }
#
#    data_filename = '{}.ikon'
#    nondata_filename = '{}/ikon'
#
#    image_settings = {}
#
#    def initialize(self, config):
#        print 'initing andor.record_path'
#        super(RecordPath, self).initialize(config)
#        self.connect_to_labrad()
#        self.cxn.yesr10_andor.select_device('hr_ikon')
#    
#    @property
#    def value(self):
#        experiment_name = self.server.experiment.get('name')
#        shot_number = self.server.experiment.get('shot_number')
#        sequence = self.server.parameters.get('sequencer.sequence')
#        previous_sequence = self.server.parameters.get('sequencer.previous_sequence')
#
#        value = None
#        rel_point_path = None
#        self.recorder_name = None
#        if (experiment_name is not None) and (sequence is not None):
#            point_filename = self.data_filename.format(shot_number)
#            rel_point_path = os.path.join(experiment_name, point_filename)
#        elif sequence is not None:
#            rel_point_path = self.nondata_filename.format(time.strftime('%Y%m%d'))
#
#        
#        if sequence.loop:
#            if np.intersect1d(previous_sequence.value, self.record_sequences.keys()):
#                intersection = np.intersect1d(previous_sequence.value, self.record_sequences.keys())
#                value = rel_point_path
#                self.recorder_name = self.record_sequences[intersection[-1]]
#        elif np.intersect1d(sequence.value, self.record_sequences.keys()):
#            intersection = np.intersect1d(sequence.value, self.record_sequences.keys())
#            value = rel_point_path
#            self.recorder_name = self.record_sequences[intersection[-1]]
#
#        return value
#    
#    @value.setter
#    def value(self, x):
#        pass
#    
#    def update(self):
#        if self.value is not None:
#            print self.value
#            image_settings_json = json.dumps(self.image_settings)
#            self.cxn.yesr10_andor.record(self.value, self.recorder_name, image_settings_json)
#        else:
#            print self.nondata_filename

Parameter = RecordPath
