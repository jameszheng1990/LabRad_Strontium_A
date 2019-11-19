from device_server.device import DefaultDevice
from sequencer.devices.yesr_digital_board.device import YeSrDigitalBoard
from sequencer.devices.yesr_digital_board.channel import YeSrDigitalChannel

class DIO(YeSrDigitalBoard):
#    okfpga_server_name = 'sr_a-ok'
#    okfpga_device_id = '1'

    autostart = True
    is_master = True

    channels = [
        YeSrDigitalChannel(loc=['D', 0], name='3D MOT AOM', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 1], name='3D MOT Shutter', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 2], name='2D MOT Shutter', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 4], name='ZS Shutter', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 5], name='Probe AOM', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 6], name='Probe Shutter', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 7], name='Repumps', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 8], name='Red MOT AOM', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 9], name='Red MOT Shutter', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 10], name='CCD trigger', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 15], name='Trigger', mode='auto', manual_output=False, invert=False),
        ]
    
    def initialize(self, config):
        YeSrDigitalBoard.initialize(self, config)
        
        
Device = DIO  #To be loaded by device server
