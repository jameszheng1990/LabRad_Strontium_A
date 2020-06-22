from datetime import date, timedelta
from itertools import chain
import json
import os
import time
import itertools

from device_server.device import DefaultDevice
from sequencer.devices.yesr_sequencer_board.helpers import time_to_ticks
from sequencer.devices.yesr_sequencer_board.helpers import combine_sequences
from ni_server.proxy import NIProxy
from sequencer.exceptions import ChannelNotFound
from sequencer.devices.yesr_sequencer_board.exceptions import CombineError, SequenceNotFound

class YeSrSequencerBoard(DefaultDevice):
    sequencer_type = None
    
    ni_servername = 'ni'
    ni_interface = None

    conductor_servername = 'conductor'

    channels = None
    total_channels = {}
    
    sequence_directory = 'C:\\LabRad\\SrSequences\\{}\\'
    subsequence_names = None
    sequence = None
    raw_sequene = None
    is_master = False
    master_channel = "3D MOT AOM@D00"
    run_priority = 0 

    loading = False
    running = False
    sequence = None
    sequence_bytes = None
    max_sequence_bytes = 24000*100
    
    def initialize(self, config):
        for key, value in config.items():
            setattr(self, key, value)
        
        for channel in self.channels:
            channel.set_board(self)
            self.total_channels.update({channel.key: channel})
        
        self.connect_to_labrad()
        
        self.ni_server = self.cxn[self.ni_servername]
        ni_proxy = NIProxy(self.ni_server)
        self.ni = ni_proxy.niCFrontPanel()
                
        self.update_mode()
        self.update_channel_modes()
        self.update_channel_manual_outputs()
        
        
    def load_sequence(self, sequencename):  # Will trace back for the sequence, starting from Today, yesterday and so on...
        for i in range(365):
            day = date.today() - timedelta(i)
            sequencepath = self.sequence_directory.format(day.strftime('%Y%m%d')) + sequencename
            if os.path.exists(sequencepath):
                break
        if not os.path.exists(sequencepath):
            # raise SequenceNotFound(sequencename)
            raise 'Sequence Error'
        
        with open(sequencepath, 'r') as infile:
            sequence = json.load(infile)
        return sequence

    def save_sequence(self, sequence, sequence_name, tmpdir=True):
        sequence_directory = self.sequence_directory.format(time.strftime('%Y%m%d'))
        if tmpdir:
            sequence_directory = os.path.join(sequence_directory, '.tmp')
        if not os.path.exists(sequence_directory):
            os.makedirs(sequence_directory)
        sequence_path = os.path.join(sequence_directory, sequence_name)
        with open(sequence_path, 'w+') as outfile:
            json.dump(sequence, outfile)

    def get_channel(self, channel_id, suppress_error=False):
        """
        expect 3 possibilities for channel_id.
        1) name -> return channel with that name
        2) @loc -> return channel at that location
        3) name@loc -> first try name, then location
        """
        channel = None

        nameloc = channel_id.split('@') + ['']
        name = nameloc[0]
        loc = nameloc[1]
        if name:
           for c in self.channels:
               if c.name == name:
                   channel = c
        if not channel:
            for c in self.channels:
                if c.loc == loc:
                    channel = c
        if (channel is None) and not suppress_error:
            raise ChannelNotFound(channel_id)
        return channel
    
    def match_sequence_key(self, channel_sequences, channel_key):
        channel_nameloc = channel_key.split('@') + ['']
        channel_name = channel_nameloc[0]
        channel_loc = channel_nameloc[1]

        for sequence_key, sequence in channel_sequences.items():
            sequence_nameloc = sequence_key.split('@') + ['']
            if sequence_nameloc == channel_nameloc:
                return sequence_key

        for sequence_key, sequence in channel_sequences.items():
            sequence_name = (sequence_key.split('@') + [''])[0]
            if sequence_name == channel_name:
                return sequence_key

        for sequence_key, sequence in channel_sequences.items():
            sequence_loc = (sequence_key.split('@') + [''])[1]
            if sequence_loc == channel_loc:
                return sequence_key

    def update_channel_modes(self):
        """ to be implemented by child class """
   
    def update_channel_manual_outputs(self): 
        """ to be implemented by child class """

    def default_sequence_segment(self, channel, dt):
        """ to be implemented by child class """


    # def fix_sequence_keys(self, subsequence_names, tmpdir):
    #     for subsequence_name in set(subsequence_names):
    #         subsequence = self.load_sequence(subsequence_name)
    #         master_subsequence = subsequence[self.master_channel]
    #         for channel in self.channels:
    #             channel_subsequence = None
    #             matched_key = self.match_sequence_key(subsequence, channel.key)
    #             if matched_key:
    #                 channel_subsequence = subsequence.pop(matched_key)
    #             if not channel_subsequence:
    #                 channel_subsequence = [
    #                     self.default_sequence_segment(channel, s['dt'])
    #                         for s in master_subsequence
    #                     ]
    #             subsequence.update({channel.key: channel_subsequence})

    #         self.save_sequence(subsequence, subsequence_name, tmpdir)
    
    def do_default_sequence_segment(channel, dt):
        return {'dt': dt, 'out': channel.manual_output}

    def ao_default_sequence_segment(self, channel, dt):
        return {'dt': dt, 'type': 's', 'vf': channel.manual_output}
    
    def fix_sequence_keys(self, subsequence_names, tmpdir = False):
        for subsequence_name in set(subsequence_names):
            subsequence = self.load_sequence(subsequence_name)
            master_channel_subsequence = subsequence[self.master_channel]
            for channel_key, channel in self.total_channels.items():
                channel_subsequence = []
                matched_key = self.match_sequence_key(subsequence, channel.key)
                if matched_key:
                    channel_subsequence = subsequence.pop(matched_key)
                if not channel_subsequence:
                    if 'AO' in channel.key:
                        channel_subsequence = [
                            self.ao_default_sequence_segment(channel, s['dt'])
                            for s in master_channel_subsequence
                            ]
                    if 'D' in channel.key:
                        channel_subsequence = [
                            self.do_default_sequence_segment(channel, s['dt'])
                            for s in master_channel_subsequence
                            ]
                subsequence.update({channel.key: channel_subsequence})
                
            self.save_sequence(subsequence, subsequence_name, False)    

    def combine_subsequences(self, subsequence_list):
        try:
            combined_sequence = {}
            for channel_key in self.total_channels.keys():
                channel_sequence = []
                for subsequence in subsequence_list:
                    channel_sequence += subsequence[channel_key]
                combined_sequence[channel_key] = channel_sequence
            return combined_sequence
        except:
            raise CombineError(channel_key)
        
    def set_sequence(self, device_name, subsequence_names):
        
        try:
            self._set_sequence(device_name, subsequence_names)
        except CombineError:
            self.fix_sequence_keys(subsequence_names)
            self._set_sequence(device_name, subsequence_names)
        # except SequenceNotFound:
        #     return

    def _set_sequence(self, device_name, subsequence_names):
        self.subsequence_names = subsequence_names
        self.device_name = device_name
        
        conductor_server = self.cxn[self.conductor_servername]
        
        subsequence_list = []
        for subsequence_name in subsequence_names:
            subsequence = self.load_sequence(subsequence_name)
            if subsequence_name[:5] == 'PROG_':
                DO_parameter_name = 'sequencer.DO_parameters.' + subsequence_name[5:]
                request = json.dumps({DO_parameter_name : None})
                parameter_values_json = conductor_server.get_parameter_values(request)  
                parameter_values = json.loads(parameter_values_json)
                subsequence = self.substitute_sequence_DO_values(subsequence, parameter_values)
                
            subsequence_list.append(subsequence)
        
        raw_sequence = self.combine_subsequences(subsequence_list)
        
        parameter_names = self.get_sequence_parameter_names(raw_sequence)
        parameter_values = self.get_sequence_AO_parameter_values(parameter_names)
        programmable_sequence = self.substitute_sequence_AO_values(raw_sequence, parameter_values)
        
        self.programmable_sequence = programmable_sequence
        self.set_programmable_sequence(programmable_sequence, device_name)
        
    def get_sequence(self):
        return self.subsequence_names
    
    def set_programmable_sequence(self, programmable_sequence, device_name):
        
        if device_name == 'AO':
            sequence_bytes = self.make_sequence_bytes(programmable_sequence) # TODO
            
            self.set_loading(True)
            self.ni.Write_AO_Sequence(sequence_bytes)
            self.set_loading(False)
         
        elif device_name == 'DIO':
            sequence_bytes = self.make_sequence_bytes(programmable_sequence) # TODO
            
            self.set_loading(True)
            self.ni.Write_DO_Sequence(sequence_bytes)
            self.set_loading(False)
        
        elif device_name == 'Z_CLK':
            sequence_bytes = self.make_clk_sequence(programmable_sequence)
            
            self.set_loading(True)
            self.ni.Write_CLK_Sequence(sequence_bytes)
            self.set_loading(False)
            
    def get_programmable_sequence(self):
        return self.programmable_sequence
    
    def get_sequence_parameter_names(self, x):  
        if type(x).__name__ in ['str', 'unicode'] and x[0] == '*':
            return [x]
        elif type(x).__name__ == 'list':
            return set(list(chain.from_iterable([
                self.get_sequence_parameter_names(xx) 
                for xx in x])))
        elif type(x).__name__ == 'dict':
            return list(chain.from_iterable([
                self.get_sequence_parameter_names(v) 
                # for v in x.values()])))  #why dict values?
                for v in x.keys()]))
        else:
            return []
    
    def get_sequence_AO_parameter_values(self, parameter_names):
        if parameter_names:
            request = {
                parameter_name.split('@')[0].replace('*', 'sequencer.AO_parameters.'): None
                    for parameter_name in parameter_names
                }
            
            conductor_server = self.cxn[self.conductor_servername]
            parameter_values_json = conductor_server.get_parameter_values(json.dumps(request))  
            parameter_values = json.loads(parameter_values_json)
        else:
            parameter_values = {}
            
        sequence_parameter_values = {
            name.replace('sequencer.AO_parameters.', '*') : value
                for name, value in parameter_values.items()
            }
        
        # match key names that works for sequencer
        for old_key in sequence_parameter_values.keys():
            for parameter_name in parameter_names:
                if old_key in parameter_name:
                    sequence_parameter_values[parameter_name] = sequence_parameter_values.pop(old_key)
                    
        return sequence_parameter_values
 
    def substitute_sequence_AO_values(self, raw_sequence, parameter_values):
        """this will change the specific AO output to some constant value set in experiment,
           this should be useful for experiment at different trap depth.
        """
        for parameter_key, parameter_value in parameter_values.items():
            if parameter_value is not None:
                for key, value in raw_sequence.items():
                    if parameter_key == key:
                        for i in value:
                            i.update({'type':'s', 'vf':parameter_value})
        return raw_sequence
 
    def substitute_sequence_DO_values(self, subsequence, parameter_values):
        """this will change the duration of pulses, for example, used for ramsey/rabi or TOF experiment.
           only accepts one column.
        """
        for parameter_key, parameter_value in parameter_values.items():
            if parameter_value is not None:
                for key, value in subsequence.items():
                    value[0].update({'dt': parameter_value})
        return subsequence
    
    def make_sequence_bytes(self, sequence):
        """ to be implemented by child class """
    
    def make_clock_sequence(self, sequence):
        """ to be implemented by child class """
    
    def update_mode(self):
        pass
#        mode_word = 0 | 2 * int(self.loading) | self.running
#        self.fp.SetWireInValue(self.mode_wire, mode_word)
#        self.fp.UpdateWireIns()
            
    def set_loading(self, loading):
        if loading is not None:
            self.loading = loading
            # self.update_mode()
    
    def get_loading(self):
        return self.running
    
    def set_running(self, device_name, running):
        if running is True:
            if device_name == 'AO':
                self.running = running
                self.ni.Start_AO_Sequence()
            
            if device_name == 'DIO':
                self.running = running
                self.ni.Start_DO_Sequence()

            if device_name == 'Z_CLK':
                self.running = running
                self.ni.Start_CLK_Sequence()
                
        else:
            self.running = running
            
            
    def get_running(self):
        return self.running
