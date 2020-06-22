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
import h5py

from twisted.internet.defer import DeferredLock
from labrad.server import setting
from server_tools.threaded_server import ThreadedServer

from sequencer.devices.timing import config


class NIServer(ThreadedServer):
    """ Provide access to NI DAQ via nidaqmx."""
    name = 'ni'
    
    def initServer(self):
        
        self.rate_do = config().set_do_rate()
        self.timeout_do = 150
        self.clk_channel_do = 'PFI4'
        
        self.rate_ao = config().set_ao_rate()
        self.timeout_ao = 150
        self.trigger_channel = 'PFI0'
        self.clk_channel_ao = 'PFI1'
        
        self.rate_clk = config().set_clk()
        # self.source = '100kHzTimebase'
        # self.source = 'PXI_Clk10' # Internal clock source, 10 MHz
        self.source = 'PFI0'  #External CLK source input, 10 MHz
        self.timeout_clk = 150
        # (Variable clock output is = p0.0)
        
        self.seq_task_ao = None
        self.seq_task_do = None
        self.seq_task_clk = None
        
        self.ai_trigger = 'PFI1' # Should be PFI1
        self.pd_task_ai = None
        self.pmt_task_ai = None
        self.timeout_ai = 180

        super(NIServer, self).initServer()
        
    @setting(1)
    def write_ao_manual(self, c, voltage, port):
        """
        Writes Voltage for ONE channel that we are interested in.
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
        CLK Manual value is always False.
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
        We write all 32 DO channels at a time.
        Default time-out is 120 s, which sets the limit of total sequence length.
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
    def write_clk_sequence(self, c, sequence_path = 's'):
    # def write_clk_sequence(self, c, sequence):
        """
        We use port0/line0 on AI card as the "Variable Clock Reference" to sample the DO and AO card.
        """
        
        sequence = np.load(sequence_path + '.npy').tolist()
        # sequence = sequence.tolist()
        
        num_samp = len(sequence)
        if self.seq_task_clk: # Make sure task is close before you add new stuffs.
            self.seq_task_clk.close()
            
        self.seq_task_clk = nidaqmx.Task()
        self.seq_task_clk.do_channels.add_do_chan('Dev0/port0/line0')
        
        self.seq_task_clk.timing.cfg_samp_clk_timing(rate = self.rate_clk, source = self.source, samps_per_chan = num_samp)    #rate, samps_per_chan
        
        self.seq_task_clk.write(sequence, auto_start = False, timeout = -1)
        
    
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
            
            print('DAQ tasks started.')
            
            self.seq_task_ao.wait_until_done(self.timeout_ao)
            self.seq_task_do.wait_until_done(self.timeout_do)
            self.seq_task_clk.wait_until_done(self.timeout_clk)
                   
            self.seq_task_ao.stop()
            self.seq_task_do.stop() 
            self.seq_task_clk.stop()
            
            print('DAQ tasks done.')
        
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
    
    @setting(15)
    def read_ai_manual(self, c, port):
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan("Dev0/ai{}".format(port))
            data = task.read()
        return data
    
    @setting(16, returns = 's')
    def pd_ai_trigger(self, c, port, samp_rate, n_samp):
        """
        Read Analog-In voltage for PD in Trigger Mode
        """
        if self.pd_task_ai: # Make sure task is close before you add new stuffs.
            self.pd_task_ai.close()
        
        self.pd_task_ai = nidaqmx.Task()
        self.pd_task_ai.ai_channels.add_ai_voltage_chan("Dev0/ai{}".format(port))
        self.pd_task_ai.timing.cfg_samp_clk_timing(rate = int(samp_rate), samps_per_chan = int(n_samp))    #rate, samps_per_chan
        self.pd_task_ai.triggers.start_trigger.cfg_dig_edge_start_trig(self.ai_trigger)  # Default with rising edge  
        
        print('AI configured.')
        
        data = self.pd_task_ai.read(number_of_samples_per_channel = -1, timeout = self.timeout_ai)  # -1 means will read all available samples
        self.pd_task_ai.wait_until_done(self.timeout_ao)
        
        self.pd_task_ai.stop()
        data_json = json.dumps(data)
        return data_json
    
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
