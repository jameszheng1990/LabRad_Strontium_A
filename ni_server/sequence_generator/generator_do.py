from sequencer.devices.timing import config
from sequencer.devices.yesr_digital_board.helpers import time_to_ticks
from functools import *
import functools, operator
import numpy as np
import time

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
    clk_function = list(map(bool, [reduce(lambda x, y: x*y, i) for i in type_list]))
    return clk_function # In Boolean. False means variable clock will not apply on the sequence.

def flip_invert(out, invert):
    if invert == True:
        out ^= 1  # flip 1/0 to 0/1
    else:
        pass
    return out
    
def map_ticks(dt, clk_function):
    if clk_function == True:
        ticks = 1
    else:
        ticks = time_to_ticks(do_interval, dt)
    return ticks

def make_sequence_bytes_do(raw_sequence, channels):
    """ 
    We group 8 lines for each port as a channel, so output should be in 4 rows, [4 by x dimension 2D numpy Array].
    Each element represents how each line outputs.
    For example, 'all off' is 0000000 = 0, 'line1 on' is 01000000 = 2^1 = 2, etc.
    """
    num_port = 4
    num_channel_in_port = 8
    
    clk_function = get_clk_function(raw_sequence)
    dt_list = [s['dt'] for s in raw_sequence[list(raw_sequence)[0]]]
    ticks_list = [map_ticks(i, j) for i, j in zip(dt_list, clk_function)]
    total_ticks = sum(ticks_list)
    
    ni_sequence = np.zeros((num_port, total_ticks), dtype=np.uint8)
    
    for i in range(num_port):
        for j in range(num_channel_in_port):
            out_list = [flip_invert(s['out'], channels[j + i*num_channel_in_port]['invert']) for s in raw_sequence[channels[j + i*num_channel_in_port]['key']]]
            m = 0
            for k in range(len(out_list)):
                ni_sequence[i, m:m + ticks_list[k]] += out_list[k]*2**j
                m += ticks_list[k]
    
    return ni_sequence  # in Boolean


# # Old way
# def make_sequence_bytes_do(raw_sequence, channels):
#     def flip_invert(out, invert):
#         if invert == True:
#             out ^= 1  # flip 1/0 to 0/1
#         else:
#             pass
#         return out
        
#     def make_variable_out(out, dt, clk_out):
#         if clk_out == True: # Apply Variable Clock
#             return np.array([out], dtype=np.uint8)
#             # return [out]
#         else:
#             ticks = time_to_ticks(do_interval, dt)
#             return np.tile(np.array([out], dtype=np.uint8), ticks)
#             # return [out]*ticks
    
#     t1 = time.time()
    
#     clk_function = get_clk_function(raw_sequence)
#     ni_sequence = np.array([], dtype=np.uint8)
#     # ni_sequence = []
        
#     for c in channels:
#         out_list = [flip_invert(s['out'], c['invert']) for s in raw_sequence[c['key']]]
#         dt_list = [s['dt'] for s in raw_sequence[c['key']]]
#         for i, j, k in zip(out_list, dt_list, clk_function):
#             ni_sequence = np.append(ni_sequence, make_variable_out(i, j, k))
            
#         # var_out = [make_variable_out(i, j, k) for i, j, k in zip(out_list, dt_list, clk_function)]
#         # var_out = functools.reduce(operator.iconcat, var_out, []) # seems to be faster.. unsure
#         # ni_sequence.append(var_out)
    
#     ni_sequence = ni_sequence.reshape(32, int(len(ni_sequence)/32))
#     # ni_sequence = np.asarray(ni_sequence, dtype = np.uint32)
#     print(time.time() - t1)
    
#     return ni_sequence  # in Boolean














    
    
    
    
    
    
    
    
    