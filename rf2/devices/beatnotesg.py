import numpy as np
import time

class BEATNOTESG(object):
    _visa_address = 'USB0::0x1AB1::0x0641::DG4E212601193::INSTR'
#    _baud_rate = 9600
#    _write_termination = '\n'
#    _read_termination = '\n'
    _timeout = 5000
    
    _frequency_range = (0, 200e6)
    
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
    
    #Channel 1 for Beatnote RF,
    
    @property
    def freq1(self):
        """ return in Hz """
        command = ':SOUR1:APPL?'
        response = self._query_to_slot(command)
        response2 = response.rstrip('"')
        response3 = response2.split(",")
        return float(response3[1])
    
    @freq1.setter
    def freq1(self, request):
        """ freq in Hz """
        command = ':SOUR1:APPL:SIN {}, 2.5, 0, 0'.format(request)
        self._write_to_slot(command)
    
class BEATNOTESGProxy(BEATNOTESG):
    _visa_servername = 'visa'

    def __init__(self, cxn=None, **kwargs):
        from visa_server.proxy import VisaProxy
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global visa
        visa_server = cxn[self._visa_servername]
        visa = VisaProxy(visa_server)
        BEATNOTESG.__init__(self, **kwargs)
