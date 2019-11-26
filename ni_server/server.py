"""
### BEGIN NODE INFO
[info]
name = ni
version = 2.0
description = 
instancename = ni

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
import nidaqmx
from nidaqmx.constants import LineGrouping
import numpy as np

from twisted.internet.defer import DeferredLock
from labrad.server import setting
from server_tools.threaded_server import ThreadedServer

from sequencer.devices.yesr_digital_board.timing import config as do_config
from sequencer.devices.yesr_analog_board.timing import config as ao_config

class NIServer(ThreadedServer):
    name = 'ni'
    
    def initServer(self):
        self.rate_do = do_config().set_rate()
        self.interval_do = 1/self.rate_do
        self.timeout_do = 10
        
        self.rate_ao = ao_config().set_rate()
        self.interval_ao = 1/self.rate_ao
        self.timeout_ao = 15
        self.trigger_channel = 'PFI0'
        
    @setting(1)
    def write_do_manual(self, c, boolean):
        """
        Writes Boolean for channels set to "manual"
        """
        with nidaqmx.Task() as task:
            task.do_channels.add_do_chan('Dev1/port0/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
            task.do_channels.add_do_chan('Dev1/port1/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
            task.do_channels.add_do_chan('Dev1/port2/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
            task.do_channels.add_do_chan('Dev1/port3/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
            
            task.write(boolean, auto_start = True)
            task.stop()
    
    @setting(2)
    def write_ao_manual(self, c, voltage, port):
        """
        Writes Voltage for ONE channel that we are interested in
        """
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev2/ao{}'.format(port))
            
            task.write(voltage, auto_start = True)
            task.stop()
            
    @setting(3)
    def write_do_sequence(self, c, sequence):
        """
        We write all 32 DIO channels at a time.
        Default time-out is 10 s, which sets the limit of total sequence length.
        """
        with nidaqmx.Task() as task:
            num = len(sequence)
            task.do_channels.add_do_chan('Dev1/port0/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
            task.do_channels.add_do_chan('Dev1/port1/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
            task.do_channels.add_do_chan('Dev1/port2/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
            task.do_channels.add_do_chan('Dev1/port3/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
            
            task.timing.cfg_samp_clk_timing(rate = self.interval_do, samps_per_chan = num)    #rate, samps_per_chan
            task.write(sequence, auto_start = True)
            task.wait_until_done(self.timeout_do) 
            task.stop()
    
    @setting(4)
    def write_ao_sequence(self, c, sequence):
        """
        AO triggered by the first rising edge from PFI0 channel. Therefore you should run AO first, then DIO (to trigger AO).
        NOT all AO channels are written, we selected channels by the length of sequence, in principle it should be >2.
        """
        with nidaqmx.Task() as task:
            num = len(sequence)
            task.ao_channels.add_ao_voltage_chan('Dev2/ao{}'.format(num-1))
            
            task.timing.cfg_samp_clk_timing(rate = self.interval_ao, samps_per_chan = num)    #rate, samps_per_chan
            task.triggers.start_trigger.cfg_dig_edge_start_trig("PFI0")  # Default with rising edge
            task.write(sequence, auto_start = True)
            task.wait_until_done(self.timeout_ao) 
            task.stop()
            
Server = NIServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
