"""
### BEGIN NODE INFO
[info]
name = visa
version = 2.0
description = 
instancename = visa

[startup]
cmdline = %PYTHON% %FILE%
timeout = 60

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
import pyvisa
import json

from labrad.server import setting

from server_tools.threaded_server import ThreadedServer

class VisaServer(ThreadedServer):
    """ Provides access to USB/GPIB resources using pyvisa """
    name = 'visa'

    def initServer(self):
        self._rm = pyvisa.ResourceManager()
        super(VisaServer, self).initServer()
    
    @setting(10, query='s', returns='*s')
    def list_resources(self, c, query='?*::INSTR'):
        return self._rm.list_resources()
    
    @setting(11, resource_name='s', resource_kwargs_json='s', mode='i')
    def control_ren(self, c, resource_name, resource_kwargs_json, mode):
        resource_kwargs = json.loads(resource_kwargs_json)
        inst = self._rm.open_resource(resource_name, **resource_kwargs)
        inst.control_ren(mode)
    
    @setting(12, resource_name='s', resource_kwargs_json='s', 
             termination=['s', '?'], encoding=['s', '?'], returns='s')
    def read(self, c, resource_name, resource_kwargs_json, termination, 
             encoding):
        resource_kwargs = json.loads(resource_kwargs_json)
        inst = self._rm.open_resource(resource_name, **resource_kwargs)
        return inst.read(termination, encoding)
    
    @setting(13, resource_name='s', resource_kwargs_json='s', returns='v')
    def get_timeout(self, c, resource_name, resource_kwargs_json):
        resource_kwargs = json.loads(resource_kwargs_json)
        inst = self._rm.open_resource(resource_name, **resource_kwargs)
        return inst.timeout

    @setting(14, resource_name='s', resource_kwargs_json='s', 
             timeout=['v', '?'])
    def set_timeout(self, c, resource_name, resource_kwargs_json, timeout):
        resource_kwargs = json.loads(resource_kwargs_json)
        inst = self._rm.open_resource(resource_name, **resource_kwargs)
        inst.timeout = timeout
    
    @setting(15, resource_name='s', resource_kwargs_json='s', message='s', 
             delay=['v', '?'], returns='s')
    def query(self, c, resource_name, resource_kwargs_json, message, delay):
        resource_kwargs = json.loads(resource_kwargs_json)
        inst = self._rm.open_resource(resource_name, **resource_kwargs)
        return inst.query(message, delay)

    @setting(16, resource_name='s', resource_kwargs_json='s', message='s', 
             termination=['s', '?'], encoding=['s', '?'], returns='i')
    def write(self, c, resource_name, resource_kwargs_json, message, 
              termination, encoding):
        resource_kwargs = json.loads(resource_kwargs_json)
        inst = self._rm.open_resource(resource_name, **resource_kwargs)
        return inst.write(message, termination, encoding)[0]
    
Server = VisaServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
