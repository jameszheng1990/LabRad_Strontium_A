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
        andor.SetTemperature(-70)
        andor.SetCoolerMode(0)
        andor.CoolerON()
        
    def config(self, record_path=None, record_type=None, record_settings={}):
        if record_path is None:
            return
        
        andor_server = self.cxn[self.andor_servername]
        andor = AndorProxy(andor_server)
        
        try:
            xi = record_settings['roi'][0]
            xf = record_settings['roi'][1]
            yi = record_settings['roi'][2]
            yf = record_settings['roi'][3]
            
        except:
            xi = 1
            xf = 1024
            yi = 1
            yf = 1024
            
        try:
            if record_settings['em_gain'] < 2:
                em_mode = 0
                em_gain = 0
            else:
                em_mode = 3
                em_gain = record_settings['em_gain']
                em_gain = sorted([self.min_em_gain, int(em_gain), self.max_em_gain])[1]
            
        except:
            em_mode = 0
            em_gain = 0
        
        if record_type == 'g_abs_img':
            andor.SetAcquisitionMode(3) # Kinetics mode
            andor.SetReadMode(4) # Image mode
            andor.SetNumberAccumulations(1)
            andor.SetNumberKinetics(3) # 3 images each run
            andor.SetAccumulationCycleTime(0)
            andor.SetKineticCycleTime(0)
            andor.SetPreAmpGain(0)
            andor.SetEMGainMode(em_mode)  # 3 for Real value mode
            andor.SetEMCCDGain(em_gain)
            andor.SetHSSpeed(0, 0)
            andor.SetVSSpeed(1)
            andor.SetShutter(1, 1, 0, 0)  # permanently open
            andor.SetTriggerMode(1)
            andor.SetExposureTime(500e-6)
            andor.SetImage(1, 1, xi, xf, yi, yf)
    
        if record_type == 'eg_abs_img':
            andor.SetAcquisitionMode(4)
            andor.SetReadMode(4)
            andor.SetPreAmpGain(0)
            andor.SetHSSpeed(0, 0)
            andor.SetVSSpeed(1)
            andor.SetShutter(1, 1, 0, 0)
            andor.SetTriggerMode(1)
            andor.SetFastKineticsEx(341, 3, 500e-6, 4, 1, 1, 682)
            
        if record_type == 'fast-g_abs_img':
            andor.SetAcquisitionMode(4)
            andor.SetReadMode(4)
            andor.SetPreAmpGain(0)
            andor.SetHSSpeed(0, 0)
            andor.SetVSSpeed(1)
            andor.SetShutter(1, 1, 0, 0)
            andor.SetTriggerMode(1)
            andor.SetFastKineticsEx(341, 3, 500e-6, 4, 1, 1, 683)

        if record_type == 'fast-eg_abs_img':
            andor.SetAcquisitionMode(4)
            andor.SetReadMode(4)
            andor.SetPreAmpGain(0)
            andor.SetHSSpeed(0, 0)
            andor.SetVSSpeed(1)
            andor.SetShutter(1, 1, 0, 0)
            andor.SetTriggerMode(1)
            andor.SetFastKineticsEx(256, 4, 500e-6, 4, 1, 1, 1024 - 256)
