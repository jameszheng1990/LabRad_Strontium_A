import json, os

class UpdateProxy(object):
    def __init__(self, name):
        import labrad
        cxn = labrad.connect(host=os.getenv('LABRADHOST'), password='')
        self._server = cxn.update
        self.name = name
        self._server.register(name)

    def emit(self, message_json):
        self._server.emit(self.name, json.dumps(message_json))
