import numpy as np
import time

class RedAFG(object):
    _visa_address = 'USB0::0x0699::0x0358::C011390::INSTR'

    _v_range = (-10, 10)         # in V
    _symmetry_range = (0, 100)
    _phase_range = (-180, 180)   # in Degree
    _rate_range = (0, 800)  # in kHz
    _duration_range = (0, 10000)  # in ms
    
    _v_high1 = None
    _v_low1 = None
    _symmetry1 = None
    _phase1 = None    # 90: starting from VH
    _rate1 = None   # in kHz
    _duration1 = None  # in ms
    
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
    
    def configure1(self, v_high, v_low, symmetry, phase, rate, duration):
        self.set_ramp1(v_high, v_low, symmetry, phase, rate)
        self.set_burst_trigger_mode1(duration, rate)
        self._write_to_slot('OUTPut1:STATe ON')
    
    def set_ramp1(self, v_high, v_low, symmetry, phase, rate):
        v_high      = sorted([self._v_range[0],  v_high, v_low,  self._v_range[1]])[2]
        v_low       = sorted([self._v_range[0],  v_high, v_low,  self._v_range[1]])[1]
        symmetry    = sorted([self._symmetry_range[0], symmetry, self._symmetry_range[1]])[1]
        phase       = sorted([self._phase_range[0],    phase,    self._phase_range[1]])[1]
         
        self._write_to_slot('SOURce1:FUNCtion:SHAPe RAMP')
        self._write_to_slot('SOURce1:VOLTage:LEVel:IMMediate:HIGH {}V'.format(v_high))
        self._write_to_slot('SOURce1:VOLTage:LEVel:IMMediate:LOW {}V'.format(v_low))
        self._write_to_slot('SOURce1:FUNCtion:RAMP:SYMMetry {}'.format(symmetry))
        self._write_to_slot('SOURce1:PHASe:ADJust {}DEG'.format(phase))
        self._write_to_slot('SOURce1:FREQuency:FIXed {}kHz'.format(rate))
        
    def set_burst_trigger_mode1(self, duration, rate):
        self._write_to_slot('SOURce1:BURSt:MODE TRIGgered')
        self._write_to_slot('SOURce1:BURSt:IDLE END')
        self._write_to_slot('TRIGger:SEQuence:SOURce EXTernal')
        cycles = int(duration*rate)  # Max Cycles: 1e6
        self._write_to_slot('SOURce1:BURSt:NCYCles {}'.format(cycles))
        
    
#    def set_duration(self, t):
#        t = 
    
#    def ramp1(self, vi, vf, rate, )
    
    
    
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
