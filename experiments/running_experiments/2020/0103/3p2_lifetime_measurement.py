# name experiment
# this string will be reformatted by the conductor prepending a (%Y%m%d) 
# datestring and appending an experiment iteratoin number
# e.g. running an experiment with name, 'example-experiment', for the first 
# time on 20181101 will give a reformatted experiment name: 
# 20181101/example-experiment#0
holdtime = '01'
name = '3p2_lifetime_lighton_420C_'+ holdtime +'s'

# specify looping of parameter values
# set this to true if we would like to infinitely loop parameter values 
# when looping, for each shot, the current value of each parameter is 
# added to the end of the value_queue.
loop = False # If in "loop" mode, one experiment will have infinite shots until you call "Trigger Off" to stop.
            # You are allowed to queue multiple experiments in "Loop = False" mode.
            # But you are NOT allowed to queue more than one experiment in "LOOP = True" mode.

# specify which parameters we should reload at the begining of the experiment
# this is useful for reconfiguring the parameter objects for different experiments
# All reload parameters will be terminated after experiment finished.
reload_parameters = {
    # 'blue_pmt.recorder': {}
    'photodiode.recorder': {}
    }

# create lists of parameter values to be scanned through
test_scan_values = range(10)  # In principle, we will only scan one parameter at a time..

# assign parameter values
# both values to be scanned through and fixed values are specified here
parameter_values = {
    # 'test_parameter': test_scan_values,
    'sequencer.sequence':[
        'blue_mot_long', 
        '3p2_mtrap_load',
        '3p2_hold_'+holdtime+'s',
        '3p2_probe',
        # 'test1',
        # 'pd-v',
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
cxn.conductor.ao_off() # Useful for sequences that only involve the DIO card, for example, the steady-state blue MOT and loading-rate.
cxn.conductor.trigger_on()