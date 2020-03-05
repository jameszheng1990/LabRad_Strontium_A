import json


class Vxi11Proxy(object):
    def __init__(self, server):
        self._server = server

    def Instrument(self, host, name=None, client_id=None, term_char=None):
        """ VXI-11 instrument interface client """
        return InstrumentProxy(self._server, host, name, client_id, term_char)


class InstrumentProxy(object):
    """ VXI-11 instrument interface client """
    def __init__(self, server, host, name=None, client_id=None, term_char=None):
        self._server = server
        self._host = host
        self._name = name
        self._client_id = client_id
        self._term_char = term_char
        self._timeout = 10
    
    @property
    def _host_kwargs_json(self):
        return json.dumps({
            'host': self._host,
            'name': self._name,
            'client_id': self._client_id,
            'term_char': self._term_char,
            'timeout': self._timeout,
            })

    def ask(self, message, num=-1, encoding='utf-8'):
        """ Write then read string """
        return self._server.ask(self._host_kwargs_json, message, num, encoding)

    def read(self, num=-1, encoding='utf-8'):
        """ Write string to instrument """
        return self._server.read(self._host_kwargs_json, num, encoding)
    
    @property
    def timeout(self):
        return self._server.get_timeout(self._host_kwargs_json)

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout
        return self._server.set_timeout(self._host_kwargs_json, timeout)
    
    def write(self, message, encoding='utf-8'):
        """ Write string to instrument """
        return self._server.write(self._host_kwargs_json, message, encoding)