#            andor.SetFastKinetics(256, 4, 500e-6, 4, 1, 1)

        if record_type == 'g_fluo_img':
            andor.SetAcquisitionMode(3) # Kinetics mode
            andor.SetReadMode(4) # Image mode
            andor.SetNumberAccumulations(1)
            andor.SetNumberKinetics(2) # 2 images each run
            andor.SetAccumulationCycleTime(0)
            andor.SetKineticCycleTime(0)
            andor.SetPreAmpGain(0)
            andor.SetEMGainMode(em_mode)  # 3 for Real value mode
            andor.SetEMCCDGain(em_gain)
            andor.SetHSSpeed(0, 0)
            andor.SetVSSpeed(1)
            andor.SetShutter(1, 1, 0, 0)  # permanently open
            andor.SetTriggerMode(1)
            andor.SetExposureTime(1e-3)
            andor.SetImage(1, 1, xi, xf, yi, yf)
            
        if record_type == 'raw':
            andor.SetAcquisitionMode(3) # Kinetics mode
            andor.SetReadMode(4) # Image mode
            andor.SetNumberAccumulations(1)
            andor.SetNumberKinetics(2) # 2 images each run
            andor.SetAccumulationCycleTime(0)
            andor.SetKineticCycleTime(0)
            andor.SetPreAmpGain(0)
            andor.SetEMGainMode(em_mode)  # 3 for Real value mode
            andor.SetEMCCDGain(em_gain)
            andor.SetHSSpeed(0, 0)
            andor.SetVSSpeed(1)
            andor.SetShutter(1, 1, 0, 0)  # permanently open
            andor.SetTriggerMode(1)
            andor.SetExposureTime(1e-3)
            andor.SetImage(1, 1, xi, xf, yi, yf)
            
        if record_type == 'gain_calibration':
            andor.SetAcquisitionMode(3) # Kinetics mode
            andor.SetReadMode(4) # Image mode
            andor.SetNumberAccumulations(1)
            andor.SetNumberKinetics(3) # number of images each run
            andor.SetAccumulationCycleTime(0)
            andor.SetKineticCycleTime(0)
            andor.SetEMGainMode(em_mode)  # 3 for Real value mode
            andor.SetEMCCDGain(em_gain)
            andor.SetPreAmpGain(0)
            andor.SetHSSpeed(0, 0)
            andor.SetVSSpeed(1)
            andor.SetShutter(1, 1, 0, 0)  # permanently open
            andor.SetTriggerMode(1)
            andor.SetExposureTime(1e-3)
            andor.SetImage(1, 1, xi, xf, yi, yf)
            
    def record(self, record_path=None, record_type=None, record_settings={}):
        if record_path is None:
            return
        
        andor_server = self.cxn[self.andor_servername]
        andor = AndorProxy(andor_server)

        # # abort if waiting
        andor.CancelWait()
        # andor.AbortAcquisition()
        
        try:
            xi = record_settings['roi'][0]
            xf = record_settings['roi'][1]
            yi = record_settings['roi'][2]
            yf = record_settings['roi'][3]
            
        except:
            xi = 1
            xf = 1024
            yi = 1
            yf = 1024
            
        if record_type == 'g_abs_img':
            for i in range(3):
                andor.StartAcquisition()
                andor.WaitForAcquisition()
            
            data = andor.GetAcquiredData(3 * (xf-xi+1) * (yf-yi+1)).reshape(3,  (yf-yi+1), (xf-xi+1))
            images = {key: data[i] 
                      for i, key in enumerate(["image", "bright", "dark"])}
            
            self._save(images, record_path)
            self._send_update(record_path, record_type, record_settings)
        
        if record_type == 'eg_abs_img':
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
            self._send_update(record_path, record_type, record_settings)
        
        if record_type == 'fast-g_abs_img':
            andor.StartAcquisition()
            andor.WaitForAcquisition()
            data = andor.GetAcquiredData(3 * 341 * 1024).reshape(3, 341, 1024)
            images = {key: data[i] 
                    for i, key in enumerate(["image", "bright", "dark"])}
            
            self._save(images, record_path)
            self._send_update(record_path, record_type, record_settings)
        
        if record_type == 'fast-eg_abs_img':
            andor.StartAcquisition()
            andor.WaitForAcquisition()
            data = andor.GetAcquiredData(4 * 256 * 1024).reshape(4, 256, 1024)
            images = {key: data[i] 
#                    for i, key in enumerate(["empty", "image-g", "image-e", "bright"])}
                    for i, key in enumerate(["image-g", "image-e", "bright", "empty"])}
            
            self._save(images, record_path)
            self._send_update(record_path, record_type, record_settings)
        
        if record_type == 'g_fluo_img':
            for i in range(2):
                andor.StartAcquisition()
                andor.WaitForAcquisition()
            
            data = andor.GetAcquiredData(2 * (xf-xi+1) * (yf-yi+1)).reshape(2,  (yf-yi+1), (xf-xi+1))
            images = {key: data[i] 
                      for i, key in enumerate(["image", "bright"])}
            
            self._save(images, record_path)
            self._send_update(record_path, record_type, record_settings)
        
        if record_type == 'raw':
            for i in range(2):
                andor.StartAcquisition()
                andor.WaitForAcquisition()
            
            data = andor.GetAcquiredData(2 * (xf-xi+1) * (yf-yi+1)).reshape(2,  (yf-yi+1), (xf-xi+1))
            images = {key: data[i] 
                      for i, key in enumerate(["bright", "dark"])}
            
            self._save(images, record_path)
            self._send_update(record_path, record_type, record_settings)
        
        if record_type == 'gain_calibration':
            for i in range(3):
                andor.StartAcquisition()
                andor.WaitForAcquisition()
            
            data = andor.GetAcquiredData(3 * (xf-xi+1) * (yf-yi+1)).reshape(3,  (yf-yi+1), (xf-xi+1))
            images = {key: data[i] 
                      for i, key in enumerate(["a", "b", "dark"])}
            
            self._save(images, record_path)
            self._send_update(record_path, record_type, record_settings)
            
        print('[camera] Andor iXon-888 recorded')
        
Device = ixon