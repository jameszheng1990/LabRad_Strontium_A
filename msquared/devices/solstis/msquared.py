import socket
import os
import sys
sys.path.append(os.getenv('PROJECT_LABRAD_TOOLS_PATH'))

from twisted.internet.defer import inlineCallbacks, returnValue

from device_server.device import DefaultDevice
from msquared.devices.solstis.lib.msquared_message import MSquaredMessage
from msquared.devices.solstis.lib.helpers import normalize_parameters

class MSquared(DefaultDevice):
    socket_address = None
    socket_timeout = None

    def initialize(self, config):
        super(MSquared, self).initialize(config)
        self.connect_to_labrad()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.socket_timeout)
        self.socket.connect(self.socket_address)
        try:
            self.socket.recv(1024)
        except socket.timeout:
            pass

        interface = self.socket.getsockname()
        response_message = self.send(op='start_link',
            parameters={ 'ip_address': interface[0]})
        print(response_message)

    def terminate(self):
        self.socket.close()

    def send(self, **kwargs):
        message = MSquaredMessage(**kwargs)
        message_json = message.to_json()
        self.socket.send(message_json.encode())  # ADD .encode()
        response_json = self.socket.recv(1024)
        return MSquaredMessage.from_json(response_json)
    
    def set(self, setting, value, key_name='setting'):
        parameters = {key_name: value}
        if key_name == 'setting':
            parameters[key_name] = [parameters[key_name]]
        response_message = self.send(op=setting, parameters=parameters)
        ok = response_message.is_ok(status=[0])
        return bool(ok)
    
    def get(self, setting):
        response_message = self.send(op=setting, parameters=None)
        if response_message.is_ok(status=[0]):
            return normalize_parameters(response_message.parameters)
        else:
            return None
