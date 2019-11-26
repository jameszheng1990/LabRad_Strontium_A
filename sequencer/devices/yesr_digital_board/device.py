import json
import os
import sys
sys.path.append(os.getenv('PROJECT_LABRAD_TOOLS_PATH'))

from device_server.device import DefaultDevice

from sequencer.devices.yesr_sequencer_board.device import YeSrSequencerBoard
from sequencer.devices.yesr_digital_board.helpers import time_to_ticks
from sequencer.devices.yesr_digital_board.helpers import get_output
from sequencer.devices.yesr_digital_board.timing import config

T_TRIGGER = 2e-3

clk = config().set_clk()
rate = config().set_rate()
interval = 1/rate

class YeSrDigitalBoard(YeSrSequencerBoard):
    sequencer_type = 'digital'
    
    def initialize(self, config):
        YeSrSequencerBoard.initialize(self, config)
    
    def update_channel_modes(self):  # Not necessary ?
        pass
#        cm_list = [c.mode for c in self.channels]
#        values = [sum([2**j for j, m in enumerate(cm_list[i:i+1]) 
#                if m == 'manual']) for i in range(0, 32, 1)]
#        for value, wire in zip(values, self.channel_mode_wires):
#            self.fp.SetWireInValue(wire, value)
#        self.fp.UpdateWireIns()
#        self.update_channel_manual_outputs()
    
    def update_channel_manual_outputs(self): 
        cm_list = [c.mode for c in self.channels]
        cs_list = [c.manual_output for c in self.channels]
        ci_list = [c.invert for c in self.channels]
        values = [sum([2**j for j, (m, s, i) in enumerate(zip(
                cm_list[i:i+1], cs_list[i:i+1], ci_list[i:i+1]))
                if (m=='manual' and s!=i) or (m=='auto' and i==True)]) 
                for i in range(0, 32, 1)]
        values_bool = list(map(bool, values))
#        print(values_bool) # For test, result shown in back-end CMD (visa server)
        self.ni.Write_DO_Manual(values_bool)
    
    def default_sequence_segment(self, channel, dt):
        return {'dt': dt, 'out': channel.manual_output}

    def make_sequence_bytes(self, sequence):
        #c.key: channel 
        #everytime you output all 32 channels together
        
        programmable_sequence = []
        
        for c in self.channels:
            total_ticks = 0
            channel_seq = []
            for s in sequence[c.key]:
                ticks = time_to_ticks(interval, s['dt'])
                if c.invert == True:
                    s_to_seq = [not bool(s['out'])]*ticks
                else:
                    s_to_seq = [bool(s['out'])]*ticks
                channel_seq.extend(s_to_seq)  # Maybe need Bool
                total_ticks += ticks
                                
            programmable_sequence.append(channel_seq) 

#        print(programmable_sequence)
#        print(total_ticks)
        return programmable_sequence  # in Boolean
    