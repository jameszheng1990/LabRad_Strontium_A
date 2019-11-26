import json
import numpy as np

from device_server.device import DefaultDevice

from sequencer.devices.yesr_sequencer_board.device import YeSrSequencerBoard
from sequencer.devices.yesr_analog_board.ramps import RampMaker
from sequencer.devices.yesr_analog_board.helpers import time_to_ticks
from sequencer.devices.yesr_analog_board.timing import config

# max timestep for digital sequencer
T_TRIGGER = 100 # [s]
clk = config().set_clk()
rate = config().set_rate()
interval = 1/rate

class YeSrAnalogBoard(YeSrSequencerBoard):
    
    sequencer_type = 'analog'
    
    def initialize(self, config):
        YeSrSequencerBoard.initialize(self, config)
    
    def update_channel_modes(self):
        pass
#        cm_list = [c.mode for c in self.channels]
#        value = sum([2**j for j, m in enumerate(cm_list) if m == 'manual'])
#        value = 0b0000000000000000 | value
#        self.fp.SetWireInValue(self.channel_mode_wire, value)
#        self.fp.UpdateWireIns()
    
    def update_channel_manual_outputs(self): 
        cp_list = [c.loc for c in self.channels if c.mode == 'manual']
        co_list = [c.manual_output for c in self.channels if c.mode == 'manual']
        
        # Pass to NI proxy
        if cp_list != []:
            for value, port in zip(co_list, cp_list):
                self.ni.Write_AO_Manual(value, port)
        else:
            print("NO manual channels!")
            pass
    
    def default_sequence_segment(self, channel, dt):
        return {'dt': dt, 'type': 's', 'vf': channel.manual_output}

    def make_sequence_bytes(self, sequence):
        #c.key: channel 
        ni_sequence = []        
        
        for channel in self.channels:
            sequence[channel.key] = [s for s in sequence[channel.key] if s['dt'] < T_TRIGGER]
            channel_sequence = sequence[channel.key]
            channel.set_sequence(channel_sequence)   # Load the defined "ramps: s, lin, slin, exp etc..."
        
        for channel in self.channels:
            channel_seq = []
            for ramp in channel.programmable_sequence:
                if ramp['dv'] == 0:
                    single_seq = [ramp['vi']]*10000
                else:
                    single_seq = list(np.linspace(ramp['vi'], ramp['vf'], int(round(ramp['dt']/interval))))
                channel_seq.extend(single_seq)
            ni_sequence.append(channel_seq)
        
        return ni_sequence