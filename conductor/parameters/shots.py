from collections import deque
import numpy as np
import time

from conductor.parameter import ConductorParameter

class Shots(ConductorParameter):
    time_record = deque([], maxlen=1000)

    def initialize(self, config):
        super(Shots, self).initialize(config)

    def update(self):
        self.value += 1 

Parameter = Shots
