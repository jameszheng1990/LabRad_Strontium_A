from device_server.device import DefaultDevice
from moglabs_server.proxy import MoglabsProxy

class Moglabs_ARF(DefaultDevice):
    _vxi11_address =None
    _moglabs_servername = 'moglabs'
    _source = None
    
    state = None

    amplitude = None
    amplitude_range = None
    amplitude_units = 'dBm'

    frequency = None
    frequency_range = None
    
    fmgain = None
    fmgain_range = None

    # update_parameters = ['state', 'frequency', 'amplitude']
    update_parameters = ['frequency', 'amplitude', 'fm_gain']

    def initialize(self, config):
        super(Moglabs_ARF, self).initialize(config)
        self.connect_to_labrad()

        moglabs_server = self.cxn[self._moglabs_servername]
        moglabs = MoglabsProxy(moglabs_server)
        self._dev = moglabs.Device(self._vxi11_address)
        
        self.do_update_parameters()

    def do_update_parameters(self):
        for parameter in self.update_parameters:
            getattr(self, 'get_{}'.format(parameter))()

    def _write_to_slot(self, command):
        self._dev.write(command)
    
    def _query_to_slot(self, command):
        response = self._dev.ask(command)
        return response
    
    def set_state(self, state):
        if state:
            command = 'ON, {}'.format(self._source)
            self._write_to_slot(command)
        else:
            command = 'OFF, {}'.format(self._source)
            self._write_to_slot(command)

    def get_state(self):
        command = 'STATUS, {}'.format(self._source)
        response = self._query_to_slot(command)
        if 'POW: ON' in response:
            return True
        else:
            return False
    
    def set_frequency(self, frequency): # freq in Hz
        """ frequency in Hz """
        min_frequency = self.frequency_range[0]
        max_frequency = self.frequency_range[1]
        frequency = sorted([min_frequency, frequency, max_frequency])[1]
        command = 'FREQ, {}, {} Hz'.format(self._source, frequency)
        self._write_to_slot(command)

    def get_frequency(self):
        command = 'FREQ, {}'.format(self._source)
        response = self._query_to_slot(command)
        response1 = float(response.split()[0])
        units = response.split()[1]
        if units == 'MHz':
            response2 = response1*1e6
        else:
            response2 = response1
        return response2

    def set_amplitude(self, amplitude):
        """ amplitude in dBm """
        min_amplitude = self.amplitude_range[0]
        max_amplitude = self.amplitude_range[1]
        amplitude = sorted([min_amplitude, amplitude, max_amplitude])[1]
        command = 'POWER, {}, {} dBm'.format(self._source, amplitude)
        self._write_to_slot(command)

    def get_amplitude(self):
        command = 'POWER, {}'.format(self._source)
        response = self._query_to_slot(command)
        response1 = response.split()[0]
        return float(response1)
    
    def set_fm_gain(self, gain):
        """ Gain in Hz/V """
        min_gain = self.fmgain_range[0]
        max_gain = self.fmgain_range[1]
        gain = sorted([min_gain, gain, max_gain])[1]
        command = 'GAIN, {},FREQ, {} Hz'.format(self._source, gain)
        self._write_to_slot(command)
        
    def get_fm_gain(self):
        """ Gain retuen in Hz/V """
        command = 'GAIN, {}, FREQ'.format(self._source)
        response = self._query_to_slot(command)
        response1 = float(response.split()[0])
        units = response.split()[1]
        if units == 'MHz':
            response2 = response1*1e6
        elif units == 'kHz':
            response2 = response1*1e3
        else:
            response2 = response1
        return response2        
        