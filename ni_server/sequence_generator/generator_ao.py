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

def get_clk_function(channels):
    clk_function = [ramp['clk'] for ramp in channels[0]['programmable_sequence']] 
    return clk_function # False means variable clock will not apply on the sequence.

def get_dt_list(channels):
    dt_list = [ramp['dt'] for ramp in channels[0]['programmable_sequence']] 
    return dt_list

def map_ticks(dt, clk_function):
    if clk_function == True:
        ticks = 1
    else:
        ticks = time_to_ticks(ao_interval, dt)
    return ticks
    
def make_sequence_bytes_ao(raw_sequence_channels_list):

    
    channels = raw_sequence_channels_list
    num_port = len(channels)

    clk_function = get_clk_function(raw_sequence_channels_list)
    dt_list = get_dt_list(raw_sequence_channels_list)
    ticks_list = [map_ticks(i, j) for i, j in zip(dt_list, clk_function)]
    total_ticks = sum(ticks_list)
    ni_sequence = np.zeros((num_port, total_ticks))
    
    for i in range(len(channels)):
        m = 0
        for ramp in channels[i]['programmable_sequence']:
            if ramp['clk'] == True:
                #WILL apply variable clock, every sub-sequence should be 's' in this case
                k = 1
                sub_sequence = np.array(ramp['vf'])  # change from vi to vf, same below.. this will jump to vf for 's' ramp if vf != vi
            else:
                #WILL NOT apply variable clock
                k = int(round(ramp['dt']/ao_interval))
                if 'dv_s' in ramp: # this should only exists in 's' ramp.
                    sub_sequence = np.tile(np.array(ramp['vf']), k)
                else:
                    sub_sequence = np.linspace(ramp['vi'], ramp['vf'], k)
            ni_sequence[i, m: m + k] = sub_sequence
            m += k
            
    return ni_sequence    
    
    
    # for c in channels:
    #     channel_seq = []
    #     for ramp in c['programmable_sequence']:
    #         if ramp['clk'] == True:
    #             #WILL apply variable clock, every sub-sequence should be 's' in this case
    #             sub_seq = [ramp['vf']]  # change from vi to vf, same below.. this will jump to vf for 's' ramp if vf != vi
                    
    #         else:
    #             #WILL NOT apply variable clock
    #             if 'dv_s' in ramp: # this should only exists in 's' ramp.
    #                 sub_seq = [ramp['vf']]*int(round(ramp['dt']/ao_interval))
    #             else:
    #                 sub_seq = list(np.linspace(ramp['vi'], ramp['vf'], int(round(ramp['dt']/ao_interval))))                
    #         channel_seq.extend(sub_seq)
    #     ni_sequence.append(channel_seq)
        
    # ni_sequence = np.asarray(ni_sequence)
    # return ni_sequence
    
    
    
    
    
    
    
    