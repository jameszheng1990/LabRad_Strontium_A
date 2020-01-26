import json
import numpy as np
import time
import os

from conductor.parameter import ConductorParameter

class RecordPath(ConductorParameter):
    autostart = False
    priority = 2
    record_sequences = {  # sequence : record_type
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
        
        'image_absorption_blue' : 'abs_img',
        'image_absorption_red' : 'abs_img',
        'image_absorption_red_fast' : 'abs_img',
        'image_fluorescence_blue' : 'fluo_img',
        'image_fluorescence_red' : 'fluo_img',
        'image_fluorescence_red_fast' : 'fluo_img',
        'image_fluorescence_red_swap' : 'fluo_img',
        }

    data_filename = '{}.tcam'
    nondata_filename = '{}/tcam'
    
    device_name = 'TOFtcam'

    record_settings = {}

    def initialize(self, config):
        super(RecordPath, self).initialize(config)
        self.connect_to_labrad()

        request = {self.device_name: {}}
        self.cxn.camera.initialize_devices(json.dumps(request))
    
    @property
    def value(self):
        experiment_name = self.server.experiment.get('name')
        shot_number = self.server.experiment.get('shot_number')
        sequence = self.server.parameters.get('sequencer.sequence')
        # previous_sequence = self.server.parameters.get('sequencer.previous_sequence')

        value = None
        rel_point_path = None
        self.record_type = None
        if (experiment_name is not None) and (sequence is not None):
            point_filename = self.data_filename.format(shot_number)
            rel_point_path = os.path.join(experiment_name, point_filename)
        elif sequence is not None:
            rel_point_path = self.nondata_filename.format(time.strftime('%Y%m%d'))
        
        if np.intersect1d(sequence.value, list(self.record_sequences.keys())):
            intersection = np.intersect1d(sequence.value, list(self.record_sequences.keys()))
            value = rel_point_path
            self.record_type = self.record_sequences[intersection[-1]]
        
        return value
    
    @value.setter
    def value(self, x):
        pass
    
    def update(self):
        
        shot_number = self.server.experiment.get('shot_number')
        is_end = self.server.is_end
        
        if (self.value is not None) and (shot_number is not None) and (not is_end):
            
            config_file = {
                    'bit_depth' : 8,
                    'camera' : 'ThorCam FS',
                    'roi_shape' : [1280, 1024],
                    'roi_pos' : [0, 0],
                    'exposure' : 10, # in ms
                    'frametime' : 40.0, # in ms, wait time between shot to shot > exposure time + frame time
                    'timeout' : 120, # in s
                    'delay'   : 5, # in us
                    'buffer_size': 3,  # store 3 images in memory
                    }
            
            request1 = {
                self.device_name : {
                        'record_type': self.record_type,
                        'config_file': config_file,
                        }
                    }
            self.cxn.camera.config_tcam(json.dumps(request1))
            
            request2 = {
                self.device_name: {
                    'record': {
                        'kwargs': {
                            'record_path': self.value,
                            'record_type': self.record_type,
                            'record_settings': self.record_settings,
                            },
                        },
                    },
                }
            self.cxn.camera.call_in_thread(json.dumps(request2))
            print('Thorlabs camera recorded, shot#{}.'.format(shot_number))

Parameter = RecordPath
