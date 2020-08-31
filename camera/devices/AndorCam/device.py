import os
import h5py
import json
from device_server.device import DefaultDevice

class AndorCam(DefaultDevice):

    _data_directory = os.path.join(os.getenv('LABRADDATA'), 'data')
    _compression = 'gzip'
    _compression_level = 4
    
    def initialize(self, config):
        # super(AndorCam, self).initialize(config)
        # self.connect_to_labrad()
        """ To be implemented by child class """
        
    def config(self, record_path = None, record_type = None, record_setting={}):
        """ To be implemented by child class """
        
    def record(self, record_path = None, record_type = None, record_setting={}):
        """ To be implemented by child class """
    
    def _save(self, images, record_path):
        data_path = os.path.join(self._data_directory, record_path + '.hdf5')
        data_directory = os.path.dirname(data_path)
        if not os.path.isdir(data_directory):
            os.makedirs(data_directory)

        h5f = h5py.File(data_path, "w")
        for image in images:
            h5f.create_dataset(image, data=images[image], 
                    compression=self._compression, 
                    compression_opts=self._compression_level)
        h5f.close()
        
    def _send_update(self, record_path, record_type, record_settings):
        signal = {
            self.name: {
                'record_path': record_path,
                'record_type': record_type,
                'record_settings': record_settings,
                },
            }
        self.server.update(json.dumps(signal))
