import numpy as np

name = 'Lattice_modulation_pump16W_148mW'

loop = True
loop = False 

reload_parameters = {
    # 'blue_pmt.recorder': {},
    # 'photodiode.recorder': {},
    'thorlabs_ccd.record_path':{},
    }

# Use Ch2 of beatnote_689 Rigol signal generator.
# 0 to -300 mV Sin wave, set output to ON

scan_Modulation = 1e3 + np.arange(0, 120e3, 2e3)

parameter_values = {
    
    'lattice.ModulationFrequency': scan_Modulation,  
    
    'sequencer':  {
        'sequence':[
                   'blue_mot', 
                    'red_mot_88', 
                    
                    # 'lattice_hold_5.0ms',
                    'lattice_hold_100.0ms',
                    # 'lattice_hold_500.0ms',
                    # 'lattice_hold_1.0s',
                    
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