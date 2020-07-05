import json
import numpy as np

from device_server.device import DefaultDevice

from sequencer.devices.yesr_sequencer_board.device import YeSrSequencerBoard
from sequencer.devices.yesr_analog_board.ramps import RampMaker
from sequencer.devices.yesr_analog_board.helpers import time_to_ticks
from sequencer.devices.timing import config
import itertools
from functools import reduce

# max timestep for digital sequencer
T_TRIGGER = 100 # [s]

clk_rate = config().set_clk()
clk_interval = 1/clk_rate
clk_key = config().get_key()

ao_rate = config().set_ao_rate()
ao_interval = 1/ao_rate

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
            pass
    
    def default_sequence_segment(self, channel, dt):
        return {'dt': dt, 'type': 's', 'vf': channel.manual_output}
    
    def update_sequence_and_channels_list(self, sequence):
        """ This will update sequence and channels list, make programmable sequence into the return dictionary """
        def type_to_bool(data):
            if data == 's': # only True for 's' ramp
                return True
            else:
                return False

        def get_clk_function(sequence):
            seq_list = [v for s, v in sequence.items()]
            analog_list = [i for i in seq_list if 'type' in i[0]]
            type_list = [[ type_to_bool(j['type'])  for j in i ] for i in analog_list]
            type_list = list(map(list, zip(*type_list))) # Transpose
            clk_list = list(map(bool, [reduce(lambda x, y: x*y, i) for i in type_list])) # ONLY when all rows are 's' will return True 
            
            return clk_list # False means variable clock will not apply on the sequence.
        
        clk_function = get_clk_function(sequence)
        
        # Update CLK sequence to Analog Keys
        for channel in self.channels:
            i=0
            for s in sequence[channel.key]:
                s['clk'] = clk_function[i]
                i += 1
        
        for channel in self.channels:
            sequence[channel.key] = [s for s in sequence[channel.key] if s['dt'] < T_TRIGGER]
            channel_sequence = sequence[channel.key]
            channel.set_sequence(channel_sequence)   # Load the defined "ramps: s, lin, slin, exp etc..."
            
        sequence_and_channels_list = []
        for c in self.channels:
            channel = {'key': c.key, 'programmable_sequence': c.programmable_sequence}
            sequence_and_channels_list.append(channel)
        return sequence_and_channels_list
    
    def make_sequence_bytes(self, sequence):
        """ No longer needed, use ni/sequence_generator/ to generate NI sequence. """
        #c.key: channel 
        
        def type_to_bool(data):
            if data == 's': # only True for 's' ramp
                return True
            else:
                return False

        def get_clk_function(sequence):
            seq_list = [v for s, v in sequence.items()]
            analog_list = [i for i in seq_list if 'type' in i[0]]
            type_list = [[ type_to_bool(j['type'])  for j in i ] for i in analog_list]
            type_list = list(map(list, zip(*type_list))) # Transpose
            clk_list = list(map(bool, [reduce(lambda x, y: x*y, i) for i in type_list])) # ONLY when all rows are 's' will return True 
            
            return clk_list # False means variable clock will not apply on the sequence.
        
        clk_function = get_clk_function(sequence)
        
        ni_sequence = []   
        
        # Update CLK sequence to Analog Keys
        for channel in self.channels:
            i=0
            for s in sequence[channel.key]:
                s['clk'] = clk_function[i]
                i += 1
        
        for channel in self.channels:
            sequence[channel.key] = [s for s in sequence[channel.key] if s['dt'] < T_TRIGGER]
            channel_sequence = sequence[channel.key]
            channel.set_sequence(channel_sequence)   # Load the defined "ramps: s, lin, slin, exp etc..."
        
        for channel in self.channels:
            channel_seq = []
            #TODO: if clk = True, out [x]*1), else, out [x]*dt/interval...
            for ramp in channel.programmable_sequence:
                if ramp['clk'] == True:
                    #WILL apply variable clock, every sub-sequence should be 's' in this case
                    sub_seq = [ramp['vf']]  # change from vi to vf, same below.. this will jump to vf for 's' ramp if vf != vi
                    
                else:
                    #WILL NOT apply variable clock
                    if 'dv_s' in ramp: # this should only exists in 's' ramp.
                        sub_seq = [ramp['vf']]*int(round(ramp['dt']/ao_interval))
                    else:
                        sub_seq = list(np.linspace(ramp['vi'], ramp['vf'], int(round(ramp['dt']/ao_interval))))                
                channel_seq.extend(sub_seq)
            ni_sequence.append(channel_seq)
        return ni_sequence