from rf.devices.RIGOL_SG.device import RIGOL_SG

class Beatnote_689(RIGOL_SG):
    autostart = True
    
    _visa_address = 'USB0::0x1AB1::0x0641::DG4E212601193::INSTR'

    frequency_range = (1, 200e6)

    def initialize(self, config):
        super(Beatnote_689, self).initialize(config)
        # self._write_to_slot('FM1:DEV 2e6')
        # self.set_amplitude(10)
        # self.set_state(True)

Device = Beatnote_689