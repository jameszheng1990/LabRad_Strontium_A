from sequencer.devices.timing import config
from sequencer.devices.yesr_digital_board.helpers import time_to_ticks
from functools import *
import functools, operator

clk_rate = config().set_clk()
clk_interval = 1/clk_rate         # Clk interval, which is basically half of sample interval
clk_key = config().get_key()

do_rate = config().set_do_rate()
do_interval = 1/do_rate      # DO sample interval, twice of the desired sample interval

def type_to_bool(data):
    if data == 's':
        return True
    else:
        return False
    
def get_clk_function(sequence):
    seq_list = [v for s, v in sequence.items()]
    analog_list = [i for i in seq_list if 'type' in i[0]]
    type_list = [[type_to_bool(j['type'])  for j in i] for i in analog_list]
    type_list = list(map(list, zip(*type_list))) # Transpose
    clk_list = list(map(bool, [reduce(lambda x, y: x*y, i) for i in type_list]))
    
    return clk_list # False means variable clock will not apply on the sequence.

def make_sequence_bytes_do(raw_sequence, channels):
        #c.key: channel 
        #everytime you output all 32 channels together
        
        def to_bool_inv(out, invert):
            if invert == True:
                return not bool(out)
            else:
                return bool(out)
        
        def make_variable_out(out, dt, clk_out):
            if clk_out == True: # Apply Variable Clock
                return [out]
            else:
                ticks = time_to_ticks(do_interval, dt)
                return [out]*ticks

        clk_function = get_clk_function(raw_sequence)
        
        ni_sequence = []
        
        for c in channels:
            out_list = [to_bool_inv(s['out'], c['invert']) for s in raw_sequence[c['key']]]
            dt_list = [s['dt'] for s in raw_sequence[c['key']]]
            
            var_out = [make_variable_out(i, j, k) for i, j, k in zip(out_list, dt_list, clk_function)]
            var_out = functools.reduce(operator.iconcat, var_out, []) # seems to be faster.. unsure
            ni_sequence.append(var_out)
            
        return ni_sequence  # in Boolean
    
    
    
    
    
    
    
    
    
    
    
    