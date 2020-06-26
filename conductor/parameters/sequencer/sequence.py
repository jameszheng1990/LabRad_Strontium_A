import json
import os
import time

import labrad
from twisted.internet.reactor import callInThread
from twisted.internet.reactor import callFromThread

from conductor.parameter import ConductorParameter
from ni_server.proxy import NIProxy

class Sequence(ConductorParameter):
    autostart = True
    priority = 10
    value_type = 'seq_list'  # All sequence should be in list, and if len()>1, will be combined into a whole sequence
    value = ['all_off']
    default_value = ['all_off']

    loop = True  # Should always be true...
    is_initiated = False
    call_in_thread = False
    
    ni_servername = 'ni'

    sequencer_servername = 'sequencer'
    sequencer_devices = ['AO', 'DIO', 'Z_CLK']  # Make sure Run Z_CLK last
    sequencer_devices_ao_off = ['DIO', 'Z_CLK']
    
    sequencer_master_device = 'Z_CLK'
    re_write = False
    
    def initialize(self, config):
        super(Sequence, self).initialize(config)
        try:
            password = os.getenv('LABRADPASSWORD')  #PW should be None
            host = os.getenv('LABRADHOST')
            self.sra_cxn = labrad.connect(host=host, password=password)
            # sra_timestamp = self.sra_cxn.time.time()  # time server?
        except Exception as e:
            print(e)
            print('sra time server not found')
            self.sra_cxn = None

        self.connect_to_labrad()
        self.ni_server = getattr(self.cxn, self.ni_servername)
        self.sequencer_server = getattr(self.cxn, self.sequencer_servername)
        
        ni_proxy = NIProxy(self.ni_server)
        self.ni = ni_proxy.niCFrontPanel()

        request = {device_name: {} for device_name in self.sequencer_devices}
