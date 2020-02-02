from rf.devices.DIM3000.device import DIM3000

class AOM_689A(DIM3000):
    autostart = True
    
    _serial_port = 'COM8'

    frequency_range = (1e3, 400e6)
    amplitude_range = (14, 34)

    def initialize(self, config):
        super(AOM_689A, self).initialize(config)
        # self._write_to_slot('FM1:DEV 2e6')
        # self.set_amplitude(10)
        # self.set_state(True)

Device = AOM_689A
