import numpy as np
import time

class RedAFG(object):
    _vxi11_address = '192.168.1.23'
    
    scaleRange = (0, 500)
    offsetRange = (-5, 5)
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'vxi11' not in globals():
            global vxi11
            import vxi11
        self._inst = vxi11.Instrument(self._vxi11_address)

    #Channel 1 for 689-A, 2 for 689-B
    
    @property
    def stop(self):
        pass
    
    @stop.setter
    def stop(self, c):
        command = 'SEQC:STOP'
        self._inst.write(command)
        
    @property
    def run(self):
        pass
    
    @run.setter
    def run(self, c):
        command = 'SEQC:RUN'
        self._inst.write(command)
    
    @property
    def scale1(self):
        command = 'SEQC:SOUR1:SCAL?'
        response = self._inst.ask(command)
        return float(response)
    
    @scale1.setter
    def scale1(self, scale):
        min_scale = self.scaleRange[0]
        max_scale = self.scaleRange[1]
        scale = sorted([min_scale, scale, max_scale])[1]
        command = 'SEQC:SOUR1:SCAL {}'.format(scale)
        self._inst.write(command)

    @property
    def scale2(self):
        command = 'SEQC:SOUR2:SCAL?'
        response = self._inst.ask(command)
        return float(response)
    
    @scale2.setter
    def scale2(self, scale):
        min_scale = self.scaleRange[0]
        max_scale = self.scaleRange[1]
        scale = sorted([min_scale, scale, max_scale])[1]
        command = 'SEQC:SOUR2:SCAL {}'.format(scale)
        self._inst.write(command)
        
class RedAFGProxy(RedAFG):
    _vxi11_servername = 'vxi11'

    def __init__(self, cxn=None, **kwargs):
        from vxi11_server.proxy import Vxi11Proxy
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global vxi11
        vxi11_server = cxn[self._vxi11_servername]
        vxi11 = Vxi11Proxy(vxi11_server)
        RedAFG.__init__(self, **kwargs)
