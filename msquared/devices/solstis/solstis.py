import json
import os
import sys
sys.path.append(os.getenv('PROJECT_LABRAD_TOOLS_PATH'))

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread

from msquared.devices.solstis.msquared import MSquared

class Solstis(MSquared):
    etalon_tune = 0.
    resonator_tune = 0.
    resonator_fine_tune = 0.

    def set_system_status(self, value):
        pass

    def get_system_status(self):
        response = self.get('get_status')
        if response:
            for key, value in response.items():
                if (value == 'off'): 
                    response[key] = False
                if (value == 'on'): 
                    response[key] = True
            return json.dumps(response)
        else:
            return json.dumps({})
    
    def set_etalon_lock(self, value):
        self.set('etalon_lock', 
                       'on' if value else 'off', 
                       key_name='operation')

    def get_etalon_lock(self):
        response = self.get('etalon_lock_status')
        if response['condition'] == 'on':
            return True
        elif response['condition'] == 'off':
            return False
        elif response['condition'] == 'low' or 'error':
            return 'Etalon OFF due to error (i.e. low output)'
    
    def set_etalon_tune(self, value):
        percentage = sorted([0., float(value), 100.])[1]
        self.set('tune_etalon', percentage)
        self.etalon_tune = percentage

    def get_etalon_tune(self):
        response = self.get('get_status')
        try:
            return response['etalon_voltage']
        except:
            return 0
    
    def set_resonator_tune(self, value):
        percentage = sorted([0., float(value), 100.])[1]
        self.set('tune_resonator', percentage)
        self.resonator_tune = percentage

    def get_resonator_tune(self):
        response = self.get('get_status')
        try:
            return response['resonator_voltage']
        except:
            return 0

    def set_resonator_fine_tune(self, value):
        percentage = sorted([0., float(value), 100.])[1]
        self.set('fine_tune_resonator', percentage)
        self.resonator_fine_tune = percentage

    def get_resonator_fine_tune(self):
        response = self.get('get_status')
        try:
            return response['resonator_voltage']
        except:
            return 0

    def set_beam_alignment(self, mode):
        """
        Mode:
        1 - Manual
        2 - Auto
        3 - Stop
        4 - One Shot
        """
        mode = sorted([1, mode, 4])[1]
        self.set('beam_alignment', [mode],  # well.. WHY only accepts [int]
                       key_name='mode')
    
    def get_beam_alignment(self):
        response_json = self.get('get_alignment_status')
        response = json.loads(response_json)
        condition = response['message']['parameters']['condition']
        if condition == 'hold' or  condition == 'manual':
            return True
        elif condition == 'automatic':
            return False
        else:
            return False

    def set_x(self, value):
        value = sorted([0, value, 100])[1]
        self.set('beam_adjust_x', [value],
                 key_name = 'x_value')
        
    def get_x(self):
        response_json = self.get('get_alignment_status')
        response = json.loads(response_json)
        try:
            value = response['message']['parameters']['x_alignment'][0]
            return value
        except:
            return 0

    def set_y(self, value):
        value = sorted([0, value, 100])[1]
        self.set('beam_adjust_y', [value],
                 key_name = 'y_value')
        
    def get_y(self):
        response_json = self.get('get_alignment_status')
        response = json.loads(response_json)
        try:
            value = response['message']['parameters']['y_alignment'][0]
            return value
        except:
            return 0
        
    def set_wavelength(self, value):
        """
        Sets wavelength in nm by using the preset wavelength table,
        available from 696 to 877 nm.
        """
        value = sorted([696, value, 877])[1]
        self.set('move_wave_t', [value],
                 key_name = 'wavelength')
    
    def get_wavelength(self):
        response = self.get('get_status')
        try:
            return response['wavelength']
        except:
            return 0
        
        
        
        
        
        
        
        
        
        