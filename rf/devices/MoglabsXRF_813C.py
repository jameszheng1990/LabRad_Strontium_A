from rf.devices.Moglabs_XRF.device import Moglabs_XRF

class MoglabsARF_813C(Moglabs_XRF):
    """ Two channel RF, for 813C, accelerating lattice """
    autostart = True
    _vxi11_address = '192.168.1.13'
    _channel = 1
    
    frequency_range = (20e6, 400e6)
    amplitude_range = (0, 31)
    fmgain_range = (0, 250e6)
    amgain_range = (0, 100)

    def initialize(self, config):
        super(MoglabsARF_813C, self).initialize(config)
        # self._write_to_slot('FM1:DEV 2e6')
        # self.set_amplitude(10)
        # self.set_state(True)

Device = MoglabsARF_813C
