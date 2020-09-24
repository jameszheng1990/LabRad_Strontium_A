import numpy as np
import time

class Moglabs_XRF(object):
    _vxi11_address = '192.168.1.13'
    
    _frequency_range = (20e6, 400e6)
    _amplitude_range = (0, 33)
    _fmgain_range = (0, 250e6)
    _amgain_range = (0, 100)
    
    _timeout = 5000
    _source1 = 1
    _source2 = 2
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'moglabs' not in globals():
            global moglabs
            import moglabs
        self._dev = moglabs.Device(self._vxi11_address)
        self.initialize()

    def _write_to_slot(self, command):
        self._dev.write(command)
    
    def _query_to_slot(self, command):
        response = self._dev.ask(command)
        return response
    
    def initialize(self):
        # Set to 10 MHz ext clock
        clk = self._query_to_slot('CLKSRC')
        if 'INTERNAL' in clk:
            self._write_to_slot('CLKSRC, EXT, 100')
        
        # Enter TPA mode
        self._write_to_slot('MODE, 1, TPA')
        self._write_to_slot('TABLE, CLEAR, 1')
        self._write_to_slot('MODE, 2, TPA')
        self._write_to_slot('TABLE, CLEAR, 2')
        
        # # Enable output
        # self.rf_state1 = True
        # self.rf_state2 = False
        
        # # Enable TTL
        # self._write_to_slot('EXTIO, MODE, 1, OFF, TOGGLE')
        # self._write_to_slot('EXTIO, DISABLE, 1, OFF') # TODO, enable
        # self._write_to_slot('EXTIO, MODE, 2, OFF, TOGGLE')
        # self._write_to_slot('EXTIO, DISABLE, 2, OFF')
    
    ##############
    
    @property
    def rf_state1(self):
        command = 'STATUS, {}'.format(self._source1)
        response = self._query_to_slot(command)
        if 'POW: ON' in response:
            return True
        else:
            return False
        
    @rf_state1.setter
    def rf_state1(self, boolean):
        if boolean:
            command = 'ON, {}'.format(self._source1)
            self._write_to_slot(command)
        else:
            command = 'OFF, {}'.format(self._source1)
            self._write_to_slot(command)
            
    @property
    def frequency1(self):
        command = 'FREQ, {}'.format(self._source1)
        response = self._query_to_slot(command)
        response1 = float(response.split()[0])
        units = response.split()[1]
        if units == 'MHz':
            response2 = response1*1e6
        else:
            response2 = response1
        return response2
    
    @frequency1.setter
    def frequency1(self, frequency):
        """ frequency in Hz """
        min_frequency = self._frequency_range[0]
        max_frequency = self._frequency_range[1]
        frequency = sorted([min_frequency, frequency, max_frequency])[1]
        command = 'FREQ, {}, {} Hz'.format(self._source1, frequency)
        self._write_to_slot(command)
        
    @property
    def amplitude1(self):
        command = 'POWER, {}'.format(self._source1)
        response = self._query_to_slot(command)
        response1 = response.split()[0]
        return float(response1)
    
    @amplitude1.setter
    def amplitude1(self, amplitude):
        """ amplitude in dBm """
        min_amplitude = self._amplitude_range[0]
        max_amplitude = self._amplitude_range[1]
        amplitude = sorted([min_amplitude, amplitude, max_amplitude])[1]
        command = 'POW, {}, {} dBm'.format(self._source1, amplitude)
        self._write_to_slot(command)
    
    #####################
        
    @property
    def rf_state2(self):
        command = 'STATUS, {}'.format(self._source2)
        response = self._query_to_slot(command)
        if 'POW: ON' in response:
            return True
        else:
            return False
        
    @rf_state2.setter
    def rf_state2(self, boolean):
        if boolean:
            command = 'ON, {}'.format(self._source2)
            self._write_to_slot(command)
        else:
            command = 'OFF, {}'.format(self._source2)
            self._write_to_slot(command)
            
    @property
    def frequency2(self):
        command = 'FREQ, {}'.format(self._source2)
        response = self._query_to_slot(command)
        response1 = float(response.split()[0])
        units = response.split()[1]
        if units == 'MHz':
            response2 = response1*1e6
        else:
            response2 = response1
        return response2
    
    @frequency2.setter
    def frequency2(self, frequency):
        """ frequency in Hz """
        min_frequency = self._frequency_range[0]
        max_frequency = self._frequency_range[1]
        frequency = sorted([min_frequency, frequency, max_frequency])[1]
        command = 'FREQ, {}, {} Hz'.format(self._source2, frequency)
        self._write_to_slot(command)
        
    @property
    def amplitude2(self):
        command = 'POWER, {}'.format(self._source2)
        response = self._query_to_slot(command)
        response1 = response.split()[0]
        return float(response1)
    
    @amplitude2.setter
    def amplitude2(self, amplitude):
        """ amplitude in dBm """
        min_amplitude = self._amplitude_range[0]
        max_amplitude = self._amplitude_range[1]
        amplitude = sorted([min_amplitude, amplitude, max_amplitude])[1]
        command = 'POWER, {}, {} dBm'.format(self._source2, amplitude)
        self._write_to_slot(command)
        
class MoglabsXRFProxy(Moglabs_XRF):
    _moglabs_servername = 'moglabs'

    def __init__(self, cxn=None, **kwargs):
        from moglabs_server.proxy import MoglabsProxy
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global moglabs
        moglabs_server = cxn[self._moglabs_servername]
        moglabs = MoglabsProxy(moglabs_server)
        Moglabs_XRF.__init__(self, **kwargs)
