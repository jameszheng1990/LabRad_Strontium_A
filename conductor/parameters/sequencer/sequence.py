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
    
    loop = None # doesn't matter at this moment
    previous_sequencer_parameter_values = None
    # re_write = False
    is_initiated = False
    call_in_thread = False
    
    ni_servername = 'ni'

    sequencer_servername = 'sequencer'
    sequencer_devices = ['AO', 'DIO', 'Z_CLK']  # Make sure Run Z_CLK last
    sequencer_devices_ao_off = ['DIO', 'Z_CLK']
    
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
        callInThread(self.update)
    
    def update(self):
        # Initialization will be called after server starts, and in principle won't be called again unless server restarts...
        if not self.is_initiated:
            request = {device_name: self.default_value for device_name in self.sequencer_devices}
            self.sequencer_server.sequence(json.dumps(request)) 
            request = {device_name: True for device_name in self.sequencer_devices}
            self.sequencer_server.running(json.dumps(request)) 
            self.is_initiated = True
            print('NI DAQ initiation done!')
        
        else:
            # Check if this is the first shot of current experiment  (popped up from queue), then write to DAQ and run
            if self.server.is_first:
                print('Writing NI DAQ tasks...')
                request = {device_name: self.value for device_name in self.sequencer_devices}
                self.sequencer_server.sequence(json.dumps(request))  # Write DAQ
                self.log_experiment_sequence() # LOG When sequence is written
                
                request = {device_name: True for device_name in self.sequencer_devices}
                self.sequencer_server.running(json.dumps(request))   # Run DAQ
                
                self.previous_sequencer_parameter_values = self._get_sequencer_parameter_values()
                self.server.is_first = False
            
            # If this is not first shot, then check if this is the end of experiments
            elif self.server.is_end:
                # Simply end experiments, and reset everything back to default values
                request = {self.sequencer_master_device: self.default_value} # Write default value to Z_CLK device
                self.sequencer_server.sequence(json.dumps(request))  
                
                # Add 06/10/20, clear parameter value queues after experiments end
                reset_parameters = self.server.saved_parameter_values
                for key, value in reset_parameters.items():
                    reset_parameters[key] = {}
                self.server._clear_value_queues(reset_parameters)
                
                # Terminate reloaded parameters after experiment ends
                terminated_parameters = self.server.saved_reload_parameters
                for key, value in terminated_parameters.items():
                    self.server._terminate_parameter(key)
                
                # And clear experiments and clear experiment queues
                self.server._clear_experiment()
                self.server._clear_experiment_queue()
                    
                print('Experiments end!')
                     
                self.server.is_end = False
                self.server.is_stop = False
                self.server.is_running = False # pulls the trigger off, and wait for next trigger to start experiments...
                self.server._send_update({'is_running': False})
                
            # If not first or end, this would be from shot to shot (scan), or looping
            else:
                experiment_loop = self.server.experiment.get('loop')
                current_sequencer_parameter_values = self._get_sequencer_parameter_values()
                
                # only re-write DAQ when loop is False and sequener parameter values are not the same.
                if (experiment_loop is False) and (current_sequencer_parameter_values 
                                                   != self.previous_sequencer_parameter_values):
                    print('Writing NI DAQ tasks...')
                    request = {device_name: self.value for device_name in self.sequencer_devices}
                    self.sequencer_server.sequence(json.dumps(request))  # Write DAQ

                    self.log_experiment_sequence() # LOG When sequence is written
                
                request = {device_name: True for device_name in self.sequencer_devices}
                self.sequencer_server.running(json.dumps(request))   # Run value
                self.previous_sequencer_parameter_values = current_sequencer_parameter_values
        
        callInThread(self._advance_on_trigger)

    def _advance_on_trigger(self):
        self._wait_for_trigger() 
        # self._mark_timestamp()
        try:
            conductor_server = getattr(self.cxn, 'conductor')
            conductor_server.advance(True)
        except Exception as e:
            print(e)

    def _wait_for_trigger(self):
        while True:
            try:
                conductor_server = getattr(self.cxn, 'conductor')
                is_running = conductor_server.check_running()
                if is_running:
                    return
                time.sleep(0.01)
            except:
                return

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
            print('Log experiment ({})'.format(name))
            log_path = os.path.join(self.server.experiment_directory, name.split('\\')[0], name.split('\\')[1]+'_sequence')
            log_dir, log_name = os.path.split(log_path)
            if not os.path.isdir(log_dir):
                os.makedirs(log_dir)
                
            request = {self.sequencer_master_device: None}
            sequence = json.loads(self.sequencer_server.log_sequence(json.dumps(request)))
            
            with open(log_path, 'w') as outfile:
                json.dump(sequence, outfile)
        except:
            pass
        
Parameter = Sequence
