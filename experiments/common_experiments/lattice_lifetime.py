from conductor.experiment import Experiment
import labrad, time

holdtime_list = [ 5.0, 10.0, 20.0, 30.0, 40.0] # units in second

holdtime_list = [1.0, 3.0]  # units in second

# loop = True
loop = False

reload_parameters = {
    # 'thorlabs_ccd.record_path':{},
    }

for i in holdtime_list:
    name = 'lattice_lifetime_measurement_hold_{}s'.format(i)
    
    parameter_values = {
        
        'sequencer.sequence':
            [
            'blue_mot',
            'red_mot_88',
    
            'PROG_lattice_hold',
            'image_absorption_red',
            ],
            
        # DO NOT accept list
        'sequencer.DO_parameters':
            {
            'lattice_hold' :i
            }
            
        }

    if __name__ == '__main__':
        
        my_experiment = Experiment(
            name=name,
            parameters=reload_parameters,  # passed to reload_parameters
            parameter_values=parameter_values,
            loop=loop,
            )
        my_experiment.queue(run_immediately=False)

cxn=labrad.connect()
cxn.conductor.trigger_on()