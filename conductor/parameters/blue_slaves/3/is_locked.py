import json

from conductor.parameter import ConductorParameter
from current_controller.devices import blue_slave_3
from update.proxy import UpdateProxy
from twisted.internet.reactor import callInThread


class IsLocked(ConductorParameter, blue_slave_3.BlueSlave3Proxy):
    autostart = True
    priority = 1
    call_in_thread = True

    def initialize(self, config):
        super(IsLocked, self).initialize(config)
        self._update = UpdateProxy('blue_slave_3')
        callInThread(self.update)

    def update(self):
        moncurrent = self.moncurrent
        lock_threshold = self.threshold
        self.value = bool(moncurrent > lock_threshold)
        self._update.emit({'moncurrent': moncurrent})

Parameter = IsLocked