import json

class VisaProxy(object):
    def __init__(self, server):
        self.server = server

    def ResourceManager(self):
        rm = ResourceManagerProxy(self.server)
        return rm

class ResourceManagerProxy(object):
    def __init__(self, server):
        self.server = server

    def list_resources(self):
        return self.server.list_resources()
    
    def open_resource(self, resource_name):
        if 'USB' in resource_name or 'ASRL' in resource_name:
            return USBInstrumentProxy(self.server, resource_name)
    
class USBInstrumentProxy(object):
    def __init__(self, server, resource_name):
        self._timeout = 3000
        self._server = server
        self.resource_name = resource_name
    
    @property
    def _resource_kwargs(self):
        return {
            'timeout': self._timeout,
            }
    
    @property
    def _resource_kwargs_json(self):
        return json.dumps(self._resource_kwargs)

    def query(self, message, delay=None):
        """A combination of write(message) and read()

        Args:
            message (str): the message to send.
            delay (float): delay in seconds between write and read operations.
                if None, defaults to self.query_delay
        Returns:
            (str) the answer from the device.

        """ 
        return self._server.query(self.resource_name, 
                                  self._resource_kwargs_json, message, delay)

    def read(self, termination=None, encoding=None):
        """Read a string from the device.

        Reading stops when the device stops sending (e.g. by setting appropriate 
        bus lines), or the termination characters sequence was detected.
        Attention: Only the last character of the termination characters is 
        really used to stop reading, however, the whole sequence is compared to 
        the ending of the read string message. If they don't match, a warning is 
        issued.

        All line-ending characters are stripped from the end of the string.
        Args:
            termination (str): characters at which to stop reading
            encoding (str): encoding used for read operation
        Returns:
            (str) output from device
        """
        return self._server.read(self.resource_name, self._resource_kwargs_json, 
                                termination, encoding)
    
    @property
    def timeout(self):
        """ The timeout in milliseconds for all resource I/O operations. """
        self._timeout = self._server.get_timeout(self.resource_name, 
                                                 self._resource_kwargs_json)
        return self._timeout
    
    @timeout.setter
    def timeout(self, timeout):
        """ The timeout in milliseconds for all resource I/O operations. """
        self._timeout = timeout
        return self._server.set_timeout(self.resource_name, 
                                        self._resource_kwargs_json, timeout)

    def write(self, message, termination=None, encoding=None):
        """ Write a string message to the device.

        The write_termination is always appended to it.

        Args:
            message (str): the message to be sent.
            termination (str): termination chars to be appended to message.
            encoding (str): byte encoding for message
        Returns:
            (int) number of bytes written
        """ 
        return self._server.write(self.resource_name, 
                                  self._resource_kwargs_json, message, 
                                  termination, encoding)
