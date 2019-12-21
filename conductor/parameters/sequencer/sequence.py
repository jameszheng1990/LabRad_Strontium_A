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
    call_in_thread = False
    
    ni_servername = 'ni'

    sequencer_servername = 'sequencer'
    sequencer_devices = ['AO', 'DIO', 'Z_CLK']  # Make sure Run AO first, then DIO
    sequencer_master_device = 'Z_CLK'
    
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
        
        # first check if we are running
        request = {self.sequencer_master_device: None}
        response = json.loads(self.sequencer_server.running(json.dumps(request)))
        running = response.get(self.sequencer_master_device)
        
        # First, to initialize the device by running default values, and set running to True.
        # This will be done after initialization of LabRad, and in principle won't be called again during experiments..
        if not running:
            request = {device_name: self.default_value for device_name in self.sequencer_devices}
            self.sequencer_server.sequence(json.dumps(request))  # Write value
            request = {device_name: True for device_name in self.sequencer_devices}
            self.sequencer_server.running(json.dumps(request))   # Run value
            print('DAQ running!')
        
        # If running, which should always be true after initialization.
        else:
            # First, check if this is the first shot of experiment.
            if self.server.is_first:
                # Simply check, then write and run.
                request = {device_name: None for device_name in self.sequencer_devices}
                what_is_running = json.loads(self.sequencer_server.sequence(json.dumps(request)))
                what_i_think_is_running = {
                    device_name: self.value
                    for device_name in self.sequencer_devices
                    }
                if (what_i_think_is_running != what_is_running):
                    request = {device_name: self.value for device_name in self.sequencer_devices}
                    self.sequencer_server.sequence(json.dumps(request))  # Write value
                
                request = {device_name: True for device_name in self.sequencer_devices}
                self.sequencer_server.running(json.dumps(request))   # Run value
                self.server.is_first = False
                
                self.log_experiment_sequence()  # LOG Sequences
            
            # If this is not first shot, check if this is the end of shots
            elif self.server.is_end:
                # Simply end experiments, and reset everything back to default values.
                self.server.is_first = True
                self.server.is_end = False
                self.server.is_triggered = False
                request = {self.sequencer_master_device: self.default_value} # Write default value to Z_CLK device
                self.sequencer_server.sequence(json.dumps(request))  
            
            # If not first or end, will check if what is running == what we want to run.
            else:
                request = {device_name: None for device_name in self.sequencer_devices}
                what_is_running = json.loads(self.sequencer_server.sequence(json.dumps(request)))
                what_i_think_is_running = {
                    device_name: self.value
                    for device_name in self.sequencer_devices
                    }
                if (what_i_think_is_running != what_is_running):
                    request = {device_name: self.value for device_name in self.sequencer_devices}
                    self.sequencer_server.sequence(json.dumps(request))  # Write value
    
                request = {device_name: True for device_name in self.sequencer_devices}
                self.sequencer_server.running(json.dumps(request))   # Run value
                self.log_experiment_sequence()  # LOG Sequences
            
            
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
        name = self.server._get_name()
        print(name)
        print(self.server.experiment_directory)
        log_path = os.path.join(self.server.experiment_directory, name.split('\\')[0], 'sequences\\', name.split('\\')[1]+'_sequence')
        log_dir, log_name = os.path.split(log_path)
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        with open(log_path, 'w') as outfile:
            request = {device_name: None for device_name in self.sequencer_devices}
            sequence = json.loads(self.sequencer_server.log_sequence(json.dumps(request)))
            json.dump(sequence, outfile)
        print('Log experiment')
        
Parameter = Sequence
