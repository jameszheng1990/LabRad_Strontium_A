from PyQt5 import QtCore, QtWidgets
from twisted.internet.defer import inlineCallbacks
import matplotlib, time
matplotlib.use('QT5Agg')

from twisted.internet.defer import inlineCallbacks

import json, os, sys

def populate_tabs(tabs, grouped_tabs, reactor):
    j = 0
    for info in grouped_tabs:
        tab = QtWidgets.QWidget()
        tabs.addTab(tab, list(info.keys())[0])
        layout = info[list(info.keys())[0]].get('layout')
        tab.layout = layout
        positions = info[list(info.keys())[0]].get('positions')
        clients = info[list(info.keys())[0]].get('clients')
        if positions:
            for position, client in zip(positions, clients):
                tab.layout.addWidget(client(reactor), *position)
        else:
            for client in clients:
                tab.layout.addWidget(client(reactor))
        sizes = info[list(info.keys())[0]].get('sizes')
        if sizes:
            tab.setFixedSize(sizes[0], sizes[1])
        tab.setLayout(tab.layout)
        j += 1

class Window(QtWidgets.QWidget):
    name = None
    
    def __init__(self, grouped_tabs, reactor, name):
        QtWidgets.QDialog.__init__(self)
        self.grouped_tabs = grouped_tabs
        self.title = name
        self.reactor = reactor
        self.populateGUI()
        self.setWindowTitle(self.title)
    
    def populateGUI(self):
        self.layout = QtWidgets.QHBoxLayout()
        self.tabs = QtWidgets.QTabWidget()
        
        populate_tabs(self.tabs, self.grouped_tabs, self.reactor)
        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)    
    
    def closeEvent(self, x):
        super(Window, self).closeEvent(x)
        try:
            self.reactor.stop()
        except:
            pass
        # self.reactor.callFromThread(self.reactor.stop)

class Container(QtWidgets.QWidget):
    def __init__(self, grouped_tabs_A, grouped_tabs_B, grouped_tabs_C, reactor):
        QtWidgets.QDialog.__init__(self)
        self.grouped_tabs_A = grouped_tabs_A
        self.grouped_tabs_B = grouped_tabs_B
        self.grouped_tabs_C = grouped_tabs_C
        self.reactor = reactor
        self.initialize()
    
    def initialize(self):
        self.populateGUI()
    
    def populateGUI(self):
        self.windowA = Window(self.grouped_tabs_A, self.reactor, 'Interface A')
        self.windowB = Window(self.grouped_tabs_B, self.reactor, 'Interface B')
        self.windowC = Window(self.grouped_tabs_C, self.reactor, 'Interface C')
        self.windowA.show()
        self.windowB.show()    
        self.windowC.show()    

if __name__ == '__main__':
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    from client_tools import qt5reactor
    qt5reactor.install()
    from twisted.internet import reactor

################ TAB 0, blue slaves, repumps, and Wavemeter ###################
    
    from current_controller.clients.default import CurrentControllerClient
    from current_controller.devices.blue_slave_1 import BlueSlave1Proxy
    from current_controller.devices.blue_slave_2 import BlueSlave2Proxy
    from current_controller.devices.blue_slave_3 import BlueSlave3Proxy

    class BlueSlave1Client(CurrentControllerClient):
        name = 'Blue Slave 1'
        DeviceProxy = BlueSlave1Proxy
        scani = 129
        scanf = 125
    
    class BlueSlave2Client(CurrentControllerClient):
        name = 'Blue Slave 2'
        DeviceProxy = BlueSlave2Proxy
        scani = 128
        scanf = 124

    class BlueSlave3Client(CurrentControllerClient):
        name = 'Blue Slave 3'
        DeviceProxy = BlueSlave3Proxy
        scani = 132
        scanf = 128
    
