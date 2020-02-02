import numpy as np
import time

class RedAFG(object):
    _visa_address = 'USB0::0x0699::0x0358::C011390::INSTR'
    
    scaleRange = (0, 500)
    offsetRange = (-5, 5)
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'visa' not in globals():
            global visa
            import visa
        rm = visa.ResourceManager()
        self._inst = rm.open_resource(self._visa_address)

    def _write_to_slot(self, command):
        self._inst.write(command)
    
    def _query_to_slot(self, command):
        response = self._inst.query(command)
        return response.strip()
    
    #Channel 1 for 689-A, 2 for 689-B
    
    @property
    def scale1(self):
        command = 'SEQC:SOUR1:SCAL?'
        response = self._query_to_slot(command)
        return float(response)
    
    @scale1.setter
    def scale1(self, scale):
        min_scale = self.scaleRange[0]
        max_scale = self.scaleRange[1]
        scale = sorted([min_scale, scale, max_scale])[1]
        command = 'SEQC:SOUR1:SCAL {}'.format(scale)
        self._write_to_slot(command)

    @property
    def scale2(self):
        command = 'SEQC:SOUR2:SCAL?'
        response = self._query_to_slot(command)
        return float(response)
    
    @scale2.setter
    def scale2(self, scale):
        min_scale = self.scaleRange[0]
        max_scale = self.scaleRange[1]
        scale = sorted([min_scale, scale, max_scale])[1]
        command = 'SEQC:SOUR2:SCAL {}'.format(scale)
        self._write_to_slot(command)
        
class RedAFGProxy(RedAFG):
    _visa_servername = 'visa'

    def __init__(self, cxn=None, **kwargs):
        from visa_server.proxy import VisaProxy
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global visa
        visa_server = cxn[self._visa_servername]
        visa = VisaProxy(visa_server)
        RedAFG.__init__(self, **kwargs)
