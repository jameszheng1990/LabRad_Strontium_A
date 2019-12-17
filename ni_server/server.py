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
import nidaqmx, json, time
from nidaqmx.constants import LineGrouping
import numpy as np

from twisted.internet.defer import DeferredLock
from labrad.server import setting
from server_tools.threaded_server import ThreadedServer

from sequencer.devices.timing import config


class NIServer(ThreadedServer):
    name = 'ni'
    
    def initServer(self):
        self.rate_do = config().set_do_rate()
        self.timeout_do = 60
        self.clk_channel_do = 'PFI4'
        
        self.rate_ao = config().set_ao_rate()
        self.timeout_ao = 60
        self.trigger_channel = 'PFI0'
        self.clk_channel_ao = 'PFI1'
        
        self.rate_clk = config().set_clk()
        self.source = '100kHzTimebase'
#        self.source = 'PXI_Clk10'
        self.timeout_clk = 60
        
        self.seq_task_ao = None
        self.seq_task_do = None
        self.seq_task_clk = None
        
        self.conductor_trigger = False
        self.conductor_trigger_once = False
        
    
    @setting(31)
    def is_triggered(self, c):
        conductor_trigger = self.conductor_trigger
        return conductor_trigger
    
    @setting(32)
    def trigger_on(self, c):
        self.conductor_trigger = True
        
    @setting(33)
    def trigger_off(self, c):
        self.conductor_trigger = False
        
    @setting(34)
    def is_triggered_once(self, c):
        conductor_trigger_once = self.conductor_trigger_once
        return conductor_trigger_once
    
    @setting(35)
    def trigger_once_on(self, c):
        self.conductor_trigger_once = True
        
    @setting(36)
    def trigger_once_off(self, c):
        self.conductor_trigger_once = False
    
    @setting(1)
    def write_ao_manual(self, c, voltage, port):
        """
        Writes Voltage for ONE channel that we are interested in
        """
        if self.seq_task_ao: # Make sure task is close before you add new stuffs.
            self.seq_task_ao.close()
            self.seq_task_ao = None
            
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev2/ao{}'.format(port))
            
            task.write(voltage, auto_start = True)
            task.stop()
            
    @setting(2)
    def write_do_manual(self, c, boolean):
        """
        Writes Boolean for channels set to "manual"
        """
        if self.seq_task_do: # Make sure task is close before you add new stuffs.
            self.seq_task_do.close()
            self.seq_task_do = None
        
        with nidaqmx.Task() as task:
            task.do_channels.add_do_chan('Dev1/port0/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
            task.do_channels.add_do_chan('Dev1/port1/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
            task.do_channels.add_do_chan('Dev1/port2/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
            task.do_channels.add_do_chan('Dev1/port3/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
            
            task.write(boolean, auto_start = True)
            task.stop()

    @setting(3)
    def write_clk_manual(self, c, boolean):
        """
        CLK Manual value is always False
        """
        if self.seq_task_clk: # Make sure task is close before you add new stuffs.
            self.seq_task_clk.close()
            self.seq_task_clk = None
            
        with nidaqmx.Task() as task:
            task.do_channels.add_do_chan('Dev0/port0/line0')
           
            task.write(boolean, auto_start = True)
            task.stop()
    
    @setting(4)
    def write_ao_sequence(self, c, sequence = 's'):
        """
        AO triggered by the first rising edge from PFI0 channel. Therefore you should run AO first, then DIO (to trigger AO). (NO NEED For variable REF clock)
        NOT all AO channels are written, we selecte channels by the length of sequence, in principle it should be >2.
        """
        sequence_json = json.loads(sequence)
        
        num_port = len(sequence_json)
        num_samp = len(sequence_json[0])
        
        if self.seq_task_ao: # Make sure task is close before you add new stuffs.
            self.seq_task_ao.close()
        
        self.seq_task_ao = nidaqmx.Task()
        self.seq_task_ao.ao_channels.add_ao_voltage_chan('Dev2/ao0:{}'.format(num_port-1))
        self.seq_task_ao.timing.cfg_samp_clk_timing(rate = self.rate_ao, source = self.clk_channel_ao, samps_per_chan = num_samp)    #rate, samps_per_chan
        # self.seq_task_ao.triggers.start_trigger.cfg_dig_edge_start_trig(self.trigger_channel)  # Default with rising edge  
        # If share the same clock, there is no need to use DO trigger
        
        self.seq_task_ao.write(sequence_json, auto_start = False, timeout = -1)
    
    @setting(5)
    def write_do_sequence(self, c, sequence = 's'):
        """
        We write all 32 DIO channels at a time.
        Default time-out is 60 s, which sets the limit of total sequence length.
        """
        sequence_json = json.loads(sequence)
        
        num_samp = len(sequence_json[0])
        
        if self.seq_task_do: # Make sure task is close before you add new stuffs.
            self.seq_task_do.close()
            
        self.seq_task_do = nidaqmx.Task()
        self.seq_task_do.do_channels.add_do_chan('Dev1/port0/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
        self.seq_task_do.do_channels.add_do_chan('Dev1/port1/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
        self.seq_task_do.do_channels.add_do_chan('Dev1/port2/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
        self.seq_task_do.do_channels.add_do_chan('Dev1/port3/line0:7', line_grouping=LineGrouping.CHAN_PER_LINE)
        self.seq_task_do.timing.cfg_samp_clk_timing(rate = self.rate_do, source = self.clk_channel_do, samps_per_chan = num_samp)    #rate, samps_per_chan
        
        self.seq_task_do.write(sequence_json, auto_start = False, timeout = -1)
     
    @setting(6)
    def write_clk_sequence(self, c, sequence = 's'):
        """
        We use port0/line0 on AI card (for temporary as of Nov. 26th 2019) as the "Variable Clock Reference" to sample 
        the DIO card and AO card.
        """
        sequence_json = json.loads(sequence)
        
        num_samp = len(sequence_json)
        
        if self.seq_task_clk: # Make sure task is close before you add new stuffs.
            self.seq_task_clk.close()
            
        self.seq_task_clk = nidaqmx.Task()
        self.seq_task_clk.do_channels.add_do_chan('Dev0/port0/line0')
        self.seq_task_clk.timing.cfg_samp_clk_timing(rate = self.rate_clk, source = self.source, samps_per_chan = num_samp)    #rate, samps_per_chan
            
        self.seq_task_clk.write(sequence_json, auto_start = False, timeout = -1)
        print('Write sequence to DAQ.')
    
    @setting(11)
    def start_ao_sequence(self, c):
        if self.seq_task_ao.is_task_done():
            self.seq_task_ao.start()
            
        else:
            print('Sequencer AO tasks do not exist!')
    
    @setting(12)
    def start_do_sequence(self, c):
        if self.seq_task_do.is_task_done():
            self.seq_task_do.start()
            
        else:
            print('Sequencer DO tasks do not exist!')
    
    @setting(13)
    def start_clk_sequence(self, c):
        if self.seq_task_clk.is_task_done():
            self.seq_task_clk.start()
            
            self.seq_task_ao.wait_until_done(self.timeout_ao)
            self.seq_task_do.wait_until_done(self.timeout_do)
            self.seq_task_clk.wait_until_done(self.timeout_clk)
            
            self.seq_task_clk.stop()
            self.seq_task_do.stop()        
            self.seq_task_ao.stop()
            
            print('Run sequence on DAQ.')
        
        else:
            print('Sequencer CLK tasks do not exist!')
        
    # @setting(11)
    # def stop_sequence(self, c):
    #     if self.seq_task_clk != None and self.seq_task_do != None and self.seq_task_ao != None:
    #         self.seq_task_clk.close()
    #         self.seq_task_do.close()
    #         self.seq_task_ao.close()
        
    #     else:
    #         pass
    
    @setting(20)
    def reset_devices(self, c):
        available_devices = list(nidaqmx.system.System.local().devices)
        if available_devices:
            for device in available_devices:
                device.reset_device()
        else:
            pass
            
    
Server = NIServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
