from PyQt5 import QtCore, QtWidgets
from twisted.internet.defer import inlineCallbacks
import matplotlib, time
matplotlib.use('QT5Agg')

from twisted.internet.defer import inlineCallbacks

import json, os, sys

class WindowA(QtWidgets.QWidget):
    name = None
    
    def __init__(self, tab_list, reactor):
        QtWidgets.QDialog.__init__(self)
        self.tab_list = tab_list
        self.title = 'Strontium Experiment Control Interface A'
        self.reactor = reactor
        self.populateGUI()
        self.setWindowTitle(self.title)
 
    def populateGUI(self):
        self.layout = QtWidgets.QHBoxLayout()
        self.tabs = QtWidgets.QTabWidget()
        
        if self.tab_list[0]:
            self.tab0 = QtWidgets.QWidget()
            self.tabs.addTab(self.tab0, "Blue Lasers")
            self.tab0.layout = QtWidgets.QHBoxLayout()
            for client in self.tab_list[0]:
                self.tab0.layout.addWidget(client)
            self.tab0.setFixedSize(400* len(self.tab_list[0]), 600)
            self.tab0.setLayout(self.tab0.layout)
        
        if self.tab_list[1]:
            positions = [(i,j) for i in range(2) for j in range(5)]
            names = self.tab_list[1]
            self.tab1 = QtWidgets.QWidget()
            self.tabs.addTab(self.tab1, "RF && AFG")
            self.tab1.layout = QtWidgets.QGridLayout()
            for position, name in zip(positions, names):
                self.tab1.layout.addWidget(name, *position)
            self.tab1.setFixedSize(240*5, 320 * 2)
            self.tab1.setLayout(self.tab1.layout)
        
        if self.tab_list[2]:
            self.tab2 = QtWidgets.QWidget()
            self.tabs.addTab(self.tab2, "Sequencer")
            self.tab2.layout = QtWidgets.QGridLayout()
            for client in self.tab_list[2]:
                self.tab2.layout.addWidget(client)
                self.tab2.setLayout(self.tab2.layout)
        
        if self.tab_list[3]:
            self.tab3 = QtWidgets.QWidget()
            self.tabs.addTab(self.tab3, "Common Actions")
            self.tab3.layout = QtWidgets.QGridLayout()
            for client in self.tab_list[3]:
                self.tab3.layout.addWidget(client)
            self.tab3.setLayout(self.tab3.layout)
                
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
    def closeEvent(self, x):
        super(WindowA, self).closeEvent(x)
        # self.reactor.stop()
        self.reactor.callFromThread(self.reactor.stop)

class WindowB(QtWidgets.QWidget):
    name = None
    
    def __init__(self, tab_list, reactor):
        QtWidgets.QDialog.__init__(self)
        self.tab_list = tab_list
        self.title = 'Strontium Experiment Control Interface B'
        self.reactor = reactor
        self.populateGUI()
        self.setWindowTitle(self.title)
    
    def populateGUI(self):
        self.layout = QtWidgets.QHBoxLayout()
        self.tabs = QtWidgets.QTabWidget()
        
        if self.tab_list[0]:
            self.tab0 = QtWidgets.QWidget()
            self.tabs.addTab(self.tab0, "Camera")
            self.tab0.layout = QtWidgets.QGridLayout()
            for client in self.tab_list[0]:
                self.tab0.layout.addWidget(client)
                self.tab0.setLayout(self.tab0.layout)
        
        if self.tab_list[1]:
            self.tab1 = QtWidgets.QWidget()
            self.tabs.addTab(self.tab1, "PD/PMT")
            self.tab1.layout = QtWidgets.QGridLayout()
            for client in self.tab_list[1]:
                self.tab1.layout.addWidget(client)
                self.tab1.setLayout(self.tab1.layout)
                
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)    
    
    def closeEvent(self, x):
        super(WindowB, self).closeEvent(x)
        # self.reactor.stop()
        self.reactor.callFromThread(self.reactor.stop)

