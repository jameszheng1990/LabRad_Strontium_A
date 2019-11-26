class NIProxy(object):
    def __init__(self, server):
        self._server = server

    def niCFrontPanel(self):
        """ This class is the workhorse of the FrontPanel API. 
        
        It's methods are organized into three main groups: Device Interaction, 
        Device Configuration, and FPGA Communication. In a typical application, 
        your software will perform the following steps:
        
        1. Create an instance of okCFrontPanel.
        2. Using the Device Interaction methods, find an appropriate XEM with which 
        to communicate and open that device.
        3. Configure the device PLL (for devices with an on-board PLL).
        4. Download a configuration file to the FPGA using ConfigureFPGA(...).
        5. Perform any application-specific communication with the FPGA using the 
        FPGA Communication methods.    
        """
        return niFrontPanelProxy(self._server)

class niFrontPanelProxy(object):
    """ This class is the workhorse of the FrontPanel API. 
    
    It's methods are organized into three main groups: Device Interaction, 
    Device Configuration, and FPGA Communication. In a typical application, 
    your software will perform the following steps:
    
    1. Create an instance of okCFrontPanel.
    2. Using the Device Interaction methods, find an appropriate XEM with which 
    to communicate and open that device.
    3. Configure the device PLL (for devices with an on-board PLL).
    4. Download a configuration file to the FPGA using ConfigureFPGA(...).
    5. Perform any application-specific communication with the FPGA using the 
    FPGA Communication methods.    
    """
    def __init__(self, server):
        self._server = server

    def Write_DO_Manual(self, boolean):
        """ Writes a manual DO to Dev1, for all channels

        Args:
            boolean (bool): The output
        """ 
        return self._server.write_do_manual(boolean)

    def Write_AO_Manual(self, voltage, port):
        """ Writes a manual AO voltage to Dev2.

        Args:
            voltage (float): The output voltage
            port (int): address of port
        """ 
        return self._server.write_ao_manual(voltage, port)

    def Write_DO_Sequence(self, sequence):
        """ Writes a DO sequence to Dev1.

        Args:
            sequence (str): The sequence must be in string at this level,
            i.e. [[...],...,[...]]
        """
        return self._server.write_do_sequence(sequence)
    
    def Write_AO_Sequence(self, sequence):
        """ Writes a AO sequence to Dev2.

        Args:
            sequence (str): The sequence must be in string at this level,
            i.e. [[...],...,[...]]
        """
        return self._server.write_ao_sequence(sequence)