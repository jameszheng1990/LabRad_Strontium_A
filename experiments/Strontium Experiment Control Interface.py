from PyQt5 import QtCore, QtWidgets
from twisted.internet.defer import inlineCallbacks
import matplotlib, time
matplotlib.use('QT5Agg')

from current_controller.clients.default import CurrentControllerClient
from current_controller.devices.blue_slave_1 import BlueSlave1Proxy
from current_controller.devices.blue_slave_2 import BlueSlave2Proxy
from current_controller.devices.blue_slave_3 import BlueSlave3Proxy

from wavemeter_lock.clients.default import WLMLockControllerClient
from wavemeter_lock.devices.repump_sg import RepumpSGProxy
from wavemeter_lock.devices.hf_wlm import HFWLMProxy

from rf.clients.default import RFClient
from rf.devices.dim3000reda import DIM3000REDAProxy
from rf.devices.dim3000blue2 import DIM3000BLUE2Proxy

from arbitrary_function_generator.client.default import AFGControllerClient
from arbitrary_function_generator.devices.Red_AFG import RedAFGProxy

from sequencer.clients.default import SequencerClient
from conductor.clients.common_action import ButtonActionWidget
import json
from ni_server.proxy import NIProxy

from camera2.clients.default import CameraClient
from camera2.devices.ikon import IKonProxy

class MultipleClientContainer(QtWidgets.QWidget):
    name = None
    
    def __init__(self, tab_list, reactor):
        QtWidgets.QDialog.__init__(self)
        self.tab_list = tab_list
        self.title = 'Strontium Experiment Control Interface'
        self.reactor = reactor
        self.populateGUI()
        self.setWindowTitle(self.title)
 
    def populateGUI(self):
        self.layout = QtWidgets.QHBoxLayout()
        
        self.tabs = QtWidgets.QTabWidget()
        self.tab0 = QtWidgets.QWidget()
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab3 = QtWidgets.QWidget()
        self.tab4 = QtWidgets.QWidget()
        
        self.tabs.addTab(self.tab0, "Blue && Repump Laser")
        self.tabs.addTab(self.tab1, "RF && AFG")
        self.tabs.addTab(self.tab2, "Sequencer")
        self.tabs.addTab(self.tab3, "Common Actions")
        self.tabs.addTab(self.tab4, "Camera")
        
        self.tab0.layout = QtWidgets.QHBoxLayout()
        for client in self.tab_list[0]:
            self.tab0.layout.addWidget(client)
            self.tab0.setFixedSize(360* len(self.tab_list[0]), 600)
            self.tab0.setLayout(self.tab0.layout)
            
        self.tab1.layout = QtWidgets.QHBoxLayout()
        for client in self.tab_list[1]:
            self.tab1.layout.addWidget(client)
            self.tab1.setFixedSize(300* len(self.tab_list[1]), 300)
            self.tab1.setLayout(self.tab1.layout)
        
        self.tab2.layout = QtWidgets.QGridLayout()
        for client in self.tab_list[2]:
            self.tab2.layout.addWidget(client)
            self.tab2.setLayout(self.tab2.layout)
        
        self.tab3.layout = QtWidgets.QGridLayout()
        for client in self.tab_list[3]:
            self.tab3.layout.addWidget(client)
            self.tab3.setFixedSize(220* len(self.tab_list[1]), 120)
            self.tab3.setLayout(self.tab3.layout)
        
        # self.tab4.layout = QtWidgets.QGridLayout()
        # if self.tab_list[4]:
        #     for client in self.tab_list[4]:
        #         self.tab4.layout.addWidget(client)
        #         self.tab4.setLayout(self.tab4.layout)
        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
    def closeEvent(self, x):
        super(MultipleClientContainer, self).closeEvent(x)
        self.reactor.stop()

if __name__ == '__main__':
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    from client_tools import qt5reactor 
    qt5reactor.install()
    from twisted.internet import reactor
    
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
    
    class WLMSubClient(WLMLockControllerClient):
        name1 = 'HF WLM'
        DeviceProxy1 = HFWLMProxy
        name2 = 'Repump SG'
        DeviceProxy2 = RepumpSGProxy
    
    class DIM3000REDAClient(RFClient):
        name = 'RED_A'
        DeviceProxy = DIM3000REDAProxy
        
        frequencyDigits = 6
        amplitudeDigits = 2
        fmfreqDigits = 1
        
    class DIM3000BLUE2Client(RFClient):
        name = 'BLUE_2'
        DeviceProxy = DIM3000BLUE2Proxy
        
        frequencyDigits = 6
        amplitudeDigits = 2
        fmfreqDigits = 1
    
    class AFGSubClient(AFGControllerClient):
        name = 'RED AFG'
        DeviceProxy = RedAFGProxy

        _v_high1 = 0
        _v_low1 = -2
        _symmetry1 = 50
        _phase1 = 90    # 90: starting from VH
        _rate1 = 20   # in kHz
        _duration1 = 300  # in ms
    
    class IKonClient(CameraClient):
        name = 'IKon'
        DeviceProxy = IKonProxy
        
###############################################################################       
        
    class RunBlueMOT(ButtonActionWidget):
        name = 'Run Blue MOT w/ manual MOT Coils'
        servername = 'conductor'
    
        @inlineCallbacks
        def onButtonPressed(self):
            server = yield self.cxn.get_server(self.servername)
            request = {
                'sequencer.sequence': ['blue_mot_ss_wo_mot']
                }
            yield server.set_parameter_values(json.dumps(request))
            yield self.ni.Trigger_Once_On() # This will trigger ON only once, and then OFF, so you don't have to reload.

    class StopExperiment(ButtonActionWidget):
        name = 'Stop Experiment'
        servername = 'conductor'

        @inlineCallbacks
        def onButtonPressed(self):
            server = yield self.cxn.get_server(self.servername)
            yield server.stop_experiment()
            yield self.ni.Trigger_Off()
        
###############################################################################    
    
    tab0 = [
            BlueSlave1Client(reactor),
            BlueSlave2Client(reactor),
            BlueSlave3Client(reactor),
            WLMSubClient(reactor),
            ]
    
    tab1 = [
            DIM3000BLUE2Client(reactor),
            DIM3000REDAClient(reactor),
            AFGSubClient(reactor),
            ]
    
    tab2 = [
            SequencerClient(reactor),
            ]
    
    tab3 = [
            RunBlueMOT(reactor),
            StopExperiment(reactor),
            ]
    
    tab4 = [
            IKonClient(reactor),
            ]
    
    tab_list = [
                tab0,
                tab1,
                tab2,
                tab3,
                # tab4,
                ]
    
    widget = MultipleClientContainer(tab_list, reactor)
    widget.show()
    reactor.suggestThreadPoolSize(20)
    reactor.run()