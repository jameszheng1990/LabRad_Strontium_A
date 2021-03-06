from conductor.experiment import Experiment
import labrad, time, os

exp_name = 'lattice_lifetime'

holdtime_list = [5.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0] # units in second
# holdtime_list = [50]

# pump_power = {13  : 'W'}
# retro_power= {114 : 'mW'}
pump_power = 9
retro_power = 350
name = exp_name + '-pump{}W_retro{}mW'.format(pump_power, retro_power)
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
            'PROG_lattice_hold',                
            'image_absorption_red',
            ]
    y_key = 'tcam_count'
else:
    pass

loop = False 
reload_parameters = RELOAD_PARAMETERS
parameter_values = {
    'sequencer':  
        {'sequence':
            SEQUENCE,
        },
    
    # don't use list here, only scan one parameter at a time..
    'sequencer.DO_parameters':
        {
        'lattice_hold': holdtime_list,
        },
    
    # has to be in dict format.
    'plotter':{
        'plot':
        {
        'plotter_path': DATA_DIR + '\\notebooks\\data_tools\\{}-analyzer.py'.format(exp_name),
        'plotter_function': 'plot_{}_{}'.format(exp_name, method),
        'processer_function': 'process_{}_{}'.format(exp_name, method),
        'args': {'plot_in_GUI': True},
        'kwargs': {'exp_name': exp_name, 'units': 's',
                   'x_key' : 'lattice_hold',  'y_key' : y_key,
                   'x_label' : 'lattice hold time',  'y_label' : 'Atom number (arb. units)',
                   'roi_width': 16, 'fit_width': 7, 'data_range':(0, 1e6) },
        }
        }
    }

if __name__ == '__main__':
    my_experiment = Experiment(
        name=name,
        parameters=reload_parameters,  # passed to reload_parameters
        parameter_values=parameter_values,
        loop=loop,
        )
    my_experiment.queue(run_immediately=True)

cxn=labrad.connect()
cxn.conductor.trigger_on()