######################### TAB 1, RF and AFGs ##################################
    
    from rf2.clients.repump_client import Repump_RFClient
    from rf2.devices.rigol_repumps import RepumpSGProxy

    from rf2.clients.dim3000_client import DIM3000_RFClient
    # from rf2.devices.dim3000_reda import DIM3000REDAProxy
    # from rf2.devices.dim3000_redb import DIM3000REDBProxy
    from rf2.devices.dim3000_blue2 import DIM3000BLUE2Proxy

    from afg2.clients.default import AFGControllerClient
    from afg2.devices.Red_AFG import RedAFGProxy
    
    from rf2.clients.beatnote_client import RedMOTRFClient
    from rf2.devices.rigol_beatnote import BEATNOTESGProxy
    
    from rf2.clients.fiberEOM_client import FiberEOM_RFClient
    from rf2.devices.rigol_fiberEOM import FiberEOMSGProxy
    
    from rf2.clients.moglabsARF_client import MoglabsARF_RFClient
    from rf2.devices.moglabs_ARF import MoglabsARFProxy
    
        
    class RepumpSGClient(Repump_RFClient):
        name = 'Repump SG'
        DeviceProxy = RepumpSGProxy
        
        frequencyDigits = 1
        voltageDigits = 2
        
    # class DIM3000REDAClient(DIM3000_RFClient):
    #     name = 'AOM_689A' # to be changed
    #     DeviceProxy = DIM3000REDAProxy
        
    #     frequencyDigits = 3
    #     amplitudeDigits = 2
    #     fmfreqDigits = 1

    # class DIM3000REDBClient(DIM3000_RFClient):
    #     name = 'AOM_689B' # to be changed
    #     DeviceProxy = DIM3000REDBProxy
        
    #     frequencyDigits = 3
    #     amplitudeDigits = 2
    #     fmfreqDigits = 1
        
    class DIM3000BLUE2Client(DIM3000_RFClient):
        name = 'AOM_blue2'
        DeviceProxy = DIM3000BLUE2Proxy
        
        frequencyDigits = 3
        amplitudeDigits = 2
        fmfreqDigits = 1

    class AFGSubClient(AFGControllerClient):
        name = 'Red AFG'
        DeviceProxy = RedAFGProxy

        scaleDigits = 1
        offsetDigits = 3
    
    class BeatnoteSGClient(RedMOTRFClient):
        name = 'Red-B beatnote'
        DeviceProxy = BEATNOTESGProxy
        
        frequencyDigits = 6
        amplitudeDigits = 2

    class FiberEOMRFClient(FiberEOM_RFClient):
        name = 'fiber EOM'
        DeviceProxy = FiberEOMSGProxy
        
        frequencyDigits = 6
        amplitudeDigits = 2
        
    class MoglabsARFClient(MoglabsARF_RFClient):
        name = 'Moglabs_ARF'
        DeviceProxy = MoglabsARFProxy
        
        frequencyDigits = 6
        amplitudeDigits = 2
        fmgainDigits = 2
        amgainDigits = 2
    
############################# TAB 2, sequencer ################################
        
    from sequencer.clients.default import SequencerClient

######################### TAB 3, M2 wlm ###############################

    from msquared_wlm_lock.clients.default import WLMLockControllerClient
    
    class WLMLockClient(WLMLockControllerClient):
        name = 'WLM lock'
        wlm_servername = 'hf_wavemeter'
        msquared_servername = 'msquared'
        wlm_lock_servername = 'msquared_wlm_lock'
        msquared_devicename = 'M2Sprout'
    
######################### TAB 4, common actions ###############################

    from conductor.clients.common_action import RunBlueMOT
    from conductor.clients.common_action import StopExperiment
    from conductor.clients.common_action import PauseToggle
            
############################ TAB 4, camera ####################################
    
    from camera.clients.default import CameraClient

    class TOF_tcam_Client(CameraClient):
        name = 'tcam' # must be the same name of device_name (in /camera/device)

##################### TAB 5, PMT ##########################
    
    from pmt.clients.pmt_client import PMTViewer
    from pd.clients.pd_client import PDViewer

    class PMT(PMTViewer):
        pmt_name = 'blue_pmt'
        data_dir = os.path.join(os.getenv('LABRADDATA'),'data')
        
    class PD(PDViewer):
        pd_name = 'ThorlabsPD'
        data_dir = os.path.join(os.getenv('LABRADDATA'),'data')
        
##################### TAB 6, Plotter ##########################
    
    from plotter.clients.plotter_client import PlotterViewer

    class Plotter(PlotterViewer):
        plotter_name = 'plotter'
        
###############################################################################    
    
    grouped_tabs_A = [
            {'461 nm Lasers':            {'clients': [BlueSlave1Client, 
                                                      BlueSlave2Client, 
                                                      BlueSlave3Client],
                                          'layout':   QtWidgets.QHBoxLayout(),
                                          'sizes':   (400*3, 600)}},
            
            {'RFs':                      {'clients': [RepumpSGClient,
                                                      DIM3000BLUE2Client,
                                                      # DIM3000REDAClient, # to be done
                                                      # DIM3000REDBClient, # to be done
                                                      AFGSubClient,
                                                      BeatnoteSGClient,
                                                      FiberEOMRFClient,
                                                      MoglabsARFClient],
                                          'layout':   QtWidgets.QGridLayout(),
                                          'sizes':   (240*5, 320*2),
                                          'positions': [(i, j) for i in range(2)
                                                              for j in range(5)]}},
            
            {'Sequencer':                {'clients': [SequencerClient],
                                          'layout':   QtWidgets.QGridLayout()}},
            
            {'Msquared Wavemeter Lock':  {'clients': [WLMLockClient],
                                          'layout':   QtWidgets.QGridLayout()}},
            
            {'Conductor Controls':       {'clients': [RunBlueMOT,
                                                      StopExperiment,
                                                      PauseToggle],
                                          'layout':   QtWidgets.QGridLayout()}}
        ]

    grouped_tabs_B = [
            {'Plotter':                  {'clients': [Plotter],
                                          'layout':   QtWidgets.QGridLayout()}},
        ]    
    
    grouped_tabs_C = [
            {'Camera':                   {'clients': [TOF_tcam_Client],
                                          'layout':   QtWidgets.QGridLayout()}},
            
            {'PD/PMT':                   {'clients': [
                                                    # PD, # only one at a time..
                                                      PMT],
                                          'layout':   QtWidgets.QGridLayout()}},
        ] 
        
    widget = Container(grouped_tabs_A,  grouped_tabs_B, grouped_tabs_C, reactor)
    # widget.show()
    reactor.suggestThreadPoolSize(50)
    reactor.run()