from conductor.experiment import Experiment
import labrad, time


tof_list = [5e-3, 10e-3] # For Red MOT it has to be at least 5 ms, because of probe shutter delay..

# TOF_list = [5.0]  # ONE point TOF, for optimizing the temperature

loop = False

reload_parameters = {
    # 'thorlabs_ccd.record_path':{},
    }
for i in tof_list:
    name = 'red_mot_tof_{}ms'.format(i*1e3)
    parameter_values = {
        
        'sequencer.sequence':
            [
            'blue_mot',
            'red_mot_88',
            'PROG_red_mot_tof',   # has to start with 'PROG_', which represents programmable... 
            'image_absorption_red',
            ],
        
        # only accepts one column for below subsequence.
        'sequencer.DO_parameters':
            {
            'red_mot_tof': i,
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