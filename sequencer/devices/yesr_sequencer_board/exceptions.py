import traceback

class TimeOutOfBoundsError(Exception):
    def __init__(self, time, ticks, clk):
        traceback.print_exc()
        message = 'time {} [s] corresponds to {} {} [Hz] clock cycles'.format(time, ticks, clk)
        super(TimeOutOfBoundsError, self).__init__(message)

class CombineError(Exception):
    def __init__(self, channel_key):
        # traceback.print_exc()
        # message = 'Combine error {}'.format(channel_key)
        # super(CombineError, self).__init__(message)
        # print(message)
        pass
    
class SequenceNotFound(Exception):
    def __init__(self, sequencename):
        message = 'Sequence not found: {}'.format(sequencename)
        print(message)
        pass
