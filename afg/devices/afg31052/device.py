import pyvisa

from device_server.device import DefaultDevice

class AFG31052(DefaultDevice):
    visa_address = None
    source = None

    waveforms = None

    update_parameters = []

    def initialize(self, config):
        ''' The followings will be loaded after server starts. '''
        super(AFG31052, self).initialize(config)
        rm = pyvisa.ResourceManager()
        self._inst = rm.open_resource(self.visa_address)
        
        # ENTER SEQ MODE
        command = 'SEQC:STAT ON'
        self._inst.write(command)
        
        # Set sampling rate = 2 MS/s
        command = 'SEQC:SRAT 2E6'
        self._inst.write(command)
        
        # SET sequence run mode to Trigger mode
        command = 'SEQC:RMOD TRIG'
        self._inst.write(command)
        
        # SET external trigger for sequence-trigger mode, there is only 1 element in this mode
        command = 'SEQ:ELEM:TWA:EVEN EXT'
        self._inst.write(command)
        # SET rising edge for trigger input
        command = 'SEQ:ELEM:TWA:SLOP POS'
        self._inst.write(command)
        
        command = 'OUTP{}:STAT ON'.format(self.source)
        self._inst.write(command)
        
        # LOAD waveforms lists from USB
        for waveform in self.waveforms: 
            command = 'WLIS:WAV:IMP "{}"'.format(waveform)
            self._inst.write(command)

    def set_waveform(self, waveform):
        if waveform not in self.waveforms:
            message = 'waveform "{}" not configured'.format(waveform)
            raise Exception(message)
        command = 'SEQ:ELEM:WAV{} "{}"'.format(self.source, waveform)
        self._inst.write(command)

    def get_waveform(self):
        command = 'SEQ:ELEM:WAV{}?'.format(self.source)
        ans = self._inst.query(command)
        return ans.strip()
    
    def get_runstate(self):
        command = 'SEQC:RSTAT?'
        ans = self._inst.query(command).strip()
        if ans == '1':
            return True
        else:
            return False
    
    def run(self):
        command = 'SEQC:RUN'
        self._inst.write(command)
    
    def stop(self):
        command = 'SEQ:STOP'
        self._inst.write(command)