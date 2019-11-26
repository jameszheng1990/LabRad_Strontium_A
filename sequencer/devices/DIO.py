from device_server.device import DefaultDevice
from sequencer.devices.yesr_digital_board.device import YeSrDigitalBoard
from sequencer.devices.yesr_digital_board.channel import YeSrDigitalChannel

class DIO(YeSrDigitalBoard):
#    okfpga_server_name = 'sr_a-ok'
#    okfpga_device_id = '1'

    autostart = True
    is_master = True
    
    # i.e. D25: Dev1/port2/line5, D also stands for Digital
    
    channels = [
        YeSrDigitalChannel(loc=['D0', 0], name='3D MOT AOM', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D0', 1], name='3D MOT Shutter', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D0', 2], name='2D MOT Shutter', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D0', 3], name='ZS Shutter', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D0', 4], name='Probe AOM', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D0', 5], name='Probe Shutter', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D0', 6], name='Repumps', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D0', 7], name='Red MOT AOM', mode='auto', manual_output=False, invert=False),
        
        YeSrDigitalChannel(loc=['D1', 0], name='Red MOT Shutter', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D1', 1], name='CCD trigger', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D1', 2], name='None1', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D1', 3], name='None2', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D1', 4], name='None3', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D1', 5], name='None4', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D1', 6], name='None5', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D1', 7], name='Trigger', mode='auto', manual_output=False, invert=False),
        
        YeSrDigitalChannel(loc=['D2', 0], name='None6', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D2', 1], name='None7', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D2', 2], name='None8', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D2', 3], name='None9', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D2', 4], name='None10', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D2', 5], name='None11', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D2', 6], name='None12', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D2', 7], name='None13', mode='auto', manual_output=False, invert=False),
        
        YeSrDigitalChannel(loc=['D3', 0], name='None14', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D3', 1], name='None15', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D3', 2], name='None16', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D3', 3], name='None17', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D3', 4], name='None18', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D3', 5], name='None19', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D3', 6], name='None20', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D3', 7], name='None21', mode='auto', manual_output=False, invert=False),
        ]
    
#    def initialize(self, config):
#        YeSrDigitalBoard.initialize(self, config)
        
        
Device = DIO  #To be loaded by device server
