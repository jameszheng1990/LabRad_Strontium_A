from device_server.device import DefaultDevice
from sequencer.devices.yesr_digital_board.device import YeSrDigitalBoard
from sequencer.devices.yesr_digital_board.channel import YeSrDigitalChannel

class Z_CLK(YeSrDigitalBoard):
    
    # There should ONLY be one Digital Channel for "Z_CLK" board
    # It starts with "Z" just to make sure it was loaded lastly.

    autostart = True
    clk_channel = 'Dev0/port0/line0'
    
    channels = [
        YeSrDigitalChannel(loc=['Z_CLK', 0], name='CLK', mode='manual', manual_output=False, invert=False),
        ]
        
Device = Z_CLK  #To be loaded by device server
