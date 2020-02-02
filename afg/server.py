"""
### BEGIN NODE INFO
[info]
name = afg
version = 1.0
description = 
instancename = afg

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

from device_server.server import DeviceServer


class AFGServer(DeviceServer):
    """ Provides basic control for arbitrary function generators"""
    name = 'afg'
    
    autostart = True

    @setting(10)
    def waveforms(self, c, request_json='{}'):
        """ get or change waveform """
        request = json.loads(request_json)
        response = self._waveforms(request)
        response_json = json.dumps(response)
        return response_json
        
    def _waveforms(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, waveform in request.items():
            device_response = None
            try:
                device_response = self._waveform(device_name, waveform)
            except:
                self._reload_device(device_name, {})
                device_response = self._waveform(device_name, waveform)
            response.update({device_name: device_response})
        self._send_update({'waveforms': response})
        return response

    def _waveform(self, name, waveform):
        device = self._get_device(name)
        if waveform:
            device.set_waveform(waveform)
        response = device.get_waveform()
        return response
    
    @setting(11)
    def run(self, c, request_json='{}'):
        """ run sequence """
        request = json.loads(request_json)
        self._run(request)

    def _run(self, request):
        for device_name, request in request.items():
            device = self._get_device(device_name)
            run_state = device.get_runstate()
            if run_state:
                device.stop()
            device.run()

Server = AFGServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