#        self.sequencer_server.reload_devices(json.dumps(request))
        self.sequencer_server.initialize_devices(json.dumps(request))
        self.previous_sequencer_parameter_values = self._get_sequencer_parameter_values()
        callInThread(self.update)
    
    def update(self):
        """ value is list of strings """
        
        # First, to initialize the device by running default values, and set running to True.
        # This will be done after initialization of LabRad, and in principle won't be called again during experiments..
        if not self.is_initiated:
            request = {device_name: self.default_value for device_name in self.sequencer_devices}
            self.sequencer_server.sequence(json.dumps(request))  # Write DAQ
            request = {device_name: True for device_name in self.sequencer_devices}
            self.sequencer_server.running(json.dumps(request))   # Run DAQ
            self.is_initiated = True
            print('DAQ initiated!')
        
        # If running, which should always be true after initialization.
        else:
            # First, check if this is the first shot of experiment, or transition from one exp to another.
            if self.server.is_first:
                self.server.is_running = True
                
                request = {device_name: None for device_name in self.sequencer_devices}
                what_is_running = json.loads(self.sequencer_server.sequence(json.dumps(request)))
                what_i_think_is_running = {
                    device_name: self.value
                    for device_name in self.sequencer_devices
                    }
                
                if (what_i_think_is_running != what_is_running):
                    print('Writing DAQ tasks.')
                    request = {device_name: self.value for device_name in self.sequencer_devices}
                    self.sequencer_server.sequence(json.dumps(request))  # Write DAQ
                
                self.log_experiment_sequence() # LOG When sequence is changed.
                
                request = {device_name: True for device_name in self.sequencer_devices}
                self.sequencer_server.running(json.dumps(request))   # Run DAQ
                
                self.server.is_first = False
            
            # If this is not first shot, check if this is the end of shots
            elif self.server.is_end:
                # Simply end experiments, and reset everything back to default values.
                
                request = {self.sequencer_master_device: self.default_value} # Write default value to Z_CLK device
                self.sequencer_server.sequence(json.dumps(request))  
                
                # Add 06/10/20, clear parameter value queues after experiment ends.
                reset_parameters = self.server.saved_parameter_values
                for key, value in reset_parameters.items():
                    reset_parameters[key] = {}
                self.server._clear_value_queues(reset_parameters)
                
                # Add 06/21/20, terminate reloaded parameters after experiment ends.
                terminated_parameters = self.server.saved_reload_parameters
                for key, value in terminated_parameters.items():
                    self.server._terminate_parameter(key)
                
                self.server._stop_experiment()
                self.server._clear_experiment_queue()
                    
                print('Experiment ends!')
                     
                self.server.is_first = True
                self.server.is_end = False
                self.server.is_triggered = False
                self.server.is_running = False # set to not running, wait for next trigger.
                self.re_write = False
                
            # If not first or end, this would be from shot to shot (like scan), or looping.
            else:
                self.server.is_running = True
                experiment_loop = self.server.experiment.get('loop')
                try:
                    parameter_values = self.server.experiment.get('parameter_values')
                    do_parameters = parameter_values.get('sequencer.DO_parameters')
                    ao_parameters = parameter_values.get('sequencer.AO_parameters')
                    # need to fix why running two experiments (lifetime first, modulation second) will lead to re-write for modulation.... seems to work again..
                    
                    if do_parameters:
                        if any(type(value).__name__ == 'list' for key, value in do_parameters.items()):
                            self.re_write = True
                    elif ao_parameters:
                        if any(type(value).__name__ == 'list' for key, value in ao_parameters.items()):
                            self.re_write = True
                    else:
                        self.re_write = False
                except Exception as e:
                    print(e)
                    self.re_write = False
    
                # only re-write DAQ when loop is False and if any ao/do_parameter value type is list.
                if (experiment_loop is False) and self.re_write:
                    print('Writing DAQ tasks.')
                    request = {device_name: self.value for device_name in self.sequencer_devices}
                    self.sequencer_server.sequence(json.dumps(request))  # Write DAQ
                        
                    self.log_experiment_sequence() # LOG When sequence is changed.
                else:
                    pass
                
                request = {device_name: True for device_name in self.sequencer_devices}
                self.sequencer_server.running(json.dumps(request))   # Run value
                    
        callInThread(self._advance_on_trigger)

    def _advance_on_trigger(self):
        self.conductor_server = getattr(self.cxn, 'conductor')
        self._wait_for_trigger() 
        # self._mark_timestamp()
        self.conductor_server.advance(True)

    def _wait_for_trigger(self):
        while True:
            is_triggered = self.conductor_server.check_trigger()
            if is_triggered:
                return
                time.sleep(0.01)

    def _mark_timestamp(self):
        request = {'timestamp': time.time()}
        if self.sra_cxn is not None:
            sra_timestamp = self.sra_cxn.time.time()
            request.update({'sra_timestamp': sra_timestamp})
        self.conductor_server.set_parameter_values(json.dumps(request))

    # current_sequencer_parameter_values = self._get_sequencer_parameter_values()
                    
    def _get_sequencer_parameter_values(self):
        active_parameters = self.server._get_active_parameters()
        active_sequencer_parameters = [pn for pn in active_parameters if pn.find('sequencer.') == 0]
        request = {pn: None for pn in active_sequencer_parameters}
        sequencer_parameter_values = self.server._get_parameter_values(request)
        return sequencer_parameter_values
    
    def log_experiment_sequence(self):
        name = self.server.experiment_name
        try:
            log_path = os.path.join(self.server.experiment_directory, name.split('\\')[0], 'sequences\\', name.split('\\')[1]+'_sequence')
            log_dir, log_name = os.path.split(log_path)
            if not os.path.isdir(log_dir):
                os.makedirs(log_dir)
                
            request = {self.sequencer_master_device: None}
            sequence = json.loads(self.sequencer_server.log_sequence(json.dumps(request)))
            
            with open(log_path, 'w') as outfile:
                json.dump(sequence, outfile)
            print('Log experiment!')
        except:
            pass
        
Parameter = Sequence
