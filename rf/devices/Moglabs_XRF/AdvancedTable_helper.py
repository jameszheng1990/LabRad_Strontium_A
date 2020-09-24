
class SRamp(object):
    """ Hold at vi for dt of time.
        (TABLE, APPEND, ch, xparam, value, duration)
        
        value = vi
        duration = dt
    """
    
    inputs = ['vi', 'dt']
    
    def __init__(self, c = None, ch = None, xparam = None):
        self.c = c
        self.ch = ch
        self.xparam = xparam
        self.value = c.get('vi')
        self.duration = c.get('dt')
    
    def to_entry(self):
        return 'TABLE, APPEND, {}, {}, {}Hz, {}s'.format(self.ch, self.xparam,
                                                      self.value, self.duration)
        
class LinRamp(object):
    """ Linearly ramp from vi to vf in dt of time, rate is refresh rate.
        (TABLE, RAMP, ch, xparam, start, stop, duration, count)
        duration = rate, duration per step
        count = int(dt/rate), number of steps
        
        start = vi
        stop = vf
    """
    
    inputs = ['vi', 'vf',
              'dt', 'rate']
    
    def __init__(self, c = None, ch = None, xparam = None):
        self.c = c
        self.ch = ch
        self.xparam = xparam
        self.start = c.get('vi')
        self.stop = c.get('vf')
        
        rate = c.get('rate')
        dt = c.get('dt')
        self.duration = rate
        self.count = int(dt/rate)
    
    def to_entry(self):
        return 'TABLE, RAMP, {}, {}, {}Hz, {}Hz, {}s, {}'.format(self.ch, self.xparam,
                                                                 self.start, self.stop,
                                                                 self.duration, self.count)
    
class Loop(object):
    """ Loop from source to dest until condition is satisfied.
        (TABLE, LOOP, ch, source, dest, condition)   
        
        source and dest can be negative numbers, which are then taken as offsets.
        If source is negative, it is taken as an offset from the end of
        the table (requires TABLE,ENTRIES to be set). If dest is negative,
        it is taken as the offset from the source.
        
        The condition can be an integer in the range [1, 4095],
        corresponding to the number of times to execute the loop,
        or a hardware descriptor flag of the form IOxy,
        indicating to repeat until the digital input pin x exhibits behaviour y,
        as described below.
        
        vi = source
        vf = dest
        condition = condition
            H: terminate loop on logic level High at loop instruction
            L: terminate loop on logic level Low at loop instruction
            F: terminate loop after falling edge occurs
            R: terminate loop after rising edge occurs
    """
    
    def __init__(self, c = None, ch = None, xparam = None):
        self.c = c
        self.ch = ch
        self.xparam = xparam
        
        self.source = c.get('vi')
        self.dest = c.get('vf')
        self.condition = c.get('condition')
        
    def to_entry(self):
        return 'TABLE, LOOP, {}, {}, {}, {}'.format(self.ch, self.source,
                                                    self.dest, self.condition)
    
class EntryMaker(object):
    
    available_xparam = ['FREQ'] # currently we only work with FREQ.. might need PHASE later..
    fm_gain = 8 # Defalut to be 2 MHz
    
    available_entries = {'s': SRamp,
                         'lin': LinRamp, 
                         'loop': Loop,}
    
    def __init__(self, request = None, ch = None):
        self.request = request
        self.ch = ch
        self.xparam = self.get_xparam(request)
          
    def get_xparam(self, request):
        xparam = request.get('xparam')
        if xparam == 'FREQ':
            self.fm_gain = request.get('fm_gain')
        return xparam
    
    def get_xparam_entry(self):
        if self.xparam == 'FREQ':
            return 'TABLE, XPARAM, {}, {}, {}'.format(self.ch, self.xparam, self.fm_gain)
        else:
            return 'TABLE, XPARAM, {}, {}'.format(self.ch, self.xparam)
    
    def get_xparam_unit(self):
        if self.xparam == 'FREQ':
            return 'Hz'
        
    def merge_entries(self, request):
        merged_request = []
        for key, value in request.items():
            if 'entry' in key:
                merged_request.extend(value) 
        return merged_request
        
    def get_entries(self):
        entries = []
        entries.append('TABLE, CLEAR, {}'.format(self.ch))
        
        entry = self.get_xparam_entry()
        entries.append(entry)
        
        merged_entries = self.merge_entries(self.request)
        
        for j in merged_entries:
            entry = self.available_entries[j['type']](j, self.ch, self.xparam).to_entry()
            entries.append(entry)
        
        # The last entry can not be LinRamp/Loop..
        if merged_entries[-1]['type'] == 'lin':
            entries.append('TABLE, APPEND, {}, {}, {}{}, 32ns'.format(self.ch,
                                                                      self.xparam,
                                                                      merged_entries[-1]['vf'],
                                                                      self.get_xparam_unit()))
        
        elif merged_entries[-1]['type'] == 'loop':
            try:
                entries.append('TABLE, APPEND, {}, {}, {}{}, 32ns'.format(self.ch,
                                                                      self.xparam,
                                                                      merged_entries[-2]['vf'],
                                                                      self.get_xparam_unit()))
            except:
                entries.append('TABLE, APPEND, {}, {}, {}{}, 32ns'.format(self.ch,
                                                                      self.xparam,
                                                                      merged_entries[-2]['vi'],
                                                                      self.get_xparam_unit()))
                
        
        entries.append('TABLE, ARM, {}'.format(self.ch))
        return entries
        
        