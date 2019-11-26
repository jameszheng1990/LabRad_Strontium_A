import nidaqmx, json, time
import numpy as np
from nidaqmx.constants import (
    LineGrouping)

from sequencer.devices.yesr_analog_board.channel import YeSrAnalogChannel

channels = [
        YeSrAnalogChannel(loc=0, name='MOT coils', mode='manual', manual_output=1, voltage_range=(-7.0, 0)),
        YeSrAnalogChannel(loc=1, name='Red MOT Freq', mode='auto', manual_output=0.0, voltage_range=(-1.0, 1.0)),
        YeSrAnalogChannel(loc=2, name='Red MOT Int', mode='auto', manual_output=0.0, voltage_range=(-1.0, 1.0)),
        ]

cp_list = [c.loc for c in channels if c.mode == 'manual']
co_list = [c.manual_output for c in channels if c.mode == 'manual']

for c, w in zip(cp_list, co_list):
    print(c, w)