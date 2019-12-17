import json
import numpy as np

from device_server.device import DefaultDevice

from sequencer.devices.yesr_sequencer_board.device import YeSrSequencerBoard
from sequencer.devices.yesr_digital_board.helpers import time_to_ticks
from sequencer.devices.yesr_digital_board.helpers import get_output
from sequencer.devices.timing import config
import itertools
from functools import reduce

T_TRIGGER = 2e-3

clk_rate = config().set_clk()
clk_interval = 1/clk_rate         # Clk interval, which is basically half of sample interval
clk_key = config().get_key()

do_rate = config().set_do_rate()
do_interval = 1/do_rate      # DO sample interval, twice of the clock sample interval

def get_clk_function(sequence):
    seq_list = [v for s, v in sequence.items()]
    analog_list = [i for i in seq_list if 'type' in i[0]]
    type_list = [[type_to_bool(j['type'])  for j in i] for i in analog_list]
    type_list = list(map(list, zip(*type_list))) # Transpose
    clk_list = list(map(bool, [reduce(lambda x, y: x*y, i) for i in type_list])) # ONLY when all rows are 's' will return True 
            
    return clk_list # False means variable clock will not apply on the sequence.

def type_to_bool(data):
    if data == 's':
        return True
    else:
        return False

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
        
        self.ni.Write_CLK_Manual(False) # CLK always set to be fasle
    
    def default_sequence_segment(self, channel, dt):
        return {'dt': dt, 'out': channel.manual_output}

    def make_sequence_bytes(self, sequence):
        #c.key: channel 
        #everytime you output all 32 channels together
        
        def to_bool_inv(out, invert):
            if invert == True:
                return not bool(out)
            else:
                return bool(out)
        
        def variable_out(out, dt, clk_out):
            if clk_out == True: # Apply Variable Clock
                return [out]
            else:
                ticks = time_to_ticks(do_interval, dt)
                return [out]*ticks
        
        def type_to_bool(data):
            if data == 's':
                return True
            else:
                return False

        clk_function = get_clk_function(sequence)
        
        ni_sequence = []
        
        for c in self.channels:
            out_list = [to_bool_inv(s['out'], c.invert) for s in sequence[c.key]]
            dt_list = [s['dt'] for s in sequence[c.key]]
            var_out = list(map(variable_out, out_list, dt_list, clk_function))
            var_out = list(itertools.chain.from_iterable(var_out))
            ni_sequence.append(var_out)
        return ni_sequence  # in Boolean
    
    def make_clk_sequence(self, sequence):
        # c.key: channel 
        # If clk.out = 1, use high-precision sample clock (1010...), otherwise use (000...).
        # Every timing edges must be ended with "0". 
        # CLK rate should be twice the Sample Rate (for DIO, AO)
        
        def clk_ticks(o, dt):
            tick = int(round(dt/clk_interval))
            if tick < 2:
                print('dt too small, minimum resolution is 2*1/CLK_rate !')
            else:
                if o == False:  # Do not apply Var Clk
                    a = [True, False] *int(round(tick/2))
                    return a
                elif o == True:  # Apply Var Clk
                    a = [True]
                    b = [False]*int(tick-1)
                    a.extend(b)
                    return a
        
        def get_dt(sequence):
            seq_list = [v for s, v in sequence.items()]
            analog_list = [i for i in seq_list if 'type' in i[0]]
            dt_list = [j['dt'] for j in analog_list[0]]
            
            return dt_list
        
        clk_sequence = []
        
        clk_outlist = get_clk_function(sequence)
        clk_dtlist = get_dt(sequence)
        
        for c in self.channels:
            if c.key != clk_key:
                print("Wrong CLK channel, please check 'Z_CLK' board.")
            else:
                a = [clk_ticks(clk_outlist[i], clk_dtlist[i]) 
                    for i in range(len(clk_outlist))]
                
        clk_sequence = list(itertools.chain(*a))
        # Should end with one more [True, False] edge
        clk_sequence.extend([True,False])
        
        return clk_sequence  # in Boolean