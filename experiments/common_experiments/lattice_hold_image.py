import numpy as np
import os

holdtime = 0.3 # in second
exp_name = 'lattice_hold_image'
name = exp_name + '-holdtime{}s'.format(holdtime)
method = 'tcam'

loop = True
# loop = False

##########################################################################
# Don't need to regularly change below
DATA_DIR = os.path.join(os.getenv('LABRADDATA'), 'data')

if method == 'tcam':
    RELOAD_PARAMETERS = {
    'thorlabs_ccd.record_path':{},
    }
    SEQUENCE = [
            'blue_mot', 
            'red_mot_88', 
            # 'red_mot_87',    
            'in_lattice_cooling_88',
            'PROG_lattice_hold',
            'image_absorption_lattice',
            # 'image_fluorescence_lattice',
            ]
    y_key = 'tcam_count'
else:
    pass

loop = loop 
reload_parameters = RELOAD_PARAMETERS
parameter_values = {
    'sequencer':  
        {'sequence':
            SEQUENCE,
        },
    
    'sequencer.DO_parameters':
            {
            'lattice_hold': holdtime,
            },
    
    'red_mot.frequency_modulation':{
        'in_lattice_cooling_88': {'B': {'wfm': 'U:/in_lattice_cooling/ILC88B_25mV.tfw'}},
        },
    
    # plotter has to be in dict format.
    'plotter':{
        'plot':
        {
        'plotter_path': DATA_DIR + '\\notebooks\\data_tools\\{}-analyzer.py'.format(exp_name),
        'plotter_function': 'plot_{}_{}'.format(exp_name, method),
        'processer_function': 'process_{}_{}'.format(exp_name, method),
        'args': {'plot_in_GUI': True},
        'kwargs': {'exp_name': exp_name, 'units': 'shot',
                   'x_key' : 'shot',  'y_key' : y_key,
                   'x_label' : 'Iteration number',  'y_label' : 'Atom number (arb. units)',
                   'roi_width': 20, 'fit_width': 10, 'data_range':(0, 1e7) },
        }
        }
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
