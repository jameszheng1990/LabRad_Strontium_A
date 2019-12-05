""" proxy for controlling serial devices on remote computer through labrad

example usage:
    
    import labrad
    from serial_server.proxy import SerialProxy
    
    cxn = labrad.connect()
    serial = SerialProxy(cxn.yesr5_serial)
    
    # ``serial'' now acts like pyserial 3.x library
    ser = serial.Serial('COM10')
    ser.timeout = 0.1
    ser.write(b'hello!\n')
    ser.readline()
"""


class SerialProxy(object):
    def __init__(self, serial_server):
        self.serial_server = serial_server

    def Serial(self, port):
        ser = Serial(self.serial_server, port)
        return ser

class Serial(object):
    def __init__(self, serial_server, port):
        self.serial_server = serial_server
        self.port = port
        self.serial_server.reopen_interface(self.port)

    @property
    def baudrate(self):
        return self.serial_server.baudrate(self.port)
    
    @baudrate.setter
    def baudrate(self, baudrate):
        self.serial_server.baudrate(self.port, baudrate)

    @property
    def bytesize(self):
        return self.serial_server.bytesize(self.port)
    
    @bytesize.setter
    def bytesize(self, bytesize):
        self.serial_server.bytesize(self.port, bytesize)
    
    @property
    def dsrdtr(self):
        return self.serial_server.dsrdtr(self.port)
    
    @dsrdtr.setter
    def dsrdtr(self, dsrdtr):
        self.serial_server.dsrdtr(self.port, dsrdtr)
    
    @property
    def parity(self):
        return self.serial_server.parity(self.port)
    
    @parity.setter
    def parity(self, parity):
        self.serial_server.parity(self.port, parity)
    
    def read(self, size=1):
        return self.serial_server.read(self.port, size)
    
    def read_until(self, expected='\n', size=1):
        return self.serial_server.read_until(self.port, expected, size)
    
    def readline(self, size=-1):
        return self.serial_server.readline(self.port, size)
    
    def readlines(self, size=-1):
        return self.serial_server.readlines(self.port, size)
    
    @property
    def rtscts(self):
        return self.serial_server.rtscts(self.port)
    
    @rtscts.setter
    def rtscts(self, rtscts):
        self.serial_server.rtscts(self.port, rtscts)
    
    @property
    def stopbits(self):
        return self.serial_server.stopbits(self.port)
    
    @stopbits.setter
    def stopbits(self, stopbits):
        self.serial_server.stopbits(self.port, stopbits)
    
    @property
    def timeout(self):
        return self.serial_server.timeout(self.port)
    
    @timeout.setter
    def timeout(self, timeout):
        self.serial_server.timeout(self.port, timeout)
    
    def write(self, data):
        return self.serial_server.write(self.port, data)
    
    def writelines(self, data):
        return self.serial_server.writelines(self.port, data)
