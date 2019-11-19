import os
import sys
sys.path.append(os.getenv('PROJECT_LABRAD_TOOLS_PATH'))

from device_server.device import DefaultDevice
from sequencer.devices.yesr_analog_board.device import YeSrAnalogBoard
from sequencer.devices.yesr_analog_board.channel import YeSrAnalogChannel

class AO(YeSrAnalogBoard):
#    okfpga_server_name = 'sr_a-ok'
#    okfpga_device_id = '1'

    autostart = True
    is_master  =False
    
    channels = [
        YeSrAnalogChannel(loc= 0, name='MOT coils', mode='auto', manual_output=0.0, voltage_range=(-7.0, 0)),
        YeSrAnalogChannel(loc= 1, name='Red MOT Freq', mode='auto', manual_output=0.0, voltage_range=(-1.0, 1.0)),
        YeSrAnalogChannel(loc= 2, name='Red MOT Int', mode='auto', manual_output=0.0, voltage_range=(-1.0, 1.0)),
        ]
    
    def initialize(self, config):
        YeSrAnalogBoard.initialize(self, config)
        
        
Device = AO  #To be loaded by device server
