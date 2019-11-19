import numpy as np
import time

class BlueSlave3(object):
    _visa_address = 'ASRL4::INSTR'
    _baud_rate = 38400
    _write_termination = '\n'
    _read_termination = '\n'
    _current_range = (0.0, 140)
    _relock_stepsize = 0.1
    _locked_threshold = 0
    _scani = 132
    _scanf = 128
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'pyvisa' not in globals():
            global pyvisa
            import pyvisa
        rm = pyvisa.ResourceManager()
        self._inst = rm.open_resource(self._visa_address)
        self._inst.baud_rate = self._baud_rate
        self._inst.write_termination = self._write_termination
        self._inst.read_termination = self._read_termination

    def _write_to_slot(self, command):
        self._inst.write(command)
    
    def _query_to_slot(self, command):
        response = self._inst.query(command)
        return response
    
    @property
    # Used as: read-current = xxx().current #
    def current(self):
        command = 'LAS:LDI?'
        response = self._query_to_slot(command)
        return float(response)
    
    @current.setter
    # Used as: xxx.current = current set-point #
    def current(self, request):
        min_current = self._current_range[0]
        max_current = self._current_range[1]
        request = sorted([min_current, request, max_current])[1]
        command = 'LAS:LDI {}'.format(request)
        self._write_to_slot(command)
    
    @property
    def is_locked(self):
        if self.moncurrent > self._locked_threshold:
            return True
        else:
            return False
    
    @property
    def moncurrent(self):
        command = 'LAS:MDI?'
        response = self._query_to_slot(command)
        moncurrent = float(response)
        return moncurrent

    @property
    def state(self):
        command = 'LAS:OUT?'
        response = self._query_to_slot(command)
        if response.strip() == '1':
            return True
        elif response.strip() == '0':
            return False

    @state.setter
    def state(self, state):
        if state:
            command = 'LAS:OUT 1'
        else:
            command = 'LAS:OUT 0'
        self._write_to_slot(command)
    
    def relock(self):
        current = self.current
        self.current = current + self._relock_stepsize
        time.sleep(0.2)
        self.current = current

class BlueSlave3Proxy(BlueSlave3):
    _visa_servername = 'visa'

    def __init__(self, cxn=None, **kwargs):
        from visa_server.proxy import VisaProxy
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global visa
        visa_server = cxn[self._visa_servername]
        visa = VisaProxy(visa_server)
        BlueSlave3.__init__(self, **kwargs)
