import json
import numpy as np
import sys

import matplotlib
from PyQt5 import QtGui, QtCore, Qt, QtWidgets
from PyQt5.QtCore import pyqtSignal 
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import traceback
from twisted.internet.defer import inlineCallbacks, returnValue
from client_tools.connection import connection

from client_tools.widgets import ClickableLabel
from client_tools.widgets import SuperSpinBox


class LockClient(QtWidgets.QWidget):
    """ Widget for Msquared Lock server control """
    wlm_lock_servername = None
    
    setpoint = None
    setpoint_uints = None
    update_id = np.random.randint(0, 2**31 - 1)
    
    def __init__(self, reactor, cxn, wlm_lock_servername, parent):
        super(LockClient, self).__init__()
        try:
            self.reactor = reactor
            self.cxn = cxn
            self.wlm_lock_servername = wlm_lock_servername
            self.parent = parent
            self.connect()
        except Exception as e:
            print(e)
            traceback.print_exc()         

    @inlineCallbacks
    def connect(self):
        if self.cxn == None:
            self.cxn = connection()
            yield self.cxn.connect()
        self.populate()
        yield self.connectWidgets()
        
    def populate(self):
        self.nameLabel = ClickableLabel('<b> MSquared Laser Wavemeter Lock </b>')
        
        self.serverButton = QtWidgets.QPushButton()
        self.serverButton.setCheckable(True)
        self.serverButton.setFixedHeight(40)
        self.serverButton.setFixedWidth(120)
        
        self.lockButton = QtWidgets.QPushButton()
        self.lockButton.setCheckable(True)
        self.lockButton.setFixedHeight(40)
        self.lockButton.setFixedWidth(120)

        self.statusLabel = ClickableLabel('<b> Lock status: </b>')
        self.statusText = QtWidgets.QLineEdit()
        self.statusText.setReadOnly(True)
        self.statusText.setAlignment(QtCore.Qt.AlignCenter)
        self.statusText.setFixedHeight(40)
        self.statusText.setFixedWidth(300)
        self.statusText.setFont(QtGui.QFont('Arial', 12))
        
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.nameLabel, 1, 0, 1, 6,
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.serverButton, 2, 0, 2, 3,
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.lockButton, 2, 3, 2, 3,
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.statusLabel, 4, 0, 2, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.statusText, 4, 1, 2, 4,
                              QtCore.Qt.AlignLeft)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)
        self.setFixedSize(400, 150)
        
    @inlineCallbacks
    def connectWidgets(self):
        self.wlm_lock_server = yield self.cxn.get_server(self.wlm_lock_servername)
        yield self.wlm_lock_server.signal__update(self.update_id)
        yield self.wlm_lock_server.addListener(listener=self.receive_update, source=None, 
                                       ID=self.update_id)
        
        self.nameLabel.clicked.connect(self.onNameLabelClick)
        self.serverButton.released.connect(self.onServerButton)
        self.lockButton.released.connect(self.onLockButton)
        self.getAll()
        
    def enableServer(self):
        self.serverButton.setDisabled(False)
 
    def disableServer(self):
        self.serverButton.setDisabled(True) 
    
    def enableLock(self):
        self.lockButton.setDisabled(False)
 
    @inlineCallbacks
    def disableLock(self):
        self.lockButton.setDisabled(True)  
        self.statusText.setText('Start task and lock Etalon first!')
        try:
            yield self.wlm_lock_server.unlock()
        except:
            pass        
        self.getLockState()
    
    def receive_update(self, c, signal_json):
        signal = json.loads(signal_json)
        message = signal.get('wlm_lock_status')
        if message is not None:
            self.statusText.setText(message)
        # dc = update.get('dc')
        # if dc is not None:,
        #     self.displayDc(dc)
    
    def onNameLabelClick(self):
        self.getAll()
        
    def getAll(self):
        self.getServerState()
        self.getLockState()
    
    def onServerButton(self):
        server_state = self.serverButton.isChecked()
        self.setServerState(server_state)
    
    @inlineCallbacks
    def setServerState(self, server_state):
        """
        Lock time constant 2.5s, no need change regularly change.
        """
        if server_state:
            yield self.wlm_lock_server.start_task()
        else:
            yield self.wlm_lock_server.stop_task()
        self.displayServerState(server_state)
        self.getLockState()

    @inlineCallbacks
    def getServerState(self):
        server_state = yield self.wlm_lock_server.get_task_state()
        self.displayServerState(server_state)
    
    def displayServerState(self, server_state):
        if server_state:
            self.serverButton.setChecked(1)
            self.serverButton.setText('Stop Lock Task')
        else:
            self.serverButton.setChecked(0)
            self.serverButton.setText('Start Lock Task')
        self.parent.toggle_lock()
            
    def onLockButton(self):
        lock_state = self.lockButton.isChecked()
        self.setLockState(lock_state)
        
    @inlineCallbacks
    def setLockState(self, lock_state):
        self.displayLockState(lock_state)
        if lock_state:
            setpoint = yield self.wlm_lock_server.get_setpoint()
            yield self.wlm_lock_server.lock(setpoint)
        else:
            yield self.wlm_lock_server.unlock()

    @inlineCallbacks
    def getLockState(self):
        lock_state = yield self.wlm_lock_server.get_lock_status()
        self.displayLockState(lock_state)
    
    def displayLockState(self, lock_state):
        if lock_state == True:
            self.lockButton.setChecked(1)
            self.lockButton.setText('Unlock')
            self.disableServer()
            self.parent.PIDClient.disable_when_wlm_lock(True)
            self.parent.MSQClient.disable_when_wlm_lock(True)
        else:
            self.lockButton.setChecked(0)
            self.lockButton.setText('Lock')
            self.enableServer()
            self.parent.PIDClient.disable_when_wlm_lock(False)
            self.parent.MSQClient.disable_when_wlm_lock(False)
            
    # @inlineCallbacks
    # def get_setpoint(self):
    #     setpoint = yield self.wlm_lock_server.get_setpoint()
        # returnValue(setpoint)
        
    def closeEvent(self, x):
        # super(WLMLockControllerClient, self).closeEvent(x)
        # self.PIDClient.wlm_lock_server.remove_etalon_lock(10) # TODO: Remove Etalon Lock when exit
        try:
            print('111')
            self.reactor.stop()
            x.accept()
        except:
            pass
        
        
        