import os
import sys
sys.path.append(os.getenv('PROJECT_LABRAD_TOOLS_PATH'))

from sequencer.devices.yesr_digital_board.exceptions import TimeOutOfBoundsError

def time_to_ticks(interval, time):
    ticks = int(round(time/interval))
    return ticks

def get_output(channel_sequence, t):
    for s in channel_sequence[::-1]:
        if s['t'] <= t:
            return s['out']
