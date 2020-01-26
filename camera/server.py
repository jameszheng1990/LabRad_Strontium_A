"""
### BEGIN NODE INFO
[info]
name = camera
version = 1.0
description = 
instancename = camera

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
import json

from labrad.server import setting
from labrad.server import setting
from twisted.internet import reactor

from device_server.server import DeviceServer


class CameraServer(DeviceServer):
    """ Provides basic control for cameras """
    name = 'camera'

    @setting(100)
    def config_tcam(self, c, request_json = '{}'):
        """ Open and configure Thorlabs camera, will be called only at first of experiment. """
        request = json.loads(request_json)
        response = self._config_tcam(request)
        response_json = json.dumps(response)
        return response_json

    def _config_tcam(self, request):
        if request == {}:
            request = {
                device_name: {} for device_name in self.devices.items()
                }
        response = {}
        for device_name, device_request in request.items():
            device_response = {}
            device = self._get_device(device_name)
            
            record_type = device_request['record_type']
            config_file = device_request['config_file']
            if record_type is not None:
                device.config(record_type, config_file)
            response.update({device_name: device_response})
        return response
    
Server = CameraServer

if __name__ == '__main__':
    from labrad import util
    reactor.suggestThreadPoolSize(5)
    util.runServer(Server())
