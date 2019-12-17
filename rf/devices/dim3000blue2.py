class FrequencyOutOfBoundsError(Exception):
    def __init__(self, frequency, frequency_range):
        message = 'frequency {} is out of bounds {}.'.format(frequency, 
                                                                frequency_range)
        super(FrequencyOutOfBoundsError, self).__init__(message)

class AmplitudeOutOfBoundsError(Exception):
    def __init__(self, amplitude, amplitude_range):
        message = 'amplitude {} is out of bounds {}.'.format(amplitude, 
                                                                amplitude_range)
        super(AmplitudeOutOfBoundsError, self).__init__(message)


class DIM3000BLUE2(object):
    _serial_port = 'COM3'
    _serial_timeout = 0.5
    _serial_baudrate = 19200
    _serial_termination = '\n'
    
    _amplitude_range = (14, 34)
    _frequency_range = (1e3, 400e6)
    _fmdev_range = (0, 15)
    _fmfreq_range = (0, 3200*2**15)
        
    rf_state = False
    fm_state = False
    fm_dev = 5
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'serial' not in globals():
            global serial
            import serial
        self._ser = serial.Serial(self._serial_port)
        self._ser.timeout = self._serial_timeout
        self._ser.baudrate = self._serial_baudrate
        self.initialize(self.rf_state, self.fm_state, self.fm_dev)
    
    def initialize(self, rf_state, fm_state, fm_dev):
        if rf_state:
            self._write_to_slot('OUT_on')
        else:
            self._write_to_slot('OUT_off')
        
        if fm_state:
            self._write_to_slot('FM_on')
        else:
            self._write_to_slot('FM_off')
        
        self.set_fm_dev(fm_dev)
    
    def _write_to_slot(self, command):
        self._ser.write(bytes(command+self._serial_termination, 'utf-8'))
    
    def _query_to_slot(self, command):
        self._ser.write(bytes(command+self._serial_termination, 'utf-8'))
        response = self._ser.readline()
        return response.decode("utf-8").strip()
    
    @property
    def frequency(self):
        command = 'FRQ?'
        response = self._query_to_slot(command)
        return float(response)
   
    @frequency.setter
    def frequency(self, frequency):
        min_frequency = self._frequency_range[0]
        max_frequency = self._frequency_range[1]
        frequency = sorted([min_frequency, frequency, max_frequency])[1]
        command = 'FRQ:{}'.format(frequency)  # freq in MHz
        self._write_to_slot(command)
        
    @property
    def amplitude(self):
        command = 'AMP?'
        response = self._query_to_slot(command)
        return float(response)/10 # in dBm
    
    @amplitude.setter
    def amplitude(self, amplitude):
        min_amplitude = self._amplitude_range[0]
        max_amplitude = self._amplitude_range[1]
        amplitude = sorted([min_amplitude, amplitude, max_amplitude])[1]
        command = 'AMP:{}'.format(amplitude*10)  # amp in dBm
        self._write_to_slot(command)
        
    def set_fm_dev(self, fmdev):
        min_fmdev = self._fmdev_range[0]
        max_fmdev = self._fmdev_range[1]
        fmdev = sorted([min_fmdev, fmdev, max_fmdev])[1]
        command = 'FMdev:{}'.format(fmdev)
        self._write_to_slot(command)
    
    @property
    def fm(self):
        return self.fm_state
    
    @fm.setter
    def fm(self, state):
        if state == True:
            command = 'FM_on'
            self.fm_state = True
            
        else:
            command = 'FM_off'
            self.fm_state = False
        self._write_to_slot(command) 
    
    @property
    def state(self):
        return self.rf_state
    
    @state.setter
    def state(self, state):
        if state == True:
            command = 'OUT_on'
            self.rf_state = True
            
        else:
            command = 'OUT_off'
            self.rf_state = False
        self._write_to_slot(command)

class DIM3000BLUE2Proxy(DIM3000BLUE2):    
    _serial_servername = 'serial'

    def __init__(self, cxn=None, **kwargs):
        
        if cxn == None:
            import labrad, os
            cxn = labrad.connect(name=self.name, host=os.getenv('LABRADHOST') , password = '')
        from serial_server.proxy import SerialProxy
        global serial
        serial = SerialProxy(cxn[self._serial_servername])
        DIM3000BLUE2.__init__(self, **kwargs)
