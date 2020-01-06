import json

class TCamProxy(object):
    def __init__(self, server):
        self.server = server

    def TCamManager(self):
        tcam = TCamManagerProxy(self.server)
        return tcam

class TCamManagerProxy(object):
    def __init__(self, server):
        self._server = server
    
    def Open(self, request):
        """
        Open camera and configure all parameters in request.
        Request type is dict here, and will be dumped into json and sent to server.
        """ 
        request_json = json.dumps(request)
        self._server.open(request_json)

    def Close(self):
        """
        Close camera.
        """
        self._server.close()
    
    def Set_Trigger_Mode(self, mode = 2):
        """
        Set Trigger Mode.
        0 : OFF,
        1 : HW Trigger, falling edge,
        2 : HW Trigger, rising edge (default).
        """
        self._server.set_trigger_mode(mode)
        
    def Get_Image(self):
        """
        Get the latest image in buffer, return in list.
        """
        im_json = self._server.get_image()
        im = json.loads(im_json)
        return im
    
    def Start_Single_Capture(self):
        """
        Start single shot capture, will wait until receiving trigger event,
        and the image will be saved to memory.
        So the correct order should be:
        1. Set_Trigger_Mode(2)
        2. Start_Single_Capture()
        3. (wait until receiving trigger event)
        4. Get_Image()
        5. Repeat 1-4 to acquire another image
        """
        self._server.start_single_capture()
    