# name experiment
name = 'TEST_red_mot'

# specify looping of parameter values
loop = True
# loop = False 

# specify which parameters we should reload at the begining of the experiment
reload_parameters = {
    'thorlabs_ccd.record_path':{},
    # 'thorlabs_ccd.record_path':{'method': 'fluorescence'},
    }

# create lists of parameter values to be scanned through
parameter_values = {
    # 'blue_isotope.frequency': [250e6, 255e6, 260e6],
    
    'sequencer':  {
        'sequence':[
                    'blue_mot', 
                    # 'blue_mot_long', 
                    
                    'red_mot_88',
                    # 'red_mot_88_fast',
                    # 'red_mot_87', 
                    # 'red_mot_87_fast', 
                    # 'red_mot_87_swap',
                    
                    'image_absorption_red',
                    ],
        },

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