name = 'TEST_blue_mot_imaging_TOF_0.1ms'

loop = True
# loop = False 

# specify which parameters we should reload at the begining of the experiment
# this is useful for reconfiguring the parameter objects for different 
# experiments
reload_parameters = {
    # 'blue_pmt.recorder': {},
    # 'photodiode.recorder': {},
    'thorlabs_ccd.record_path': {},
    }

# create lists of parameter values to be scanned through
test_scan_values = range(10)  # In principle, we will only scan one parameter at a time..

# assign parameter values
# both values to be scanned through and fixed values are specified here
parameter_values = {
    # 'test_parameter': test_scan_values,
    'sequencer.sequence':[
        'blue_mot',
        # 'blue_mot_long', 
        'TOF_0.1ms',
        'image_absorption_blue',
        # 'image_fluorescence_blue',
        ]
    }

if __name__ == '__main__':
    from conductor.experiment import Experiment
    my_experiment = Experiment(
        name=name,
        parameters=reload_parameters,  # passed to reload_parameters
        parameter_values=parameter_values,
        loop=loop,
        )
    my_experiment.queue(run_immediately=True)

import labrad, time
cxn=labrad.connect()
# cxn.conductor.ao_off()  # Will remove AO from sequencer.
cxn.conductor.trigger_on()