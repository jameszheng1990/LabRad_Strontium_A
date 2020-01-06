"""
### BEGIN NODE INFO
[info]
name = camera
version = 1.0
description = 
instancename = camera

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
import json

from labrad.server import setting
from labrad.server import setting
from twisted.internet import reactor

from device_server.server import DeviceServer


class CameraServer(DeviceServer):
    """ Provides basic control for cameras """
    name = 'camera'

Server = CameraServer

if __name__ == '__main__':
    from labrad import util
    reactor.suggestThreadPoolSize(5)
    util.runServer(Server())
