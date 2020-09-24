import numpy as np
import time

class BEATNOTESG(object):
    # _visa_address = 'USB0::0x1AB1::0x0641::DG4E212601193::INSTR'
    _vxi11_address = '192.168.1.12'
    
    _timeout = 5000
    
    _frequency_range = (0, 200e6)
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'vxi11' not in globals():
            global vxi11
            import vxi11
        self._inst = vxi11.Instrument(self._vxi11_address)

    def _write_to_slot(self, command):
        self._inst.write(command)
    
    def _query_to_slot(self, command):
        response = self._inst.ask(command)
        return response
    
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
    
    # Channel 2 for Lattice depth modulations etc,
    
    @property
    def state2(self):
        command = ':OUTPut2?'
        ans = self._query_to_slot(command)
        if ans == 'OFF':
            return False
        elif ans == 'ON':
            return True
        else:
            pass
    
    @state2.setter
    def state2(self, state):
        if state == 1:    
            command = ':OUTPut2 ON'
            self._write_to_slot(command)
        elif state == 0:
            command = ':OUTPut2 OFF'
            self._write_to_slot(command)
        else:
            pass    
        
    @property
    def freq2(self):
        """ return in Hz """
        command = ':SOUR2:APPL?'
        response = self._query_to_slot(command)
        response2 = response.rstrip('"')
        response3 = response2.split(",")
        return float(response3[1])
    
    @freq2.setter
    def freq2(self, request):
        """ freq in Hz """
        # command = ':SOUR2:APPL:SIN {}, 2.5, 0, 0'.format(request)
        command = ':SOUR2:APPL:SIN {}'.format(request)
        self._write_to_slot(command)
        

    
class BEATNOTESGProxy(BEATNOTESG):
    _vxi11_servername = 'vxi11'

    def __init__(self, cxn=None, **kwargs):
        from vxi11_server.proxy import Vxi11Proxy
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global vxi11
        vxi11_server = cxn[self._vxi11_servername]
        vxi11 = Vxi11Proxy(vxi11_server)
        BEATNOTESG.__init__(self, **kwargs)
