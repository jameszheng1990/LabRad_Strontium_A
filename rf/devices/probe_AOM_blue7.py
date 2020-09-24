from rf.devices.RIGOL_SG.device import RIGOL_SG

class Probe_AO7(RIGOL_SG):
    autostart = True
    
    _visa_address = 'USB0::0x1AB1::0x0641::DG4E205003353::INSTR'
    # _vxi11_address = '192.168.1.12'

    frequency_range = (1, 200e6)
    amplitude_range = (0, 1)

    def initialize(self, config):
        super(Probe_AO7, self).initialize(config)
        # self._write_to_slot('FM1:DEV 2e6')
        # self.set_amplitude(10)
        # self.set_state(True)
        
    def set_frequency(self, frequency): # freq in Hz
        command = ':SOUR2:APPL:SIN {}'.format(frequency)
        self._write_to_slot(command)

    def get_frequency(self):
        response1 = self._query_to_slot(':SOUR2:APPL?')
        response2 = response1.rstrip('"')
        response3 = response2.split(",")
        return float(response3[1])
   
    def set_amplitude(self, amplitude): # amp in Vpp
        freq = self.get_frequency()
        command = ':SOUR2:APPL:SIN {}, {}'.format(freq, amplitude)
        self._write_to_slot(command)
        
    def get_amplitude(self):
        # command = ':SOUR2:APPL:SIN {}'.format(amplitude)
        # self._write_to_slot(command)
        pass
        
    def set_state(self, state):
        if state == True:    
            command = ':OUTPut2 ON'
            self._write_to_slot(command)
        elif state == False:
            command = ':OUTPut2 OFF'
            self._write_to_slot(command)
        else:
            pass
    
    def get_state(self):
        ans = self._query_to_slot(':OUTPut2?')
        if ans == 'ON':
            return True
        elif ans == 'OFF':
            return False

Device = Probe_AO7