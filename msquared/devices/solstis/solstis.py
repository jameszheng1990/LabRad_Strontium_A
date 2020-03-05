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
        if response:
            return response['condition'] == 'on'
        else:
            return False
    
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
        self.set('fine_tune_etalon', percentage)
        self.resonator_fine_tune = percentage

    def get_resonator_fine_tune(self):
        response = self.get('get_status')
        try:
            return response['resonator_voltage']
        except:
            return 0

