import numpy as np
import os

exp_name = 'lattice_trap_freq_modulation'
# Use Ch2 of beatnote_689 Rigol signal generator.
# 0 to -300 mV Sin wave, set output to ON

# power_units = {'W': 1, 'mW': 1e-3}

scan_ModulationFreq_list = np.arange(1e3, 100e3, 0.5e3)
# pump_power = {13  : 'W'}
# retro_power= {114 : 'mW'}
pump_power = 9.6
retro_power = 300
holdtime = 0.1
name = exp_name + '-Sr88-pump{}W_retro{}mW-holdtime{}s'.format(pump_power, retro_power, holdtime)
method = 'tcam'
# method = 'ixon'
# method = 'pmt'

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
            ]
    y_key = 'tcam_count'
else:
    pass

loop = False 
reload_parameters = RELOAD_PARAMETERS
parameter_values = {
    'lattice.ModulationFrequency': scan_ModulationFreq_list,  
    'sequencer':  
        {'sequence':
            SEQUENCE,
        },
    
    # don't use list here, only scan one parameter at a time..
    'sequencer.DO_parameters':
        {
        'lattice_hold': holdtime,
        },
    
    'red_mot.frequency_modulation':
        {
        'in_lattice_cooling_88': {'B': {'wfm': 'U:/in_lattice_cooling/ILC88B_25mV.tfw'}},
        },
    
    # has to be in dict format.
    'plotter':{
        'plot':
        {
        'plotter_path': DATA_DIR + '\\notebooks\\data_tools\\{}-analyzer.py'.format(exp_name),
        'plotter_function': 'plot_{}_{}'.format(exp_name, method),
        'processer_function': 'process_{}_{}'.format(exp_name, method),
        'args': {'plot_in_GUI': True},
        'kwargs': {'exp_name': exp_name, 'units': 'kHz',
                   'x_key' : 'modulation_frequency',  'y_key' : y_key,
                   'x_label' : 'Modulation_frequency',  'y_label' : 'Atom number (arb. units)',
                   'roi_width': 20, 'fit_width': 10, 'data_range':(0, 3e5) },
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
# cxn.conductor.ao_off()  # Will remove AO from sequencer.
cxn.conductor.trigger_on()