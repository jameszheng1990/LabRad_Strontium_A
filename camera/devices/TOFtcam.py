from camera.devices.ThorCam.device import TCam
from thorlabs_cam.proxy import TCamProxy
import json, time

class TOFtcam(TCam):
    tcam_servername = 'tcam'
    
    compression = 'gzip'
    compression_level = 0
    
    def config(self, record_type=None, config_file={}):
        if record_type is None:
            return
        
        self.buffer_size = config_file['buffer_size']
        self.roi_shape = config_file['roi_shape']
        
        tcam_server = self.cxn[self.tcam_servername]
        tcam_proxy = TCamProxy(tcam_server)
        self.tcam = tcam_proxy.TCamManager()

        # close if acquiring
        self.tcam.Close()
        
        if (record_type == 'abs_img') or (record_type == 'fluo_img'):   # Simple absorption imaging
            self.tcam.Open(config_file)
            self.tcam.Set_Trigger_Mode() # Set mode to External trigger with rising edge (default = 2)
    
    def record(self, record_path=None, record_type=None, record_settings={}):
        if record_path is None:
            return
        
        if record_type == 'abs_img':   # Simple absorption imaging
            # Take three images, one ('image') with atoms, one ('bright') without atoms, and 'dark' without probe light.            
            for i in range(3):
                self.tcam.Start_Single_Capture()

            images = {key: self.tcam.Get_Image(i).reshape(self.roi_shape[1], self.roi_shape[0])
                      for i, key in enumerate(["image", "bright", "dark"])}
            
            self._save(images, record_path)
            self._send_update(record_path, record_type)
        
        if record_type == 'fluo_img':   # Simple absorption imaging
            # Take one image with blue beam on.
            for i in range(2):
                self.tcam.Start_Single_Capture()

            images = {key: self.tcam.Get_Image(i).reshape(self.roi_shape[1], self.roi_shape[0])
                      for i, key in enumerate(["image", "bright"])}
            
            self._save(images, record_path)
            self._send_update(record_path, record_type)
        
Device = TOFtcam