"""
### BEGIN NODE INFO
[info]
name = tcam
version = 2.0
description = 
instancename = tcam

[startup]
cmdline = %PYTHON% %FILE%
timeout = 60

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
import numpy as np
import os, json, time

from ctypes import *

from labrad.server import setting
from server_tools.threaded_server import ThreadedServer

class CameraOpenError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class TCamServer(ThreadedServer):
    """ Provides access to Thorlabs Camera via SDK UC480. """
    name = 'tcam'

    def initServer(self):
        uc480_file = 'C:\\Program Files\\Thorlabs\\Scientific Imaging\\ThorCam\\uc480_64.dll'
        if os.path.isfile(uc480_file):        
            self.bit_depth = None
            self.roi_shape = None
            self.camera = None
            self.handle = None
            self.meminfo = None
            self.exposure = None
            self.roi_pos = None
            self.frametime = None
            self.timeout = None
            self.delay = None
            self.uc480 = windll.LoadLibrary(uc480_file)
        else:
            raise CameraOpenError("ThorCam drivers not available.")
        super(TCamServer, self).initServer()
    
    def stopServer(self):
        self._close()
        super(TCamServer, self).stopServer()
    
    @setting(10, request_json = 's')
    def open(self, c, request_json = '{}'):
        """Open the Camera,
        Request should be dict dumped in json, for example,
        '{
        'bit_depth' : 8,
        'camera' : 'ThorCam FS',
        'roi_shape' : [1280, 1024],
        'roi_pos' : [0, 0],
        'exposure' : 2, # in ms
        'frametime' : 10.0,
        'timeout' : 100, # in s
        'delay' : 3, # in us
        }'        
        """
        if request_json == '{}':
            print('No config loaded, ThorCam initialization failed.')
        else:
            request = json.loads(request_json)
            response = self._open(request)
            response_json = json.dumps(response)
            # return response_json
        
    def _open(self, request):
        # self.bit_depth = request['bit_depth']
        # self.camera = request['camera']
        if self.handle != None:  # make sure camera is closed when opening.
            self._close()
        
        self.roi_shape = request['roi_shape']
        self.roi_pos = request['roi_pos']
        self.exposure = request['exposure']
        self.frametime = request['frametime']
        self.timeout = request['timeout']
        self.delay = request['delay']
        
        is_InitCamera = self.uc480.is_InitCamera
        is_InitCamera.argtypes = [POINTER(c_int)]
        self.handle = c_int(0)  # 0 for the first CCD
        i = is_InitCamera(byref(self.handle))
        
        if i == 0 :
            print("ThorCam opened successfully.")
            pixelclock = c_uint(43) # set Pixel clock to 43 MHz (max)
            is_PixelClock = self.uc480.is_PixelClock
            is_PixelClock.argtypes = [c_int, c_uint, POINTER(c_uint), c_uint]
            is_PixelClock(self.handle, 6, byref(pixelclock), sizeof(pixelclock)) # 6 for setting pixel clock
            
            self.uc480.is_SetColorMode(self.handle, 6) # 6 is for monochrome 8 bit.
            self._set_roi_shape(self.roi_shape)
            self._set_roi_position(self.roi_pos)
            self._set_frametime(self.frametime)   # MUST set frametime first, then exposure time.
            self._set_exposure(self.exposure)
            self._set_timeout(self.timeout)
            self._set_trigger_delay(self.delay)
        else:
            raise CameraOpenError('Opening the ThorCam failed with error code '+str(i))
            
    @setting(11, roi_shape = '*i')
    def set_roi_shape(self, c, roi_shape):
        self._set_roi_shape(roi_shape)        
    
    def _set_roi_shape(self, roi_shape):
        class IS_SIZE_2D(Structure):
            _fields_ = [('s32Width', c_int), ('s32Height', c_int)]
        AOI_size = IS_SIZE_2D(roi_shape[0], roi_shape[1])  # Width and Height
        
        is_AOI = self.uc480.is_AOI
        is_AOI.argtypes = [c_int, c_uint, POINTER(IS_SIZE_2D), c_uint]
        i = is_AOI(self.handle, 5, byref(AOI_size), 8), # 5 for setting size, 3 for setting position
        is_AOI(self.handle, 6, byref(AOI_size), 8) # 6 for getting size, 4 for getting position
        self.roi_shape = [AOI_size.s32Width, AOI_size.s32Height]
        
        if i[0] == 0 :
            print("ThorCam ROI size set sucessfully.")
            self._initialize_memory()                                         
        else:
            print("Set ThorCam ROI size failed with error code "+str(i))
            
    @setting(12, roi_position = '*i')
    def set_roi_position(self, c, roi_position):
        self._set_roi_position(roi_position)
    
    def _set_roi_position(self, roi_position):
        class IS_POSITION_2D(Structure):
            _fields_ = [('s32X', c_int), ('s32Y', c_int)]
        AOI_pos = IS_POSITION_2D(roi_position[0], roi_position[1]) # X and Y
        
        is_AOI = self.uc480.is_AOI
        is_AOI.argtypes = [c_int, c_uint, POINTER(IS_POSITION_2D), c_uint]
        i = is_AOI(self.handle, 3, byref(AOI_pos), 8), # 5 for setting size, 3 for setting position
        is_AOI(self.handle, 4, byref(AOI_pos), 8) # 6 for getting size, 4 for getting position
        self.roi_pos = [AOI_pos.s32X, AOI_pos.s32Y]
        
        if i[0] == 0 :
            print("ThorCam ROI position set sucessfully.")                    
        else:
            print("Set ThorCam ROI position failed with error code "+str(i))
    
    @setting(13)
    def initialize_memory(self, c):
        self._initialize_memory()  
    
    def _initialize_memory(self):
        if self.meminfo != None:
            self.uc480.is_FreeImageMem(self.handle, self.meminfo[0], self.meminfo[1])
        
        xdim = self.roi_shape[0]
        ydim = self.roi_shape[1]
        imagesize = xdim*ydim
        
        memid = c_int(0)
        c_buf = (c_ubyte * imagesize)(0)
        self.uc480.is_SetAllocatedImageMem(self.handle, xdim, ydim, 8, c_buf, byref(memid))
        self.uc480.is_SetImageMem(self.handle, c_buf, memid)
        self.meminfo = [c_buf, memid]
    
    @setting(14)
    def set_exposure(self, c, exposure):
        """Set exposure time in ms"""
        self._set_exposure(exposure)  
    
    def _set_exposure(self, exposure):
        exposure_c = c_double(exposure/1000.0)
        is_Exposure = self.uc480.is_Exposure
        is_Exposure.argtypes = [c_int, c_uint, POINTER(c_double), c_uint]
        is_Exposure(self.handle, 12, exposure_c, 8) # 12 is for setting exposure
        self.exposure = exposure_c.value
    
    @setting(15)
    def set_frametime(self, c, frametime):
        """Setting frametime will reset exposure time!!!
        Frametime given in ms.
        Framerate = 1/Frametime.
        """
        self._set_frametime(frametime)  
    
    def _set_frametime(self, frametime):
        is_SetFrameRate = self.uc480.is_SetFrameRate
        
        if frametime == 0:
            frametime = 0.001
        
        set_framerate = c_double(0)
        is_SetFrameRate.argtypes = [c_int, c_double, POINTER(c_double)]
        is_SetFrameRate(self.handle, 1.0/(frametime/1000.0), byref(set_framerate))
        self.frametime = (1.0/set_framerate.value*1000.0)
    
    @setting(20)
    def close(self, c):
        self._close()
    
    def _close(self):
        if self.handle != None:
            self._stop_live_capture()
            i = self.uc480.is_ExitCamera(self.handle)
            if i == 0:
                self.handle = None
                print("Thorcam closed successfully.")
            else:
                print("Closing ThorCam with error code " + str(i))
        else:
            return
    
    @setting(21)
    def stop_live_capture(self, c):
        """ Stop Capture. """
        self._stop_live_capture()
    
    def _stop_live_capture(self):
        print('Unlive CCD now.')
        self.uc480.is_StopLiveVideo(self.handle, 1)
    
    @setting(30)
    def start_continuous_capture(self, c, buffersize = None):
        """
        Start capture in continuous mode.
        w = 0: will not wait; 1: will wait until event.
        Buffersize: number of frames to keep in rolling buffer.
        """
        self._start_continuous_capture()
        
    def _start_continuous_capture(self):
        self.uc480.is_CaptureVideo(self.handle, 1)
    
    @setting(31)
    def start_single_capture(self, c):
        """
        Start capture in single shot mode.
        w = 0: will not wait; 1: will wait until event.
        """        
        self._start_single_capture()
    
    def _start_single_capture(self):
        self.uc480.is_FreezeVideo(self.handle, 1)
        
    @setting(32, mode = 'i')
    def set_trigger_mode(self, c, mode = 2):
        """Sets the trigger mode, default to External HW trigger, with rising edge.
        0 = Trigger OFF
        1 = HW Trigger, Falling edge
        2 = HW Trigger, Rising edge
        """
        self._set_trigger_mode(mode)
    
    def _set_trigger_mode(self, mode = 2):
        is_SetExternalTrigger = self.uc480.is_SetExternalTrigger
        is_SetExternalTrigger.argtypes = [c_int, c_int]
        is_SetExternalTrigger(self.handle, mode)
    
    @setting(33, timeout = 'i')
    def set_timeout(self, c, timeout = 100):
        """Set trigger timeout in s.
        """
        self._set_timeout(timeout)
    
    def _set_timeout(self, timeout = 100):
        set_timeout = timeout*100
        is_SetTimeout = self.uc480.is_SetTimeout
        is_SetTimeout.argtypes = [c_int, c_uint, c_uint]
        is_SetTimeout(self.handle, 0, set_timeout) # 0 for trigger timeout.
    
    @setting(34, delay = 'i')
    def set_trigger_delay(self, c, delay):
        """Set trigger delay in us.
        """
        self._set_trigger_delay(delay)
    
    def _set_trigger_delay(self, delay):
        is_SetTriggerDelay = self.uc480.is_SetTriggerDelay
        is_SetTriggerDelay.argtypes = [c_int, c_int]
        is_SetTriggerDelay(self.handle, c_int(int(delay)))
    
    @setting(40, returns='s')
    def get_image(self, c, buffer_number = None):
        # buffer_number not yet used
        im = self._get_image(buffer_number)
        im_json = json.dumps(im)
        return im_json
    
    def _get_image(self, buffer_number = None):
        im = np.frombuffer(self.meminfo[0], c_ubyte).reshape(self.roi_shape[1], self.roi_shape[0])
        im_list = im.tolist()
        return im_list
    
Server = TCamServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())