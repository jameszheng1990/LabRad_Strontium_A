import json
import traceback

from conductor.parameter import ConductorParameter

class Plot(ConductorParameter):
    autostart = False
    priority = 1
    call_in_thread = True
    value_type = 'dict'
    value = None
    
    plotter_servername = 'plotter'

    def initialize(self,config):
        self.connect_to_labrad()
    
    def update(self):
        """ 
        This parameter plots after each shot, so we need to know previous experiment.
        For the first shot, the previous_experiment should be {}.
        """
        is_end = self.server.is_end 
        
        previous_experiment_name = self.server.previous_experiment.get('name')
        previous_shot_number = self.server.previous_experiment.get('shot_number')
        
        self.value['data_path'] = previous_experiment_name
        self.value['shot'] = previous_shot_number
            
        if self.value and not (is_end) and (previous_experiment_name is not None):
            self.value['to_plot'] = False
            self.cxn.plotter.plot(json.dumps(self.value))
        
        elif self.value and is_end:
            self.value['to_plot'] = True
            self.cxn.plotter.plot(json.dumps(self.value))
            self.value = None

Parameter = Plot
