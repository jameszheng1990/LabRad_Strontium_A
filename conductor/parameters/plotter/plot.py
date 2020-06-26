import json
import traceback

from conductor.parameter import ConductorParameter

class Plot(ConductorParameter):
    autostart = False
    priority = 1
    call_in_thread = True
    value_type = 'dict'
    value = None
    shot = None
    
    plotter_servername = 'plotter'

    def initialize(self,config):
        self.connect_to_labrad()
    
    def update(self):
        is_first = self.server.is_first
        is_end = self.server.is_end 
        experiment_name = self.server.experiment.get('name')
        shot_number = self.server.experiment.get('shot_number')

        if self.value and is_first and (experiment_name is not None) and (shot_number is not None):
            self.shot = shot_number - 1
            self.value['data_path'] = experiment_name
            self.value['shot'] = self.shot
            self.value['to_plot'] = False
        
        elif self.value and (not is_end):
            self.shot = shot_number - 1
            self.value['shot'] = self.shot
            self.cxn.plotter.plot(json.dumps(self.value))
        
        elif self.value and is_end:
            self.shot += 1
            self.value['shot'] = self.shot
            self.value['to_plot'] = True
            self.cxn.plotter.plot(json.dumps(self.value))
            self.value = None
            self.shot = None

Parameter = Plot
