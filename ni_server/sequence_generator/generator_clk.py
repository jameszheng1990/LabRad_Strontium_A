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
    clk_list = list(map(bool, [reduce(lambda x, y: x*y, i) for i in type_list]))
    
    return clk_list # False means variable clock will not apply on the sequence.

def make_sequence_bytes_clk(raw_sequence):
    def clk_ticks(out, dt):
        ticks = int(round(dt/do_interval))
        factor = int(do_interval/clk_interval) # conversion factor from 10 MHz CLK to DO/AO sample rate (0.5 MHz)
            
        if ticks < 1:
            print('dt too small, minimum resolution is 2*1/CLK_rate !')
        else:
            if out == False:  # Do not apply Var Clk
                # a = [True]
                # b = [False]*int(factor-1)
                # a.extend(b)
                # c = a*int(ticks)
                a = np.array([1], dtype=np.uint8)
                b = np.repeat(np.array([0], dtype=np.uint8), int(factor-1))
                a = np.append(a, b)
                c = np.tile(a, int(ticks))
                return c
            elif out == True:  # Apply Var Clk
                # a = [True]
                # b = [False]*int(ticks*factor - 1)
                a = np.array([1], dtype=np.uint8)
                b = np.repeat(np.array([0], dtype=np.uint8), int(ticks*factor - 1))
                a = np.append(a, b)
                return a

    def get_dt(sequence):
            seq_list = [v for s, v in sequence.items()]
            analog_list = [i for i in seq_list if 'type' in i[0]]
            dt_list = [j['dt'] for j in analog_list[0]]
            return dt_list
        
    clk_sequence = []
        
    clk_outlist = get_clk_function(raw_sequence)
    clk_dtlist = get_dt(raw_sequence)
        
    # t1=time.time()
    
    # clk_sequence = [clk_ticks(i, j) for i, j in zip(clk_outlist, clk_dtlist)]
    # clk_sequence = functools.reduce(operator.iconcat, clk_sequence, []) # seems to be faster.. unsure
    clk_sequence = np.array([], dtype = np.uint8)
    for i, j in zip(clk_outlist, clk_dtlist):
        clk_sequence = np.append(clk_sequence, clk_ticks(i, j))
    
    # Should end with one more [True, False] pulse edge
    # clk_sequence.extend([True, False])
    clk_sequence = np.append(clk_sequence, np.array([1, 0], dtype=np.uint8))
    
    # print( 'make clk ', time.time() - t1)
    
    return clk_sequence
    
    
    
    
    
    
    
    
    