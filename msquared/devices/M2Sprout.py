from msquared.devices.solstis.solstis import Solstis

class M2Sprout(Solstis):
    autostart = True
    
    socket_address = ('192.168.1.222', 39933)
    socket_timeout = 1

Device = M2Sprout
