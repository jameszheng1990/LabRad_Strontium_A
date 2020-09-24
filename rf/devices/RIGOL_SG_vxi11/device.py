from device_server.device import DefaultDevice
from vxi11_server.proxy import Vxi11Proxy

class RIGOL_SG_vxi11(DefaultDevice):
    _vxi11_address = None
    _vxi11_servername = 'vxi11'
    
    timeout = 2
    
    state = None

    amplitude = None
    amplitude_range = None
    amplitude_units = 'dBm'

    frequency = None
    frequency_range = None

    # update_parameters = ['state', 'frequency', 'amplitude']
    update_parameters = ['frequency']

    def initialize(self, config):
        super(RIGOL_SG_vxi11, self).initialize(config)
        self.connect_to_labrad()
        
        vxi11_server = self.cxn[self._vxi11_servername]
        vxi11 = Vxi11Proxy(vxi11_server)
        self._inst = vxi11.Instrument(self._vxi11_address)
        self._inst.timeout = self.timeout
        
        self.do_update_parameters()

    def do_update_parameters(self):
        for parameter in self.update_parameters:
            getattr(self, 'get_{}'.format(parameter))()

    def _write_to_slot(self, command):
        self._inst.write(command)
    
    def _query_to_slot(self, command):
        response = self._inst.ask(command)
        return response
    
    def set_state(self, state):
        if state:
            command = 'OUTPut ON'
        else:
            command = 'OUTPut ON'
        self._write_to_slot(command)

    def get_state(self):
        ans = self._query_to_slot('OUTPut?')
        if ans == 'ON':
            return True
        elif ans == 'OFF':
            return False
    
    def set_frequency(self, frequency): # freq in Hz
        command = ':SOUR1:APPL:SIN {}, 2.5, 0, 0'.format(frequency)
        self._write_to_slot(command)

    def get_frequency(self):
        response1 = self._query_to_slot(':SOUR1:APPL?')
        response2 = response1.rstrip('"')
        response3 = response2.split(",")
        return float(response3[1])

    # def set_amplitude(self, amplitude): # amp in dBm *10
    #     command = 'AMP:{}'.format(amplitude)
    #     self._write_to_slot(command)

    # def get_amplitude(self):
    #     ans = self._query_to_slot('AMP?')
    #     return float(ans) 