import numpy as np
import time

from wavemeter_lock.devices.hf_wlm_binding import HFWavemeterBinding

class HF_WLM(object):
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        binding = HFWavemeterBinding()
        self.binding = binding

    def get_frequency(self, channel):
        """
        Gets the frequency of a channel
        """
       
        try:
            frequency = self.binding.get_frequency_num(channel)
            return frequency * 1e3; # in GHz
        except Exception as e:
            return self.handle_wavemeter_error(e)

    def get_wavelength(self, channel):
        """
        Gets the wavelength (vacuum) of a channel

        This setting tries to guess the active channel unless in multiplex mode
        """
  
        try:
            wavelength = self.binding.get_wavelength_num(channel)
            return wavelength;  # in nm
        except Exception as e:
#            return self.handle_wavemeter_error(e)
            return 0
    
    
    def handle_wavemeter_error(self, e):
        print('(wavemeter) error: %s' % e)
        return None
 
    
class HFWLMProxy(HF_WLM):
    _visa_servername = 'visa'

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        HF_WLM.__init__(self, **kwargs)
