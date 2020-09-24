import numpy as np
import time

class Repump_SG(object):
    # _visa_address = 'USB0::0x1AB1::0x0642::DG1ZA201701875::INSTR'
    # _visa_address = 'USB0::0x1AB1::0x0643::DG8A212801146::INSTR'
    
    _vxi11_address = '192.168.1.11'
    
    _baud_rate = 9600
    _write_termination = '\n'
    _read_termination = '\n'
    _timeout = 5000
    _source1 = 1
    _source2 = 2
    
    _dc_v_range = (0, 2.5)
    _ramp_freq_range = (0, 10e3)
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'vxi11' not in globals():
            global vxi11
            import vxi11
        self._inst = vxi11.Instrument(self._vxi11_address)
        self.output()

    def _write_to_slot(self, command):
        self._inst.write(command)
    
    def _query_to_slot(self, command):
        response = self._inst.ask(command)
        return response
    
    def output(self):
        command1 = ':OUTP{} ON'.format(self._source1)
        command2 = ':OUTP{} ON'.format(self._source2)
        self._write_to_slot(command1)
        self._write_to_slot(command2)
    
    #Channel 1 for 679 nm, channel 2 for 707 nm
    
    @property
    def shape1(self):
        command = ':SOUR{}:FUNC?'.format(self._source1)
        response = self._query_to_slot(command)
        if response == 'DC':
            return True
        else:
            return False
        
    @shape1.setter
    def shape1(self, boolean):
        if boolean:
            command = ':SOUR{}:FUNC DC'.format(self._source1)
            self._write_to_slot(command)
        else:
            command = ':SOUR{}:FUNC RAMP'.format(self._source1)
            self._write_to_slot(command)
    
    @property
    def dc1(self):
        command = ':SOUR{}:APPL?'.format(self._source1)
        response = self._query_to_slot(command)
        response2 = response.rstrip('"').lstrip('"')
        response3 = response2.split(",")
        return float(response3[-1])
    
    @dc1.setter
    def dc1(self, request):
        min_v = self._dc_v_range[0]
        max_v = self._dc_v_range[1]
        request = sorted([min_v, request, max_v])[1]
        command = ':SOUR{}:APPL:DC DEF,DEF,{}'.format(self._source1, request)
        self._write_to_slot(command)
        
    @property
    def ramp1(self):
        command = ':SOUR{}:APPL?'.format(self._source1)
        response = self._query_to_slot(command)
        response2 = response.rstrip('"').lstrip('"')
        response3 = response2.split(",")
        return float(response3[1]), float(response3[2]), float(response3[3])
    
    @ramp1.setter
    def ramp1(self, request):
        freq = request[0]
        min_freq = self._ramp_freq_range[0]
        max_freq = self._ramp_freq_range[1]
        freq = sorted([min_freq, freq, max_freq])[1]
        
        amp = request[1]
        offset = request[2]
        command = ':SOUR{}:APPL:RAMP {},{},{},0'.format(self._source1, freq, amp, offset)
        self._write_to_slot(command)
        
    @property
    def shape2(self):
        command = ':SOUR{}:FUNC?'.format(self._source2)
        response = self._query_to_slot(command)
        if response == 'DC':
            return True
        else:
            return False
        
    @shape2.setter
    def shape2(self, boolean):
        if boolean:
            command = ':SOUR{}:FUNC DC'.format(self._source2)
            self._write_to_slot(command)
        else:
            command = ':SOUR{}:FUNC RAMP'.format(self._source2)
            self._write_to_slot(command)
    
    @property
    def dc2(self):
        command = ':SOUR{}:APPL?'.format(self._source2)
        response = self._query_to_slot(command)
        response2 = response.rstrip('"').lstrip('"')
        response3 = response2.split(",")
        return float(response3[-1])
    
    @dc2.setter
    def dc2(self, request):
        min_v = self._dc_v_range[0]
        max_v = self._dc_v_range[1]
        request = sorted([min_v, request, max_v])[1]
        command = ':SOUR{}:APPL:DC DEF,DEF,{}'.format(self._source2, request)
        self._write_to_slot(command)
        
    @property
    def ramp2(self):
        command = ':SOUR{}:APPL?'.format(self._source2)
        response = self._query_to_slot(command)
        response2 = response.rstrip('"').lstrip('"')
        response3 = response2.split(",")
        return float(response3[1]), float(response3[2]), float(response3[3])
    
    @ramp2.setter
    def ramp2(self, request):
        freq = request[0]
        min_freq = self._ramp_freq_range[0]
        max_freq = self._ramp_freq_range[1]
        freq = sorted([min_freq, freq, max_freq])[1]
        
        amp = request[1]
        offset = request[2]
        command = ':SOUR{}:APPL:RAMP {},{},{},0'.format(self._source2, freq, amp, offset)
        self._write_to_slot(command)
        
class RepumpSGProxy(Repump_SG):
    _vxi11_servername = 'vxi11'

    def __init__(self, cxn=None, **kwargs):
        from vxi11_server.proxy import Vxi11Proxy
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global vxi11
        vxi11_server = cxn[self._vxi11_servername]
        vxi11 = Vxi11Proxy(vxi11_server)
        Repump_SG.__init__(self, **kwargs)
