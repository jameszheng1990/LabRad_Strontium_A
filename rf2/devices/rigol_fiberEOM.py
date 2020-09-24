import numpy as np
import time

class FiberEOM_SG(object):
    
    _vxi11_address = '192.168.1.15'
    
    _frequency_range = (1e-3, 3e9)
    _amplitude_range = (0.0, 20.0)
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'vxi11' not in globals():
            global vxi11
            import vxi11
        self._inst = vxi11.Instrument(self._vxi11_address)
    
    @property
    def state(self):
        command = ':OUTPut?'
        ans = self._inst.ask(command)
        if float(ans) == 0:
            return False
        elif float(ans) == 1:
            return True
        else:
            pass
    
    @state.setter
    def state(self, state):
        if state == 1:    
            command = ':OUTPut ON'
            self._inst.write(command)
        elif state == 0:
            command = 'OUTPut OFF'
            self._inst.write(command)
        else:
            pass
    
    @property
    def frequency(self):
        command = ':FREQ?'
        ans = self._inst.ask(command)
        return float(ans)
    
    @frequency.setter
    def frequency(self, frequency):
        min_frequency = self._frequency_range[0]
        max_frequency = self._frequency_range[1]
        frequency = sorted([min_frequency, frequency, max_frequency])[1]
        command = ':FREQ {}'.format(frequency)
        self._inst.write(command)
    
    @property
    def amplitude(self):
        command = ':LEV?'
        ans = self._inst.ask(command)
        return float(ans)
    
    @amplitude.setter
    def amplitude(self, amplitude):
        min_amplitude = self._amplitude_range[0]
        max_amplitude = self._amplitude_range[1]
        amplitude = sorted([min_amplitude, amplitude, max_amplitude])[1]
        command = ':LEV {}dBm'.format(amplitude)
        self._inst.write(command)

class FiberEOMSGProxy(FiberEOM_SG):
    _vxi11_servername = 'vxi11'

    def __init__(self, cxn=None, **kwargs):
        from vxi11_server.proxy import Vxi11Proxy
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global vxi11
        vxi11_server = cxn[self._vxi11_servername]
        vxi11 = Vxi11Proxy(vxi11_server)
        FiberEOM_SG.__init__(self, **kwargs)
