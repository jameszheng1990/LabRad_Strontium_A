import json

from conductor.parameter import ConductorParameter
from current_controller.devices import blue_slave_1
from update.proxy import UpdateProxy
from twisted.internet.reactor import callInThread


class IsLocked(ConductorParameter, blue_slave_1.BlueSlave1Proxy):
    autostart = True
    priority = 1
    call_in_thread = True
    
    def initialize(self, config):
        super(IsLocked, self).initialize(config)
        self._update = UpdateProxy('Blue Slave 1')   # Should have the same name as in current controller client..
        callInThread(self.update)
        
    def update(self):
        moncurrent = self.moncurrent
        lock_threshold = self.threshold
        self.value = bool(moncurrent > lock_threshold)
        self._update.emit({'moncurrent': moncurrent})  # Will update value on current controller.. in principle..

Parameter = IsLocked