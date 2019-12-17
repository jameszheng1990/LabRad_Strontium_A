import time

from conductor.parameter import ConductorParameter

class Timestamp(ConductorParameter):
    """ value set by sequencer.sequence """ 
    autostart = True
    priority = 1

Parameter = Timestamp
