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

from device_server.server import DeviceServer
from server_tools.decorators import quickSetting

UPDATE_ID = 698043

class MSquaredServer(DeviceServer):
    """
    M-squared LabRAD server
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
        if state:
            device.set_etalon_lock(state)
        response = device.get_etalon_lock()
        return response
    
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

if __name__ == '__main__':
    from labrad import util
    util.runServer(MSquaredServer())
