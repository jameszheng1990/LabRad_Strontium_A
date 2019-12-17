from device_server.device import DefaultDevice
from visa_server.proxy import VisaProxy

class HPSignalGenerator(DefaultDevice):
    visa_servername = None
    visa_address = None
    
    state = None

    amplitude = None
    amplitude_range = None
    amplitude_units = 'dB'

    frequency = None
    frequency_range = None

    update_parameters = ['state', 'frequency', 'amplitude']

    def initialize(self, config):
        super(HPSignalGenerator, self).initialize(config)
        self.connect_to_labrad()

        self.visa_server = self.cxn[self.visa_servername]
        visa = VisaProxy(self.visa_server)
        rm = visa.ResourceManager()
        rm.open_resource(self.visa_address)
        self.visa = visa
        self.rm = rm

        self.do_update_parameters()

    def do_update_parameters(self):
        for parameter in self.update_parameters:
            getattr(self, 'get_{}'.format(parameter))()

    def set_state(self, state):
        command = 'OUTP:STAT {}'.format(int(bool(state)))
        self.rm.write(command)

    def get_state(self):
        ans = self.rm.query('OUTP:STAT?')
        return bool(int(ans))
    
    def set_frequency(self, frequency):
        command = 'FREQ:CW {} Hz'.format(frequency)
        self.rm.write(command)

    def get_frequency(self):
        ans = self.rm.query('FREQ:CW?')
        return float(ans) # keep things in MHz 

    def set_amplitude(self, amplitude):
        command = 'POW:AMPL {} {}'.format(amplitude, self.amplitude_units)
        self.rm.write(command)

    def get_amplitude(self):
        ans = self.rm.query('POW:AMPL?')
        return float(ans)

