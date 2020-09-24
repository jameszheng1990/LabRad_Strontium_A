from rf.devices.Moglabs_ARF.device import Moglabs_ARF

class MoglabsARF_689B(Moglabs_ARF):
    """ Two channel RF """
    autostart = True
    _vxi11_address = '192.168.1.33'
    _source = 2
    
    frequency_range = (20e6, 400e6)
    amplitude_range = (0, 31)
    fmgain_range = (0, 250e6)
    amgain_range = (0, 100)

    def initialize(self, config):
        super(MoglabsARF_689B, self).initialize(config)
        # self._write_to_slot('FM1:DEV 2e6')
        # self.set_amplitude(10)
        # self.set_state(True)

Device = MoglabsARF_689B
