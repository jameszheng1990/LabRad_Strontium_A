import json
import numpy as np
import time
import os

from conductor.parameter import ConductorParameter

class RecordPath(ConductorParameter):
    autostart = False
    priority = 2
    record_sequences = {
        # 'image': 'g',
        # 'image_OSGtransfer': 'g',
        # 'image_3P1_excitation': 'g',
        # 'image_3P1_excitation-405': 'g',
        # 'image_v2': 'g',
        # 'image_clock': 'eg',
        # 'image_ft': 'eg',
        # 'image-fast': 'fast-g',
        # 'image-clock-fast': 'fast-eg',
        # 'image-clock-fast-side': 'fast-eg',
        
        'image_test': 'test',
        
        'image_absorption_blue' : 'g_abs_img',
        'image_absorption_red' : 'g_abs_img',
        'image_absorption_red_fast' : 'g_abs_img',
        'image_absorption_lattice' : 'g_abs_img',
        
        'image_fluorescence_lattice': 'g_fluo_img',
        }
    
    data_filename = '{}.ixon'
    nondata_filename = '{}/ixon'
    
    device_name = 'ixon'

    record_settings = {}
    value_type = 'dict'

    def initialize(self, config):
        super(RecordPath, self).initialize(config)
        self.connect_to_labrad()

        # request = {self.device_name: {}}
        # self.cxn.camera.initialize_devices(json.dumps(request))
    
    @property
    def path(self):
        experiment_name = self.server.experiment.get('name')
        shot_number = self.server.experiment.get('shot_number')
        sequence = self.server.parameters.get('sequencer.sequence')
        # previous_sequence = self.server.parameters.get('sequencer.previous_sequence')
        
        path = None
        rel_point_path = None
        self.record_type = None
        
        if (experiment_name is not None) and (sequence is not None):
            point_filename = self.data_filename.format(shot_number)
            rel_point_path = os.path.join(experiment_name, point_filename)
        elif sequence is not None:
            rel_point_path = self.nondata_filename.format(time.strftime('%Y%m%d'))
        
        if np.intersect1d(sequence.value, list(self.record_sequences.keys())):
            intersection = np.intersect1d(sequence.value, list(self.record_sequences.keys()))
            path = rel_point_path
            self.record_type = self.record_sequences[intersection[-1]]

        return path
    
    @path.setter
    def path(self, x):
        pass
    
    def update(self):
        is_end = self.server.is_end
        parameter_values = self.server.experiment.get('parameter_values')
        
        if self.value['roi']:
            self.record_settings['xi'] = self.value.get('roi')[0]
            self.record_settings['xf'] = self.value.get('roi')[1]
            self.record_settings['yi'] = self.value.get('roi')[2]
            self.record_settings['yf'] = self.value.get('roi')[3]
            
        if (self.path is not None) and (not is_end) and ('andor' in parameter_values):
            
            request = {
                self.device_name: {
                    'record': {
                        'kwargs': {
                            'record_path': self.path,
                            'record_type': self.record_type,
                            'record_settings': self.record_settings,
                            },
                        },
                    },
                }
            self.cxn.camera.call_in_thread(json.dumps(request))
            
Parameter = RecordPath
