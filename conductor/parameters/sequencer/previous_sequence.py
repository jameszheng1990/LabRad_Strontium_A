import json
import time
import os
import sys
#sys.path.append(os.getenv('PROJECT_LABRAD_TOOLS_PATH'))

from conductor.parameter import ConductorParameter

class PreviousSequence(ConductorParameter):
    autostart = True
    priority = 13
    value_type = 'list'
    value = None

    sequencer_servername = 'sequencer'
    master_device = 'Z_CLK'
    
    def initialize(self, config):
        super(PreviousSequence, self).initialize(config)
        self.connect_to_labrad()
        self.sequencer_server = getattr(self.cxn, self.sequencer_servername)
    
    def update(self):
        request = {self.master_device: None}
        response = json.loads(self.sequencer_server.sequence(json.dumps(request)))
        self.value = response[self.master_device]

Parameter = PreviousSequence
