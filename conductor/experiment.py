import json, os
import labrad

def json_defaults(obj):
    if type(obj).__name__ == 'ndarray':
        return obj.tolist()

class Experiment(object):
    def __init__(self, **kw):
        self.name = kw.get('name', 'default')
        self.parameters = kw.get('parameters', {})  # Reload parameters
        self.parameter_values = kw.get('parameter_values', {})
        self.loop = kw.get('loop', False)

    def queue(self, run_immediately=False):
        cxn = labrad.connect(name=self.name, host=os.getenv('LABRADHOST'), password='')
        request = {
            'name': self.name,
            'parameters': self.parameters,
            'parameter_values': self.parameter_values,
            'loop': self.loop,
            }
        request_json = json.dumps(request, default=json_defaults)
        if run_immediately:
            cxn.conductor.queue_experiment(request_json, True)
            # cxn.conductor.stop_experiment()
        else:
            cxn.conductor.queue_experiment(request_json)


