import vxi11

from device_server.device import DefaultDevice

class AFG31052(DefaultDevice):
    vxi11_address = None

    waveforms = None
    timeout = 2

    update_parameters = []

    def initialize(self, config):
        ''' The followings will be loaded after server starts. '''
        super(AFG31052, self).initialize(config)
        self.vxi11 = vxi11.Instrument(self.vxi11_address)
        self.vxi11.timeout = self.timeout
        
        # ENTER SEQ MODE
        command = 'SEQC:STAT ON'
        self.vxi11.write(command)
        
        # Set sampling rate = 2 MS/s
        command = 'SEQC:SRAT 2E6'
        self.vxi11.write(command)
        
        # SET sequence run mode to Trigger mode
        command = 'SEQC:RMOD TRIG'
        self.vxi11.write(command)
        
        # SET external trigger for sequence-trigger mode, there is only 1 element in this mode
        command = 'SEQ:ELEM:TWA:EVEN EXT'
        self.vxi11.write(command)
        # SET rising edge for trigger input
        command = 'SEQ:ELEM:TWA:SLOP POS'
        self.vxi11.write(command)
        
        command = 'OUTP1:STAT ON'
        self.vxi11.write(command)
        command = 'OUTP2:STAT ON'
        self.vxi11.write(command)
        
        # LOAD waveforms lists from USB
        for waveform in self.waveforms: 
            command = 'WLIS:WAV:IMP "{}"'.format(waveform)
            self.vxi11.write(command)

    def set_waveform(self, source, waveform):
        if waveform not in self.waveforms:
            message = 'waveform "{}" not configured'.format(waveform)
            raise Exception(message)
        command = 'SEQ:ELEM:WAV{} "{}"'.format(source, waveform)
        self.vxi11.write(command)

    def get_waveform(self, source):
        command = 'SEQ:ELEM:WAV{}?'.format(source)
        ans = self.vxi11.ask(command)
        return ans

    def set_scale(self, source, scale):
        command = 'SEQC:SOUR{}:SCAL {}'.format(source, scale)
        self.vxi11.write(command)

    def get_scale(self, source):
        command = 'SEQC:SOUR{}:SCAL?'.format(source)
        ans = self.vxi11.ask(command)
        return ans
    
    def get_runstate(self):
        command = 'SEQC:RSTAT?'
        ans = self.vxi11.ask(command)
        if ans == '1':
            return True
        else:
            return False
    
    def run(self):
        command = 'SEQC:RUN'
        self.vxi11.write(command)
    
    def stop(self):
        command = 'SEQC:STOP'
        self.vxi11.write(command)