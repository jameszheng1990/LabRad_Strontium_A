from camera.devices.AndorCam.device import AndorCam
from andor_server.proxy import AndorProxy
import json, time, os

class ixon(AndorCam):
    andor_servername = 'andor'
    autostart= True
    
    compression = 'gzip'
    compression_level = 0
    
    min_em_gain = 2
    max_em_gain = 300
    
    def initialize(self, config):
        super(ixon, self).initialize(config)
        self.connect_to_labrad()
        
        andor_server = self.cxn[self.andor_servername]
        andor = AndorProxy(andor_server)
        
        andor.Initialize()
        andor.SetFanMode(0) # Fan on full
        andor.SetTemperature(-65)
        andor.SetCoolerMode(0)
        andor.CoolerON()
    
    def record(self, record_path=None, record_type=None, record_settings={}):
        if record_path is None:
            return
        
        andor_server = self.cxn[self.andor_servername]
        andor = AndorProxy(andor_server)

        # # abort if acquiring
        andor.AbortAcquisition()
        
        try:
            xi = record_settings['roi'][0]
            xf = record_settings['roi'][1]
            yi = record_settings['roi'][2]
            yf = record_settings['roi'][3]
            em_gain = record_settings['em_gain']
            em_gain = sorted([self.min_em_gain, em_gain, self.max_em_gain])[1]
        except:
            xi = 1
            xf = 1024
            yi = 1
            yf = 1024
            em_gain = self.min_em_gain
            
        if record_type == 'g_abs_img':
            number_of_img = 2
            andor.SetAcquisitionMode(3) # Kinetics mode
            andor.SetReadMode(4) # Image mode
            andor.SetNumberAccumulations(1)
            andor.SetNumberKinetics(number_of_img) # 2 images each run
            andor.SetAccumulationCycleTime(0)
            andor.SetKineticCycleTime(0)
            andor.SetPreAmpGain(0)
            andor.SetEMGainMode(4)  # Real value mode
            andor.SetEMCCDGain(em_gain)
            andor.SetHSSpeed(0, 0)
            andor.SetVSSpeed(1)
            andor.SetShutter(1, 1, 0, 0)  # permanently open
            andor.SetTriggerMode(1)
            andor.SetExposureTime(500e-6)
            # andor.SetImage(1, 1, 1, 1024, 1, 1024)
            andor.SetImage(1, 1, xi, xf, yi, yf)
            
            for i in range(number_of_img):
                andor.StartAcquisition()
                andor.WaitForAcquisition()
            
            # data = andor.GetAcquiredData(3 * 1024 * 1024).reshape(3, 1024, 1024)
            data = andor.GetAcquiredData(number_of_img * (xf-xi+1) * (yf-yi+1)).reshape(number_of_img,  (yf-yi+1), (xf-xi+1))
            images = {key: data[i] 
                      for i, key in enumerate(["image", "bright"])}
            
            self._save(images, record_path)
            self._send_update(record_path, record_type)
        
        if record_type == 'eg_abs_img':
            andor.SetAcquisitionMode(4)
            andor.SetReadMode(4)
            andor.SetPreAmpGain(0)
            andor.SetHSSpeed(0, 0)
            andor.SetVSSpeed(1)
            andor.SetShutter(1, 1, 0, 0)
            andor.SetTriggerMode(1)
            andor.SetFastKineticsEx(341, 3, 500e-6, 4, 1, 1, 682)

            andor.StartAcquisition()
            andor.WaitForAcquisition()
            data = andor.GetAcquiredData(3 * 341 * 1024).reshape(3, 341, 1024)
            images = {key: data[i] 
                    for i, key in enumerate(["image_g", "image_e", "bright"])}
            
            andor.StartAcquisition()
            andor.WaitForAcquisition()
            data = andor.GetAcquiredData(3 * 341 * 1024).reshape(3, 341, 1024)
            
            background_images = {key: data[i] 
                    for i, key in enumerate(["dark_g", "dark_e", "dark_bright"])}

            images.update(background_images)
            
            self._save(images, record_path)
            self._send_update(record_path, record_type)
        
        if record_type == 'fast-g_abs':
            andor.SetAcquisitionMode(4)
            andor.SetReadMode(4)
            andor.SetPreAmpGain(0)
            andor.SetHSSpeed(0, 0)
            andor.SetVSSpeed(1)
            andor.SetShutter(1, 1, 0, 0)
            andor.SetTriggerMode(1)
            andor.SetFastKineticsEx(341, 3, 500e-6, 4, 1, 1, 683)

            andor.StartAcquisition()
            andor.WaitForAcquisition()
            data = andor.GetAcquiredData(3 * 341 * 1024).reshape(3, 341, 1024)
            images = {key: data[i] 
                    for i, key in enumerate(["image", "bright", "dark"])}
            
            self._save(images, record_path)
            self._send_update(record_path, record_type)
        
        if record_type == 'fast-eg_abs':
            andor.SetAcquisitionMode(4)
            andor.SetReadMode(4)
            andor.SetPreAmpGain(0)
            andor.SetHSSpeed(0, 0)
            andor.SetVSSpeed(1)
            andor.SetShutter(1, 1, 0, 0)
            andor.SetTriggerMode(1)
            andor.SetFastKineticsEx(256, 4, 500e-6, 4, 1, 1, 1024 - 256)
#            andor.SetFastKinetics(256, 4, 500e-6, 4, 1, 1)

            andor.StartAcquisition()
            andor.WaitForAcquisition()
            data = andor.GetAcquiredData(4 * 256 * 1024).reshape(4, 256, 1024)
            images = {key: data[i] 
#                    for i, key in enumerate(["empty", "image-g", "image-e", "bright"])}
                    for i, key in enumerate(["image-g", "image-e", "bright", "empty"])}
            
            self._save(images, record_path)
            self._send_update(record_path, record_type)
        
        print('Andor IXon-888 recorded.')
        
Device = ixon