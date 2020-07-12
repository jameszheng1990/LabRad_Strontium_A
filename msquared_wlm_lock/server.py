"""
### BEGIN NODE INFO
[info]
name = msquared_wlm_lock
version = 1.0
description = 
instancename = msquared_wlm_lock
[startup]
cmdline = %PYTHON% %FILE%
timeout = 20
[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from labrad.server import LabradServer, setting
from twisted.internet import task, defer, reactor
import os
import json
import numpy as np
from lib.pid import PID
import sys
from datetime import datetime
from time import time
from labrad.server import Signal

class MSquaredWLMLockServer(LabradServer):
    """
    Wavelength meter lock LabRAD server for the M-squared laser
    """
    name = 'msquared_wlm_lock'
    UPDATE_ID = 698055
    update = Signal(UPDATE_ID, 'signal: update', 's')  # on listener: signal__update
    
    frquency_units = ['Hz', 'kHz', 'MHz', 'GHz', 'THz']
    wavelength_units = ['nm', 'um']
    
    def __init__(self, config_path='./config.json'):
        self.is_locked = False
        self.task_state = False
        # self.lock_status = False
        # self.name = '{}_wlm_lock'.format(self.config['lock_name'])
        
        self.config = self.load_config(config_path)
        self.wlm_name = self.config['wlm_name']
        self.msquared_name = self.config['msquared_name']
        self.log_path = self.config['log_path']
        
        pid_config = self.config['pid']
        self.pid = PID(overall_gain=pid_config['overall_gain'],
                  prop_gain=pid_config['prop_gain'],
                  int_gain=pid_config['int_gain'],
                  diff_gain=pid_config['diff_gain'],
                  min_max=pid_config['range'],
                  offset=pid_config['offset'])
        self.pid.setpoint = pid_config['setpoint']
        
        wlm_config = self.config['wlm']
        self.wlm_channel = wlm_config['channel']
        self.wlm_units = wlm_config['units']
        
        LabradServer.__init__(self)
    
    # @defer.inlineCallbacks
    def initServer(self):
        pass
        # yield self.client.spectrum_analyzer.select_device(self.config['spectrum_analyzer_name'])
        # self.msquared = yield self.client.msquared.select_device(self.config['msquared_name'])  # TODO
        
    def stopServer(self):
        pass
    
    @setting(101)
    def start_task(self, c):
        """
        sample_interval, default to be 2.5 s
        """
        self.feedbackTask = task.LoopingCall(self.feedback)
        self.task_state = True
        sampling_interval = 2.5
        self.feedbackTask.start(sampling_interval)
        
    @setting(102)
    def stop_task(self, c):
        self.feedbackTask.stop()
        self.task_state = False
    
    @setting(103)
    def get_task_state(self, c):
        return self.task_state
    
    @defer.inlineCallbacks
    def feedback(self):
        if not self.is_locked:
            return
        # shutter_open = yield self.client.sequencer.channel_manual_output(self.config['shutter_name'])
        # if not shutter_open:
        #     return

#         trace = yield self.spectrum_analyzer.trace()
#         trace = np.array(trace)

#         position = np.where(trace == np.max(trace))[0][0]
#         setpoint = self.pid.setpoint*1e6
#         frequency = setpoint + (  float(position-len(trace)/2) * ( self.lock_span / len(trace) )  )

# #        has_good_snr = (np.max(trace) - np.min(trace)) > self.peak_threshold
#         has_good_snr = (np.max(trace) - np.mean(trace)) > self.peak_threshold
#         if not has_good_snr:
#             self.lock_status = False
#             print('Feedback disabled due to bad signal')
#             return
        
        # shutter_open = yield self.client.sequencer.channel_manual_output(self.config['shutter_name'])
        # if not shutter_open:
        #     return
        
        if self.wlm_units in self.frquency_units:
            wlm_value = yield self.hf_wavemeter.get_frequency(self.wlm_channel)
        elif self.wlm_units in self.wavelength_units:
            wlm_value = yield self.hf_wavemeter.get_wavelength(self.wlm_channel)
        
        if wlm_value:
            pass
        else:
            self._send_update({'wlm_lock_status': 'Something wrong with WLM.' })
            return
        
        # self.lock_status = True
        feedback = self.pid.tick(wlm_value)

        value = round(feedback, 4)
        yield self.set_msquared_resonator_tune(value)

        message = 'Error: {:.6f} {} | Output: {:.4f} %'.format(self.pid.error, self.wlm_units, feedback)
        self._send_update({'wlm_lock_status': message })

        self.log()

    def log(self):
        if self.log_path == None:
            return
        
        log_path_folder = os.path.join(self.log_path, datetime.now().strftime('%Y'), datetime.now().strftime('%m%d'))
        if not os.path.isdir(log_path_folder):
            os.makedirs(log_path_folder) 
            
        log_path_daily = os.path.join(log_path_folder, datetime.now().strftime('%H')) # log every hour
        with open(log_path_daily + '.csv', 'a') as f:
            # f.write('%s,%s\n' % (time(), self.pid.error))
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write('%s, %s\n' % (now, self.pid.error))

    @property
    def hf_wavemeter(self):
        return self.client.hf_wavemeter

    @property
    def msquared(self):
        return self.client.msquared

        
        return self.config
        # self._send_update(json.dumps({'config' : self.config}))
    
    
    @setting(1, 'lock')
    def lock(self, c, setpoint):
        """
        Locks to <setpoint>
        """
        
        # set pid setpoint to setpoint
        self.pid.setpoint = setpoint

        # spectrum analyzer might glitch
        # => wait for one second before applying lock
        reactor.callLater(1, self.enable_lock)

        # defer.returnValue(f_0) 
        # defer.returnValue(setpoint) # why return f_0?


    @setting(2, 'unlock')
    def unlock(self, c):
        """
        Removes lock
        """

        self.is_locked = False

        # reset pid buffers
        self.pid.reset()

        # stop logging
        # yield self.stop_logging(c)

        # # zoom out
        # yield self.spectrum_analyzer.frequency_range(*self.capture_range)

    @setting(3, 'get_lock_status', returns='b')
    def get_lock_status(self, c):
        """
        Returns current lock status
        """

        # return self.is_locked and self.lock_status
        return self.is_locked

    @setting(4)
    def set_msquared_resonator_tune(self, value):
        """
        Sets MSquared Resonator Tune voltage, accepts 0 < value < 100
        """
        request = json.dumps({self.config['msquared_name']: value})
        response_json = self.msquared.resonator_tune(request)
        return response_json

    @setting(5)
    def get_wlm_frequency(self, channel):
        """
        Get wavemeter frequency for channel
        """
        response = self.hf_wavemeter.get_frequency(channel)
        return response
        
    @setting(6)
    def get_wlm_wavelength(self, channel):
        """
        Get wavemeter wavelength for channel
        """
        response = self.hf_wavemeter.get_wavelength(channel)
        return response

    @setting(7, 'set_setpoint', setpoint='v[]')
    def set_setpoint(self, c, setpoint):
        """
        Sets PID setpoint to <setpoint>
        """

        self.pid.setpoint = setpoint

    @setting(8, 'get_setpoint', returns='v[]')
    def get_setpoint(self, c):
        """
        Returns PID setpoint
        """

        return self.pid.setpoint

    @setting(9, 'set_gain', gain='v[]')
    def set_gain(self, c, gain):
        """
        Sets PID overall gain to <gain>
        """

        self.pid.set_params(overall_gain=gain)

    @setting(10, 'get_gain', returns='v[]')
    def get_gain(self, c):
        """
        Returns PID overall gain
        """

        return self.pid.overall_gain

    @setting(11, 'set_prop_gain', gain='v[]')
    def set_prop_gain(self, c, gain):
        """
        Sets PID proportional gain to <gain>
        """

        self.pid.set_params(prop_gain=gain)

    @setting(12, 'get_prop_gain', returns='v[]')
    def get_prop_gain(self, c, gain):
        """
        Returns PID proportional gain
        """

        return self.pid.prop_gain

    @setting(13, 'set_int_gain', gain='v[]')
    def set_int_gain(self, c, gain):
        """
        Sets PID integrator gain to <gain>
        """

        self.pid.set_params(int_gain=gain)

    @setting(14, 'get_int_gain', returns='v[]')
    def get_int_gain(self, c):
        """
        Return PID integrator gain
        """

        return self.pid.int_gain

    @setting(15, 'set_diff_gain', gain='v[]')
    def set_diff_gain(self, c, gain):
        """
        Sets PID differentiator gain to <gain>
        """

        self.pid.set_params(diff_gain=gain)

    @setting(16, 'get_diff_gain', returns='v[]')
    def get_diff_gain(self, c):
        """
        Returns PID differentiator gain
        """

        return self.pid.diff_gain

    @setting(17, 'set_offset', offset='v[]')
    def set_offset(self, c, offset):
        """
        Sets PID offset to <offset>
        """
        # yield self.msquared.resonator_tune(offset) #TODO
        yield self.set_msquared_resonator_tune(offset)
        self.pid.offset = offset

    @setting(18, 'get_offset', returns='v[]')
    def get_offset(self, c):
        """
        Returns PID offset
        """

        return self.pid.offset

    @setting(19, 'set_clamp', rng='(vv)')
    def set_clamp(self, c, rng):
        """
        Sets PID clamp values to <rng>
        """

        self.pid.min_max = rng

    @setting(20, 'get_clamp', returns='(vv)')
    def get_clamp(self, c):
        """
        Returns PID clamp values
        """

        return self.pid.min_max

    @setting(21, 'get_error', returns='v[]')
    def get_error(self, c):
        """
        Returns PID error
        """

        return self.pid.error

    @setting(22, 'get_setpoint_units', returns='v[]')
    def get_setpoint_units(self, c):
        """
        Returns PID setpoint units
        """

        return self.pid.setpoint_units
    
    @setting(23)
    def get_units(self, c):
        """
        Returns WLM units
        """
        return self.wlm_units

    @setting(24)
    def set_units(self, c, units):
        """
        Sets WLM units
        """
        if units in self.wavelength_units:
            self.wlm_units = units
        elif units == self.frequency_units:
            self.wlm_units = units
        else:
            pass
        
    @setting(25)
    def get_channel(self, c):
        """
        Gets WLM channel
        """
        return self.wlm_channel
    
    @setting(26)
    def set_channel(self, c, channel):
        """
        Sets WLM channel
        """
        channel = sorted([1, channel,4])[1]
        self.wlm_channel = channel
    
    @setting(27)
    def load_current_settings(self, c):
        """
        Loads current settings and return as json
        """
        
        settings = self.current_settings
        settings_json = json.dumps(settings, indent=2)
        
        return settings_json

    @setting(28, 'save_current_settings')
    def save_current_settings(self, c):
        """
        Saves current settings to disk
        """

        settings = self.current_settings
        settings_json = json.dumps(settings, indent=2)

        with open('config.json', 'w') as f:
            f.write(settings_json)

        print('Saved current settings to config.json')

    # @setting(29, 'start_logging')
    # def start_logging(self, c):
    #     """
    #     Starts logging pid error to disk
    #     """

    #     log_filename = 'log-%s.csv' % datetime.now().strftime("%Y%m%d%H%M%S")
    #     root = os.path.dirname(os.path.abspath(__file__))
    #     path = os.path.join(os.sep, root, 'logs', log_filename)
    #     self.log_path = os.path.abspath(path)

    #     # touch
    #     open(self.log_path, 'a').close()

    @setting(30, 'stop_logging')
    def stop_logging(self, c):
        """
        Stops logging
        """

        self.log_path = None
    
    @setting(31)
    def enable_lock(self):
        self.is_locked = True

    @setting(32)
    def disable_lock(self):
        self.is_locked = False

    @property
    def current_settings(self):
        settings = {
             "wlm_name": self.wlm_name,
             "msquared_name": self.msquared_name,
             "log_path": self.log_path,
                'pid': {
                    'overall_gain': self.pid.overall_gain,
                    'prop_gain': self.pid.prop_gain,
                    'int_gain': self.pid.int_gain,
                    'diff_gain': self.pid.diff_gain,
                    'range': self.pid.min_max,
                    'offset': self.pid.offset,
                    'setpoint': self.pid.setpoint
                },
                'wlm': {
                    'channel':  self.wlm_channel,
                    'units': self.wlm_units
                }
            }

        return settings
    
    @staticmethod
    def load_config(path):
        if (not os.path.isfile(path)):
            # raise Exception('DS815Server: Could not find configuration (%s).', config_path)
            raise Exception('DS815Server: Could not find configuration (%s).')

        f = open(path, 'r')
        json_data = f.read()
        f.close()
        
        return json.loads(json_data)

    def _send_update(self, update):
        update_json = json.dumps(update, default=lambda x: None)
        self.update(update_json)

if __name__ == '__main__':
    from labrad import util

    server = MSquaredWLMLockServer()
    util.runServer(server)