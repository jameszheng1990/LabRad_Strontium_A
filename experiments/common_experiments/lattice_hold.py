# name experiment

holdtime = 50e-3

name = 'lattice_hold_{}ms'.format(holdtime*1e3)

# specify looping of parameter values
loop = True
loop = False 

# specify which parameters we should reload at the begining of the experiment
reload_parameters = {
    # 'blue_pmt.recorder': {},
    # 'photodiode.recorder': {},
    'thorlabs_ccd.record_path':{},
    }

parameter_values = {

    'sequencer.sequence':  
                    [
                    'blue_mot', 
                    'red_mot_88',
                    # 'red_mot_87',
                    
                    'PROG_lattice_hold',
                    'image_absorption_red',
                    ],
    
    # DO NOT accept list
    'sequencer.DO_parameters':
            {
            'lattice_hold': holdtime,
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

cxn.conductor.trigger_on()