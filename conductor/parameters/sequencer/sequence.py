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
    value_type = 'list'
    value = ['all_off'] * 1

    loop = False
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
        if not running:
            request = {device_name: self.value for device_name in self.sequencer_devices}
            self.sequencer_server.sequence(json.dumps(request))  # Write value
            request = {device_name: True for device_name in self.sequencer_devices}
            self.sequencer_server.running(json.dumps(request))   # Run value
            if not self.loop:
                request = {device_name: False for device_name in self.sequencer_devices}
                self.sequencer_server.running(json.dumps(request))   # Stop running if not loop

        if self.loop:
            # then check what sequence is running
            request = {device_name: None for device_name in self.sequencer_devices}
            what_is_running = json.loads(self.sequencer_server.sequence(json.dumps(request)))
            what_i_think_is_running = {
                device_name: self.value 
                    for device_name in self.sequencer_devices
                } 
            current_sequencer_parameter_values = self._get_sequencer_parameter_values()
            
            if (what_i_think_is_running != what_is_running):
                request = what_i_think_is_running
                self.sequencer_server.sequence(json.dumps(request))
                self.server.experiment['repeat_shot'] = True
            if (self.next_value == self.value):
                request = {device_name: True for device_name in self.sequencer_devices}
                self.sequencer_server.running(json.dumps(request)) # If value not changed, simply start task after writing buffer.
            else:
                request = {device_name: self.next_value for device_name in self.sequencer_devices}
                self.sequencer_server.sequence(json.dumps(request))
            
        if (not self.loop) and running:
            raise Exception('something is wrong with sequencer.sequence')
        
        callInThread(self._advance_on_trigger)

    def _get_sequencer_parameter_values(self):
        active_parameters = self.server._get_active_parameters()
        active_sequencer_parameters = [pn for pn in active_parameters if pn.find('sequencer.') == 0]
        request = {pn: None for pn in active_sequencer_parameters}
        sequencer_parameter_values = self.server._get_parameter_values(request)
        return sequencer_parameter_values

    def _wait_for_trigger(self):
        while True:
            is_triggered = self.ni.Is_Triggered()  # TODO: NEED to add a virtual trigger
            if is_triggered:
                return
            
            is_triggered_once = self.ni.Is_Triggered_Once()
            if is_triggered_once:
                self.ni.Trigger_Once_Off()
                return
            
            time.sleep(0.01)

    def _advance_on_trigger(self):
        self._wait_for_trigger() 
        # self._mark_timestamp()
        conductor_server = getattr(self.cxn, 'conductor')
        conductor_server.advance(True)

    def _mark_timestamp(self):
        request = {'timestamp': time.time()}
        if self.sra_cxn is not None:
            sra_timestamp = self.sra_cxn.time.time()
            request.update({'sra_timestamp': sra_timestamp})
        conductor_server = self.cxn.conductor
        conductor_server.set_parameter_values(json.dumps(request))

Parameter = Sequence
