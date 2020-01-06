from camera.devices.ThorCam.device import TCam
from thorlabs_cam.proxy import TCamProxy

class TOFtcam(TCam):
    tcam_servername = 'tcam'
    
    compression = 'gzip'
    compression_level = 0
        
    def record(self, record_path=None, record_type=None, record_settings={}):
        if record_path is None:
            return
        
        tcam_server = self.cxn[self.tcam_servername]
        tcam = TCamProxy(tcam_server)

        # close if acquiring
        tcam.Close()
        
        config = {
            'bit_depth' : 8,
            'camera' : 'ThorCam FS',
            'roi_shape' : [1280, 1024],
            'roi_pos' : [0, 0],
            'exposure' : 2, # in ms
            'frametime' : 10.0,
            'timeout' : 120, # in s
            'delay'   : 3, # in us
            }
        
        if record_type == 'abs_img':   # Simple absorption imaging
            tcam.Open(config)
            data = []
            
            # Take three images, one ('image') with atoms, one ('bright') without atoms, and 'dark' without probe light.
            for i in range(3):
                tcam.Start_Single_Capture()
                image = tcam.Get_Image()
                data.append(image)

            images = {key: data[i] 
                      for i, key in enumerate(["image", "bright", "dark"])}
            
            self._save(images, record_path)
            self._send_update(record_path, record_type)

Device = TOFtcam