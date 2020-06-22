import numpy as np

name = 'red_mot'

loop = True
loop = False 

reload_parameters = {
    # 'blue_pmt.recorder': {},
    # 'photodiode.recorder': {},
    'thorlabs_ccd.record_path':{},
    }

scan_A = 79.707e6 + np.arange(-5e3, 5e3, 1e3)
scan_B = 79.996e6 + np.arange(-500e3, 500e3, 50e3)
scan_beatnote = 19.354300e6 + np.arange(-2e3, 2e3, 1e3)

parameter_values = {
    
    # 'red_mot.A_frequency': scan_A,
    # 'red_mot.B_frequency': scan_B,
    # 'red_mot.beatnote': scan_beatnote,
    
    'sequencer':  {
        'sequence':[
                    'blue_mot', 
                    # 'blue_mot_long', 
                    # 'red_mot_88',
                    'red_mot_88_short',
                    # 'red_mot_87', 
                    'image_absorption_red',
                    ],
        
        # '*A' : 1   # To be implemented later, to scan parameter in sequencer..
                     # It seems a bit unnecessary to do so, since we have to write & run sequencer anyway...
        }
    
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