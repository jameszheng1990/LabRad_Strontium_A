import numpy as np
import time

class BlueSlave1(object):
    _serial_port = 'COM6'
    _serial_baudrate = 38400
    _serial_timeout = 1
    _serial_termination = '\n'
    _current_range = (0.0, 140)
    _relock_stepsize = 0.1
    _locked_threshold = 0
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'serial' not in globals():
            global serial
            import serial
        self._ser = serial.Serial(self._serial_port)
        self._ser.timeout = self._serial_timeout
        self._ser.baudrate = self._serial_baudrate
        
    def _write_to_slot(self, command):
        self._ser.write(bytes(command+self._serial_termination, 'utf-8'))
    
    def _query_to_slot(self, command):
        self._ser.write(bytes(command+self._serial_termination, 'utf-8'))
        response = self._ser.readline()
        return response.decode("utf-8").strip()
    
    @property
    def current(self):
        command = 'LAS:LDI?'
        response = self._query_to_slot(command)
        return float(response)
        
    @current.setter
    def current(self, current):
        min_current = self._current_range[0]
        max_current = self._current_range[1]
        current = sorted([min_current, current, max_current])[1]
        command = 'LAS:LDI {}'.format(current)
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
        return float(response)

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
    
    @property
    def threshold(self):
        command = 'MESsage?'
        response = self._query_to_slot(command)
        return float(response)
    
    @threshold.setter
    def threshold(self, value):
        # Write to internal message buffer, to store the threshold.
        command = 'MESsage {}'.format(value)
        self._write_to_slot(command)

class BlueSlave1Proxy(BlueSlave1):
    _serial_servername = 'serial'

    def __init__(self, cxn=None, **kwargs):
        from serial_server.proxy import SerialProxy
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global serial
        serial = SerialProxy(cxn[self._serial_servername])
        BlueSlave1.__init__(self, **kwargs)
