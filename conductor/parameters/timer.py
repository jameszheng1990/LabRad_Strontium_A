from collections import deque
import numpy as np
import time

from conductor.parameter import ConductorParameter

class Timer(ConductorParameter):
    time_record = deque([], maxlen=1000)

    def initialize(self, config):
        super(Timer, self).initialize(config)

    def update(self):
        self.value = time.time()
        self.time_record.append(time.time())
        if len(self.time_record) > 2:
            cycle_times = np.diff(self.time_record)
            print("cycle time: {}({}) s".format(np.mean(cycle_times), np.std(cycle_times)))


Parameter = Timer
