from device_server.device import DefaultDevice
from moglabs_server.proxy import MoglabsProxy
from rf.devices.Moglabs_XRF.AdvancedTable_helper import EntryMaker
import json

class Moglabs_XRF(DefaultDevice):
    _vxi11_address = None
    _moglabs_servername = 'moglabs'
    _channel = None
    
    state = None

    amplitude = None
    amplitude_range = None
    amplitude_units = 'dBm'

    frequency = None
    frequency_range = None

    # update_parameters = ['state', 'frequency', 'amplitude']
    update_parameters = ['frequency', 'amplitude', 'table']

    def initialize(self, config):
        super(Moglabs_XRF, self).initialize(config)
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
            command = 'ON, {}'.format(self._channel)
            self._write_to_slot(command)
        else:
            command = 'OFF, {}'.format(self._channel)
            self._write_to_slot(command)

    def get_state(self):
        command = 'STATUS, {}'.format(self._channel)
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
        command = 'FREQ, {}, {} Hz'.format(self._channel, frequency)
        self._write_to_slot(command)

    def get_frequency(self):
        command = 'FREQ, {}'.format(self._channel)
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
        command = 'POWER, {}, {} dBm'.format(self._channel, amplitude)
        self._write_to_slot(command)

    def get_amplitude(self):
        command = 'POWER, {}'.format(self._channel)
        response = self._query_to_slot(command)
        response1 = response.split()[0]
        return float(response1)
    
    def set_table(self, request):
        """ set table mode request """
        entries = EntryMaker(request, self._channel).get_entries()
        for i in entries:
            self._write_to_slot(i)
    
    def get_table(self):
        """ get table mode entries """
        pass
        # entries = EntryMaker(request, self._channel).get_entries()
        # for i in entries:
        #     self._write_to_slot(i)
        