class Container(QtWidgets.QWidget):
    name = None
    
    def __init__(self, tab_list_A, tab_list_B, reactor):
        QtWidgets.QDialog.__init__(self)
        self.tab_list_A = tab_list_A
        self.tab_list_B = tab_list_B
        self.reactor = reactor
        self.initialize()
    
    def initialize(self):
        self.populateGUI()
    
    def populateGUI(self):
        self.windowA = WindowA(tab_list_A, reactor)
        self.windowB = WindowB(tab_list_B, reactor)
        self.windowA.show()
        self.windowB.show()    

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
    from rf2.devices.dim3000_reda import DIM3000REDAProxy
    from rf2.devices.dim3000_redb import DIM3000REDBProxy
    from rf2.devices.dim3000_blue2 import DIM3000BLUE2Proxy

    from afg2.clients.default import AFGControllerClient
    from afg2.devices.Red_AFG import RedAFGProxy
    
    from rf2.clients.beatnote_client import RedMOTRFClient
    from rf2.devices.rigol_beatnote import BEATNOTESGProxy
    
    from rf2.clients.fiberEOM_client import FiberEOM_RFClient
    from rf2.devices.rigol_fiberEOM import FiberEOMSGProxy
        
    class RepumpSGClient(Repump_RFClient):
        name = 'Repump SG'
        DeviceProxy = RepumpSGProxy
        
        frequencyDigits = 1
        voltageDigits = 2
        
    class DIM3000REDAClient(DIM3000_RFClient):
        name = 'AOM_689A'
        DeviceProxy = DIM3000REDAProxy
        
        frequencyDigits = 3
        amplitudeDigits = 2
        fmfreqDigits = 1

    class DIM3000REDBClient(DIM3000_RFClient):
        name = 'AOM_689B'
        DeviceProxy = DIM3000REDBProxy
        
        frequencyDigits = 3
        amplitudeDigits = 2
        fmfreqDigits = 1
        
    class DIM3000BLUE2Client(DIM3000_RFClient):
        name = 'AOM_blue2'
        DeviceProxy = DIM3000BLUE2Proxy
        
        frequencyDigits = 3
        amplitudeDigits = 2
        fmfreqDigits = 1

    class AFGSubClient(AFGControllerClient):
        name = 'RED AFG'
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
    
############################# TAB 2, sequencer ################################
        
    from sequencer.clients.default import SequencerClient

######################### TAB 3, common actions ###############################

    from conductor.clients.common_action import RunBlueMOT
    from conductor.clients.common_action import StopExperiment
    from conductor.clients.terminator import Terminator
            
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
        
###############################################################################    
    
    tabA0 = [
            BlueSlave1Client(reactor),
            BlueSlave2Client(reactor),
            BlueSlave3Client(reactor),
            ]
    
    tabA1 = [
            RepumpSGClient(reactor),
            DIM3000BLUE2Client(reactor),
            DIM3000REDAClient(reactor),
            DIM3000REDBClient(reactor),
            AFGSubClient(reactor),
            BeatnoteSGClient(reactor),
            FiberEOMRFClient(reactor),
            ]
    
    tabA2 = [
            SequencerClient(reactor),
            ]
    
    tabA3 = [
            RunBlueMOT(reactor),
            StopExperiment(reactor),
            Terminator(reactor),
            ]
    
    tabB0 = [
            # ONLY ONE AT A TIME!
            TOF_tcam_Client(reactor), 
            ]
    
    tabB1 = [
            # ONLY ONE AT A TIME!
            PMT(reactor),
            # PD(reactor)
            ]
    
    tab_list_A = [
                tabA0,
                tabA1,
                tabA2,
                tabA3,
                ]
    
    tab_list_B =[
                tabB0,
                tabB1,
                ]
    
    widget = Container(tab_list_A, tab_list_B, reactor)
    # widget.show()
    reactor.suggestThreadPoolSize(50)
    reactor.run()