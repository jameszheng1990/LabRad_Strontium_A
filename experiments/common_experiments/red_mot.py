# name experiment
name = 'red_mot'

# specify looping of parameter values
loop = True
loop = False 

# specify which parameters we should reload at the begining of the experiment
reload_parameters = {
    # 'blue_pmt.recorder': {},
    # 'photodiode.recorder': {},
    'thorlabs_ccd.record_path':{},
    }

# create lists of parameter values to be scanned through
parameter_values = {
    # 'blue_isotope.frequency': [250e6, 255e6, 260e6],
    
    'sequencer':  {
        'sequence':[
                    'blue_mot', 
                    # 'blue_mot_long', 
                    # 'red_mot_88',
                    # 'red_mot_88_short',
                    # 'red_mot_87', 
                    # 'TOF_red_5.0',
                    
                    'red_mot_88_test',
                    # 'red_mot_87_test',
                    
                    # 'TOF_red_13.0',
                    'image_absorption_red',
                    # 'image_fluorescence_red',
                    ],
        },

    # This will be useful to vary the pulse duration, like TOF/Rabi/Ramsey measurement, good thing is we don't need to create the exact
    # subsequence for each experiment...
    # Still will need a for loop to scan over different pulse durations. 
    # Has to be the same name as in above subsequence, and will ONLY change the first duration in that subsequence.
    # DO NOT accept list
    # 'sequencer.DO_parameters':
    #     {
    #     'red_TOF': 0.1,
    #     },
            
       
    # This will set AO output to constant value during experiment
    # DO NOT accept list
    # 'sequencer.AO_parameters': {
    #         'Lattice 813A AM' : 0.5,
    #          },
    
    # 'plotter.plot' :{
    #         'plotter_path': 'C:\\LabRad\\SrData\\notebook\\data_tools\\process_camera.py',
    #         'plotter_function': 'load_images',
    #     }
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