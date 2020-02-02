from device_server.device import DefaultDevice
from visa_server.proxy import VisaProxy

class RIGOL_SG(DefaultDevice):
    _visa_servername = 'visa'
    _visa_address = None
    _visa_timeout = 1
    
    state = None

    amplitude = None
    amplitude_range = None
    amplitude_units = 'dBm'

    frequency = None
    frequency_range = None

    # update_parameters = ['state', 'frequency', 'amplitude']
    update_parameters = ['frequency']

    def initialize(self, config):
        super(RIGOL_SG, self).initialize(config)
        self.connect_to_labrad()
        
        visa_server = self.cxn[self._visa_servername]
        visa = VisaProxy(visa_server)
        rm = visa.ResourceManager()
        self._inst = rm.open_resource(self._visa_address)
        
        self.do_update_parameters()

    def do_update_parameters(self):
        for parameter in self.update_parameters:
            getattr(self, 'get_{}'.format(parameter))()

    def _write_to_slot(self, command):
        self._inst.write(command)
    
    def _query_to_slot(self, command):
        response = self._inst.query(command)
        return response.strip()
    
    # def set_state(self, state):
    #     if state:
    #         command = 'OUT_on'
    #     else:
    #         command = 'OUT_off'
    #     self._write_to_slot(command)

    # def get_state(self):
    #     # ans = self.rm.query('OUTP:STAT?')
    #     # return bool(int(ans))
    #     return True
    
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