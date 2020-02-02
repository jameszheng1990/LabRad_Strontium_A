from afg.devices.afg31052.device import AFG31052

class B_FM(AFG31052):
    visa_address = 'USB0::0x0699::0x0358::C011390::INSTR'
    source = 2
    
    autostart = True
    
    waveforms = [
        # 'U:/RedMOT_88_A.tfw',
        ]

Device = B_FM
