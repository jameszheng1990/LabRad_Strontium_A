from sequencer.devices.timing import config
from sequencer.devices.yesr_digital_board.helpers import time_to_ticks
from functools import *
import functools, operator
import numpy as np

clk_rate = config().set_clk()
clk_interval = 1/clk_rate         # Clk interval, which is basically half of sample interval
clk_key = config().get_key()

ao_rate = config().set_ao_rate()
ao_interval = 1/ao_rate

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

def make_sequence_bytes_ao(raw_sequence_channels_list):
    channels = raw_sequence_channels_list
    ni_sequence = []
    
    for c in channels:
        channel_seq = []
        #TODO: if clk = True, out [x]*1), else, out [x]*dt/interval...
        for ramp in c['programmable_sequence']:
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
    
    
    
    
    
    
    
    