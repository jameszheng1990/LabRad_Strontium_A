"""
### BEGIN NODE INFO
[info]
name = msquared
version = 1.0
description = 
instancename = msquared

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

import json
import os
import sys
sys.path.append(os.getenv('PROJECT_LABRAD_TOOLS_PATH'))

from labrad.server import Signal, setting
from twisted.internet import task, defer, reactor
from twisted.internet.defer import inlineCallbacks, returnValue

from device_server.server import DeviceServer
from server_tools.decorators import quickSetting

UPDATE_ID = 698043

class MSquaredServer(DeviceServer):
    """
    M-squared server
    """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'msquared'
    autostart = True
    
    @setting(10)
    def system_status(self, c, request_json='{}'):
        """ get system status """
        request = json.loads(request_json)
        response = self._system_status(request)
        response_json = json.dumps(response)
        return response_json

    def _system_status(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, status in request.items():
            device_response = None
            try:
                device_response = self.__system_status(device_name, status)
            except:
                self._reload_device(device_name, {})
                device_response = self.__system_status(device_name, status)
            response.update({device_name: device_response})
        self._send_update({'system status': response})
        return response
    
    def __system_status(self, name, status):
        device = self._get_device(name)
        if status:
            device.set_system_status(status)
        response = device.get_system_status()
        return response
    
    @setting(11)
    def etalon_lock(self, c, request_json='{}'):
        """ get or set etalon lock state """
        request = json.loads(request_json)
        response = self._etalon_lock(request)
        response_json = json.dumps(response)
        return response_json

    def _etalon_lock(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, state in request.items():
            device_response = None
            try:
                device_response = self.__etalon_lock(device_name, state)
            except:
                self._reload_device(device_name, {})
                device_response = self.__etalon_lock(device_name, state)
            response.update({device_name: device_response})
        self._send_update({'etalon state': response})
        return response
    
    def __etalon_lock(self, name, state):
        device = self._get_device(name)
        if state is not None:
            device.set_etalon_lock(state)
            # reactor.callLater(2, self.update_etalon_lock_later, name)
            response = None
        elif state is None:
            response = device.get_etalon_lock()
        return response
    
    # def update_etalon_lock_later(self, name):
    #     response = {}
    #     device = self._get_device(name)
    #     device_response = device.get_etalon_lock()
    #     response.update({name: device_response})
    #     self._send_update({'etalon state': response})
        
    @setting(12)
    def etalon_tune(self, c, request_json='{}'):
        """ set etalon tune percentage
            or get etalon voltage """
        request = json.loads(request_json)
        response = self._etalon_tune(request)
        response_json = json.dumps(response)
        return response_json

    def _etalon_tune(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, percentage in request.items():
            device_response = None
            try:
                device_response = self.__etalon_tune(device_name, percentage)
            except:
                self._reload_device(device_name, {})
                device_response = self.__etalon_tune(device_name, percentage)
            response.update({device_name: device_response})
        self._send_update({'etalon_tune': response})
        return response
    
    def __etalon_tune(self, name, percentage):
        device = self._get_device(name)
        if percentage:
            device.set_etalon_tune(percentage)
        response = device.get_etalon_tune()
        return response
    
    @setting(13)
    def resonator_tune(self, c, request_json='{}'):
        """ set resonator tune percentage
            or get resonator voltage """
        request = json.loads(request_json)
        response = self._resonator_tune(request)
        response_json = json.dumps(response)
        return response_json

    def _resonator_tune(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, percentage in request.items():
            device_response = None
            try:
                device_response = self.__resonator_tune(device_name, percentage)
            except:
                self._reload_device(device_name, {})
                device_response = self.__resonator_tune(device_name, percentage)
            response.update({device_name: device_response})
        self._send_update({'resonator_tune': response})
        return response
    
    def __resonator_tune(self, name, percentage):
        device = self._get_device(name)
        if percentage:
            device.set_resonator_tune(percentage)
        response = device.get_resonator_tune()
        return response
    
    @setting(14)
    def resonator_fine_tune(self, c, request_json='{}'):
        """ set resonator fine tune percentage
            or get resonator voltage """
        request = json.loads(request_json)
        response = self._resonator_fine_tune(request)
        response_json = json.dumps(response)
        return response_json

    def _resonator_fine_tune(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, percentage in request.items():
            device_response = None
            try:
                device_response = self.___resonator_fine_tune(device_name, percentage)
            except:
                self._reload_device(device_name, {})
                device_response = self.___resonator_fine_tune(device_name, percentage)
            response.update({device_name: device_response})
        self._send_update({'resonator_fine_tune': response})
        return response
    
    def ___resonator_fine_tune(self, name, percentage):
        device = self._get_device(name)
        if percentage:
            device.set_resonator_fine_tune(percentage)
        response = device.get_resonator_fine_tune()
        return response

    @setting(15)
    def beam_alignment(self, c, request_json='{}'):
        """ Controls the operation of the beam alignment,
            or gets whether the beam alignment is finished,
            True for done, False means it is still under alignment. """
        request = json.loads(request_json)
        response = self._beam_alignment(request)
        response_json = json.dumps(response)
        return response_json

    def _beam_alignment(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, mode in request.items():
            device_response = None
            try:
                device_response = self.__beam_alignment(device_name, mode)
            except:
                self._reload_device(device_name, {})
                device_response = self.__beam_alignment(device_name, mode)
            response.update({device_name: device_response})
        self._send_update({'beam_alignment': response})
        return response
    
    def __beam_alignment(self, name, mode):
        device = self._get_device(name)
        if mode is not None:
            device.set_beam_alignment(mode)
            if mode == 4:
                self.beamalignment_task = task.LoopingCall(self.beam_alignment_update, name)
                reactor.callLater(1, self.beamalignment_task.start, 0.5) # Assume the alignment won't finish by 1 seconds, update X, Y every 0.5 seconds.
            response = None
        else:
            response = device.get_beam_alignment()
        return response
    
    def beam_alignment_update(self, name):
        response = {}
        response_x = {}
        response_y = {}
         
        device = self._get_device(name)
        device_response = device.get_beam_alignment()
        if device_response == True:
            response.update({name: device_response})
            self._send_update({'beam_alignment': response})
            self.beamalignment_task.stop()
        # Get X, Y value and update on client
        device_response_x = device.get_x() # TODO: might be get_x_auto here.. have to check later
        response_x.update({name: device_response_x})
        self._send_update({'alignment_x_auto': response_x}) # or alignment_auto
        device_response_y = device.get_y()
        response_y.update({name: device_response_y})
        self._send_update({'alignment_y_auto': response_y})        

    @setting(16)
    def alignment_x(self, c, request_json='{}'):
        """ Tune X of the beam alignment,
            or gets the current value of X. """
        request = json.loads(request_json)
        response = self._alignment_x(request)
        response_json = json.dumps(response)
        return response_json

    def _alignment_x(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, value in request.items():
            device_response = None
            try:
                device_response = self.__alignment_x(device_name, value)
            except:
                self._reload_device(device_name, {})
                device_response = self.__alignment_x(device_name, value)
            response.update({device_name: device_response})
        self._send_update({'alignment_x': response})
        return response
    
    def __alignment_x(self, name, value):
        device = self._get_device(name)
        if value is not None:
            device.set_x(value)
        response = device.get_x()
        return response

    @setting(17)
    def alignment_y(self, c, request_json='{}'):
        """ Tune Y of the beam alignment,
            or gets the current value of Y. """
        request = json.loads(request_json)
        response = self._alignment_y(request)
        response_json = json.dumps(response)
        return response_json

    def _alignment_y(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, value in request.items():
            device_response = None
            try:
                device_response = self.__alignment_y(device_name, value)
            except:
                self._reload_device(device_name, {})
                device_response = self.__alignment_y(device_name, value)
            response.update({device_name: device_response})
        self._send_update({'alignment_y': response})
        return response
    
    def __alignment_y(self, name, value):
        device = self._get_device(name)
        if value is not None:
            device.set_y(value)
        response = device.get_y()
        return response

    @setting(18)
    def wavelength(self, c, request_json='{}'):
        """ Sets or gets wavelength (rough, preset, don't trust it') """
        request = json.loads(request_json)
        response = self._wavelength(request)
        response_json = json.dumps(response)
        return response_json

    def _wavelength(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, value in request.items():
            device_response = None
            try:
                device_response = self.__wavelength(device_name, value)
            except:
                self._reload_device(device_name, {})
                device_response = self.__wavelength(device_name, value)
            response.update({device_name: device_response})
        self._send_update({'msq_wavelength': response})
        return response
    
    def __wavelength(self, name, value):
        device = self._get_device(name)
        if value is not None:
            device.set_wavelength(value)
        response = device.get_wavelength()
        return response    
        
if __name__ == '__main__':
    from labrad import util
    util.runServer(MSquaredServer())
