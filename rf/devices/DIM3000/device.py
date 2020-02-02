from device_server.device import DefaultDevice
from serial_server.proxy import SerialProxy

class DIM3000(DefaultDevice):
    _serial_servername = 'serial'
    _serial_port = None
    _serial_timeout = 0.5
    _serial_baudrate = 19200
    _serial_termination = '\n'
    
    state = None

    amplitude = None
    amplitude_range = None
    amplitude_units = 'dB'

    frequency = None
    frequency_range = None

    # update_parameters = ['state', 'frequency', 'amplitude']
    update_parameters = ['frequency']

    def initialize(self, config):
        super(DIM3000, self).initialize(config)
        self.connect_to_labrad()

        self.serial_server = self.cxn[self._serial_servername]
        serial = SerialProxy(self.serial_server)
        
        self._ser = serial.Serial(self._serial_port)
        self._ser.timeout = self._serial_timeout
        self._ser.baudrate = self._serial_baudrate
        
        self.do_update_parameters()

    def do_update_parameters(self):
        for parameter in self.update_parameters:
            getattr(self, 'get_{}'.format(parameter))()

    def _write_to_slot(self, command):
        self._ser.write(bytes(command+self._serial_termination, 'utf-8'))
    
    def _query_to_slot(self, command):
        self._ser.write(bytes(command+self._serial_termination, 'utf-8'))
        response = self._ser.readline()
        return response.decode("utf-8").strip()
    
    def set_state(self, state):
        if state:
            command = 'OUT_on'
        else:
            command = 'OUT_off'
        self._write_to_slot(command)

    def get_state(self):
        # ans = self.rm.query('OUTP:STAT?')
        # return bool(int(ans))
        return True
    
    def set_frequency(self, frequency): # freq in Hz
        command = 'FRQ:{}'.format(frequency)
        self._write_to_slot(command)

    def get_frequency(self):
        ans = self._query_to_slot('FRQ?')
        return float(ans) # keep things in MHz 

    def set_amplitude(self, amplitude): # amp in dBm *10
        command = 'AMP:{}'.format(amplitude)
        self._write_to_slot(command)

    def get_amplitude(self):
        ans = self._query_to_slot('AMP?')
        return float(ans) 