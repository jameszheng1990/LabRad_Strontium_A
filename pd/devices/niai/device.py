from collections import deque

from device_server.device import DefaultDevice
from ni_server.proxy import NIProxy

class NIAI(DefaultDevice):
    niai_servername = None
    samp_rate = None
    n_samples = None

    records = {}
    record_names = deque([])
    max_records = 100
    
    
    def initialize(self, config):
        super(NIAI, self).initialize(config)
        self.connect_to_labrad()
        self.niai_server = self.cxn[self.niai_servername]
        niai_proxy = NIProxy(self.niai_server)
        niai = niai_proxy.niCFrontPanel()

        self.niai = niai

#        self.picoscope_server.reopen_interface(self.picoscope_serialnumber)
#        for channel, settings in self.picoscope_channel_settings.items():
#            self.picoscope_server.set_channel(self.picoscope_serialnumber, 
#                                              channel, settings['coupling'], 
#                                              settings['voltage_range'], 
#                                              settings['attenuation'], 
#                                              settings['enabled'])
#        self.picoscope_server.set_sampling_frequency(self.picoscope_serialnumber, 
#                                                     self.picoscope_duration, 
#                                                     self.picoscope_frequency)
#        self.picoscope_server.set_simple_trigger(self.picoscope_serialnumber, 
#                                                 'External', 
#                                                 self.picoscope_trigger_threshold, 
#                                                 self.picoscope_timeout)
#        self.picoscope_server.memory_segments(self.picoscope_serialnumber,
#                                              self.picoscope_n_capture)
#        self.picoscope_server.set_no_of_captures(self.picoscope_serialnumber,
#                                                 self.picoscope_n_capture)

    def record(self, data_path):
        pass

    def retrive_record(self, record_name):
        if type(record_name).__name__ == 'int':
            record_name = self.record_names[record_name]
        if record_name not in self.records:
            message = 'cannot locate record: {}'.format(record_name)
            raise Exception(message)
        record = self.records[record_name]
        record['record_name'] = record_name
        return record
