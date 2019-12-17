import numpy as np
import time

class RepumpSG(object):
    _visa_address = 'USB0::0x1AB1::0x0642::DG1ZA201701875::INSTR'
#    _baud_rate = 9600
#    _write_termination = '\n'
#    _read_termination = '\n'
    _v_range = (0, 2.5)
    _timeout = 5000
    
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
    
    #Channel 1 for 679 nm, channel 2 for 707 nm
    
    @property
    def dc1(self):
        command = ':SOUR1:APPL?'
        response = self._query_to_slot(command)
        response2 = response.rstrip('"')
        response3 = response2.split(",")
        return float(response3[-1])
    
    @dc1.setter
    def dc1(self, request):
        min_v = self._v_range[0]
        max_v = self._v_range[1]
        request = sorted([min_v, request, max_v])[1]
        command = ':SOUR1:APPL:DC DEF,DEF,{}'.format(request)
        self._write_to_slot(command)
        
    @property
    def dc2(self):
        command = ':SOUR2:APPL?'
        response = self._query_to_slot(command)
        response2 = response.rstrip('"')
        response3 = response2.split(",")
        return float(response3[-1])
    
    @dc2.setter
    def dc2(self, request):
        min_v = self._v_range[0]
        max_v = self._v_range[1]
        request = sorted([min_v, request, max_v])[1]
        command = ':SOUR2:APPL:DC DEF,DEF,{}'.format(request)
        self._write_to_slot(command)
    
class RepumpSGProxy(RepumpSG):
    _visa_servername = 'visa'

    def __init__(self, cxn=None, **kwargs):
        from visa_server.proxy import VisaProxy
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global visa
        visa_server = cxn[self._visa_servername]
        visa = VisaProxy(visa_server)
        RepumpSG.__init__(self, **kwargs)
