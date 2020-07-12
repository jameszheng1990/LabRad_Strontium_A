from sequencer.devices.timing import config
from sequencer.devices.yesr_digital_board.helpers import time_to_ticks
from functools import *
import functools, operator, time
import numpy as np

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

# Old way
def make_sequence_bytes_clk(raw_sequence):
    def get_ticks_list(sequence):
        seq_list = [v for s, v in sequence.items()]
        analog_list = [i for i in seq_list if 'type' in i[0]]
        dt_list = [j['dt'] for j in analog_list[0]]
        ticks_list = [time_to_ticks(clk_interval, i) for i in dt_list]
        return ticks_list
        
    clk_sequence = []
        
    clk_function = get_clk_function(raw_sequence)
    ticks_list = get_ticks_list(raw_sequence)
    total_ticks = sum(ticks_list)
    conversion_factor = int(do_interval/clk_interval)
        
    clk_sequence = np.zeros(total_ticks, dtype = np.uint8)
    
    m = 0
    for i in range(len(clk_function)):
        if clk_function[i] == True:
            # will apply Variable Clock, output in [1000...0000]
            a = np.array([1], dtype=np.uint8)
            b = np.zeros(ticks_list[i]-1, dtype =np.uint8)
            sub_sequence = np.append(a, b)
        else:
            # will not apply Variable Clock, output in [10..(k)..010...0...10...0], each is [1] + (k-1)*[0],where k = conversion_factor.
            a = np.array([1], dtype=np.uint8)
            b = np.zeros(int(conversion_factor-1), dtype=np.uint8)
            a = np.append(a, b)
            sub_sequence = np.tile(a, int(ticks_list[i]/conversion_factor))
        clk_sequence[m: m+ ticks_list[i]] = sub_sequence
        m += ticks_list[i]
    
    # Should end with one more [True, False] pulse edge
    clk_sequence = np.append(clk_sequence, np.array([1, 0], dtype=np.uint8))
    
    return clk_sequence

# def make_sequence_bytes_clk(raw_sequence):
#     def get_ticks_list(sequence):
#             seq_list = [v for s, v in sequence.items()]
#             analog_list = [i for i in seq_list if 'type' in i[0]]
#             ticks_list = [ time_to_ticks(clk_interval, j['dt']) for j in analog_list[0]]
#             return ticks_list
    
#     # t1 = time.time()    
    
#     clk_sequence = []
#     clk_function = get_clk_function(raw_sequence)
#     ticks_list = get_ticks_list(raw_sequence)
#     total_ticks = sum(ticks_list) + 2   # end with [1,0] pulse, so total_ticks + 2

#     clk_sequence = np.zeros(total_ticks, dtype = np.uint8) 
    
#     k = 0

#     # Too slow below...
#     for i in range(len(clk_function)):
#         if clk_function[i] == True: # apply Var Clk, 100..00
#             clk_sequence[k] = 1
#             clk_sequence[k+1 : k+ticks_list[i]] = 0
#         else: # do not apply Var Clk, 1010...10
#             for j in range(int(ticks_list[i]/2)):
#                 clk_sequence[k+j: k+j+2] = [1, 0]
#         k += ticks_list[i]
    
#     # Should end with [1, 0] pulse
#     clk_sequence[-2:] = [1,0]
    
#     # print( 'make clk ', time.time() - t1)
    
#     return clk_sequence
    
    
    
    
    
    
    
    
    