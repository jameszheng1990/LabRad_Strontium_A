from device_server.device import DefaultDevice
from sequencer.devices.yesr_digital_board.device import YeSrDigitalBoard
from sequencer.devices.yesr_digital_board.channel import YeSrDigitalChannel

class DIO(YeSrDigitalBoard):

    autostart = True
    is_master = True
    
    channels = [
        YeSrDigitalChannel(loc=['D', 0], name='3D MOT AOM', mode='auto', manual_output=False, invert=True),
        YeSrDigitalChannel(loc=['D', 1], name='3D MOT Shutter', mode='auto', manual_output=False, invert=True),
        YeSrDigitalChannel(loc=['D', 2], name='2D MOT Shutter', mode='auto', manual_output=True, invert=True),
        YeSrDigitalChannel(loc=['D', 3], name='ZS Shutter', mode='auto', manual_output=False, invert=True),
        YeSrDigitalChannel(loc=['D', 4], name='Probe AOM', mode='auto', manual_output=True, invert=True),
        YeSrDigitalChannel(loc=['D', 5], name='Probe Shutter', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 6], name='Repumps AOM', mode='auto', manual_output=True, invert=False),
        YeSrDigitalChannel(loc=['D', 7], name='Repumps Shutter', mode='auto', manual_output=True, invert=True),
    
        YeSrDigitalChannel(loc=['D', 8], name='Red MOT TTL', mode='auto', manual_output=False, invert=True),
        YeSrDigitalChannel(loc=['D', 9], name='Red MOT Shutter', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 10], name='Red MOT Ramp Trigger', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 11], name='CCD trigger', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 12], name='None3', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 13], name='None4', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 14], name='None5', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 15], name='Trigger', mode='auto', manual_output=False, invert=False),  #AI card trigger
        
        YeSrDigitalChannel(loc=['D', 16], name='None6', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 17], name='None7', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 18], name='None8', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 19], name='None9', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 20], name='None10', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 21], name='None11', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 22], name='None12', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 23], name='None13', mode='auto', manual_output=False, invert=False),
        
        YeSrDigitalChannel(loc=['D', 24], name='None14', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 25], name='None15', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 26], name='None16', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 27], name='None17', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 28], name='None18', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 29], name='None19', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 30], name='None20', mode='auto', manual_output=False, invert=False),
        YeSrDigitalChannel(loc=['D', 31], name='None21', mode='auto', manual_output=False, invert=False),
        ]
          
Device = DIO  #To be loaded by device server