"""
### BEGIN NODE INFO
[info]
name = vxi11
version = 1
description = none
instancename = vxi11

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
import json
import vxi11

from labrad.server import setting

from server_tools.threaded_server import ThreadedServer


class VXI11Server(ThreadedServer):
    name = 'vxi11'

    def _get_inst(self, **kwargs):
        host = kwargs.pop('host')
        timeout = kwargs.pop('timeout')
        inst = vxi11.Instrument(host, **kwargs)
        if timeout is not None:
            inst.timeout = timeout
        return inst

    @setting(10, host_kwargs_json='s', message='s', num='i', encoding='s', 
             returns='s')
    def ask(self, c, host_kwargs_json, message, num=-1, encoding='utf-8'):
        host_kwargs = json.loads(host_kwargs_json)
        inst = self._get_inst(**host_kwargs)
        response = inst.ask(message, num, encoding)
        return response
    
    @setting(11, host_kwargs_json='s', num='i', encoding='s', returns='s')
    def read(self, c, host_kwargs_json, num=-1, encoding='utf-8'):
        host_kwargs = json.loads(host_kwargs_json)
        inst = self._get_inst(**host_kwargs)
        response = inst.read(num, encoding)
        return response

    @setting(12, host_kwargs_json='s', returns='v')
    def get_timeout(self, c, host_kwargs_json):
        host_kwargs = json.loads(host_kwargs_json)
        inst = self._get_inst(**host_kwargs)
        return inst.timeout
    
    @setting(13, host_kwargs_json='s', timeout='v')
    def set_timeout(self, c, host_kwargs_json, timeout):
        host_kwargs = json.loads(host_kwargs_json)
        inst = self._get_inst(**host_kwargs)
        inst.timeout = timeout
    
    @setting(14, host_kwargs_json='s', message='s', encoding='s')
    def write(self, c, host_kwargs_json, message, encoding='utf-8'):
        host_kwargs = json.loads(host_kwargs_json)
        inst = self._get_inst(**host_kwargs)
        return inst.write(message, encoding)

if __name__ == '__main__':
    from labrad import util
    util.runServer(VXI11Server())
