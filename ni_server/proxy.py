import json, time

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
    
    def Write_CLK_Manual(self, boolean):
        self._server.write_clk_manual(boolean)
        
    def Write_DO_Manual(self, boolean):
        """ Writes a manual DO to Dev1, for all channels

        Args:
            boolean (bool): The output
        """ 
        self._server.write_do_manual(boolean)

    def Write_AO_Manual(self, voltage, port):
        """ Writes a manual AO voltage to Dev2.

        Args:
            voltage (float): The output voltage
            port (int): address of port
        """ 
        self._server.write_ao_manual(voltage, port)

    def Write_AO_Sequence(self, sequence):
        """ Writes a AO sequence to Dev2.

        Args:
            sequence (str): The sequence must be in string at this level,
            i.e. '[[...],...,[...]]'
            use json.dumps(sequence) to implement
        """
        sequence_json = json.dumps(sequence)
        self._server.write_ao_sequence(sequence_json)

    def Write_AO_Raw_Sequence(self, raw_sequence_channels_list):
        """ Write AO raw sequence to Dev1, using import channels

        Args:
            sequence (str): The sequence must be in string at this level,
            i.e. '[[...],...,[...]]'
        """
        raw_sequence_channels_list_json = json.dumps(raw_sequence_channels_list)
        self._server.write_ao_raw_sequence(raw_sequence_channels_list_json)
        
    def Write_DO_Sequence(self, sequence):
        """ Writes a DO sequence to Dev1.

        Args:
            sequence (str): The sequence must be in string at this level,
            i.e. '[[...],...,[...]]'
        """
        sequence_json = json.dumps(sequence)
        self._server.write_do_sequence(sequence_json)
    
    def Write_DO_Raw_Sequence(self, raw_sequence, channels_list):
        """ Write DO raw sequence to Dev1, using import channels

        Args:
            sequence (str): The sequence must be in string at this level,
            i.e. '[[...],...,[...]]'
        """
        raw_sequence_json = json.dumps(raw_sequence)
        channels_list_json = json.dumps(channels_list)
        self._server.write_do_raw_sequence(raw_sequence_json, channels_list_json)
    
    def Write_CLK_Sequence(self, sequence_path):
        """Writes the Clk sequence to Dev0.
        """
        self._server.write_clk_sequence(sequence_path)

    def Write_CLK_Raw_Sequence(self, raw_sequence):
        """Writes the Clk raw sequence to Dev0.
        """
        raw_sequence_json = json.dumps(raw_sequence)
        self._server.write_clk_raw_sequence(raw_sequence_json)
        
    def Start_AO_Sequence(self):
        """
        Start AO sequences for conductor.
        """
        self._server.start_ao_sequence()
    
    def Start_DO_Sequence(self):
        """
        Start DO sequences for conductor.
        """
        self._server.start_do_sequence()

    def Start_CLK_Sequence(self):
        """
        Start CLK sequences for conductor.
        """
        self._server.start_clk_sequence()
    
    def Read_AI_Manual(self, port):
        """ Read an AI channel for an arbitrary port,
        
        Args:
            port (int): The input port from A0 to A7
        """ 
        return self._server.read_ai_manual(port)
        
    def Read_PD_AI(self, port, samp_rate, n_samp):
        """ Read an AI channel for PD voltage in trigger mode.
        
        Args:
            port (int): The input port from A0 to A7
        """ 
        return self._server.pd_ai_trigger(port, samp_rate, n_samp)
    
    def Reset_Devices(self):
        """
        Reset all devices, stop all runnig tasks.
        """
        self._server.reset_devices()