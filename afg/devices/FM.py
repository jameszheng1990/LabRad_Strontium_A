from afg.devices.afg31052.device import AFG31052

class FM(AFG31052):
    vxi11_address = '192.168.1.23'
    
    autostart = True
    
    waveforms = [
        'U:/RedMOT_87_A.tfw',
        
        'U:/RedMOT_87_B.tfw',
        'U:/RedMOT_88_B.tfw',
        ]

Device = FM
