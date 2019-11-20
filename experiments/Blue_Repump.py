from PyQt5 import QtCore, QtWidgets
import matplotlib
matplotlib.use('QT5Agg')

from current_controller.clients.default import CurrentControllerClient
from current_controller.devices.blue_slave_1 import BlueSlave1Proxy
from current_controller.devices.blue_slave_2 import BlueSlave2Proxy
from current_controller.devices.blue_slave_3 import BlueSlave3Proxy

from wavemeter_lock.clients.default import WLMLockControllerClient
from wavemeter_lock.devices.repump_sg import RepumpSGProxy
from wavemeter_lock.devices.hf_wlm import HFWLMProxy
    
class MultipleClientContainer(QtWidgets.QWidget):
    name = None
    
    def __init__(self, client_list, reactor):
        QtWidgets.QDialog.__init__(self)
        self.client_list = client_list
        self.reactor = reactor
        self.populateGUI()
        self.setWindowTitle('Blue Laser and Repump Controller')
 
    def populateGUI(self):
        self.layout = QtWidgets.QHBoxLayout()
        for client in self.client_list:
            self.layout.addWidget(client)
        self.setFixedSize(380* len(self.client_list), 650)
        self.setLayout(self.layout)

    def closeEvent(self, x):
        super(MultipleClientContainer, self).closeEvent(x)
        self.reactor.stop()

if __name__ == '__main__':
    
    class BlueSlave1Client(CurrentControllerClient):
        name = 'Blue Slave 1'
        DeviceProxy = BlueSlave1Proxy
    
    class BlueSlave2Client(CurrentControllerClient):
        name = 'Blue Slave 2'
        DeviceProxy = BlueSlave2Proxy
    
    class BlueSlave3Client(CurrentControllerClient):
        name = 'Blue Slave 3'
        DeviceProxy = BlueSlave3Proxy
    
    class WLMSubClient(WLMLockControllerClient):
        name1 = 'HF WLM'
        DeviceProxy1 = HFWLMProxy
        name2 = 'Repump SG'
        DeviceProxy2 = RepumpSGProxy

    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    from client_tools import qt5reactor 
    qt5reactor.install()
    from twisted.internet import reactor

    widgets = [
            BlueSlave1Client(reactor),
            BlueSlave2Client(reactor),
            BlueSlave3Client(reactor),
            WLMSubClient(reactor),
            ]
    widget = MultipleClientContainer(widgets, reactor)
    widget.show()
    reactor.suggestThreadPoolSize(30)
    reactor.run()