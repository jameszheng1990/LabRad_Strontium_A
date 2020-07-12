from conductor.experiment import Experiment
import labrad, time

# TOF_list = [5.0]  # ONE point TOF, for optimizing the temperature

# To iterate tof list, loop has to be False. Should NEVER loop!!!
loop = False

name = 'red_mot_tof'

reload_parameters = {
    'thorlabs_ccd.record_path':{},
    }

tof_list = [3e-3, 5e-3, 7e-3, 9e-3, 11e-3]

tof_list = 5e-3  # one point TOF optimization
loop = True

parameter_values = {
    'sequencer.sequence':
            [
            'blue_mot',
            # 'red_mot_88',
            'red_mot_87',
            'PROG_red_mot_tof',   # has to start with 'PROG_', which represents programmable... 
            'image_absorption_red',
            ],
        
    'sequencer.DO_parameters':
            {
            'red_mot_tof': tof_list,
            },
            
        # 'sequencer.AO_parameters':
        #     {
        #     'Lattice 813A AM': 0,
        #     },
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