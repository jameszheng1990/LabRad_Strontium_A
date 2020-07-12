import json
import numpy as np
import time
import os
import datetime

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import task
from twisted.internet.threads import deferToThread

from client_tools.connection import connection
from client_tools.widgets import SuperSpinBox

from PyQt5 import QtCore, Qt, QtWidgets
import matplotlib
matplotlib.use('QT5Agg')

import matplotlib.pylab as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas 
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from client_tools.widgets import ClickableLabel
from msquared_wlm_lock.clients.widgets.pid_widgets import PIDClient
from msquared_wlm_lock.clients.widgets.lock_widgets import LockClient
from msquared_wlm_lock.clients.widgets.msq_widgets import MSQClient


class WLMLockControllerClient(QtWidgets.QGroupBox):
    name = None
    wlm_servername = None
    msquared_servername = None
    wlm_lock_servername = None
    
    spinbox_width = 80
    
    lockedColor = '#80ff80'
    unlockedColor = '#ff8080'
    
    update_id = np.random.randint(0, 2**31 - 1)
        
    def __init__(self, reactor, cxn = None):
        QtWidgets.QDialog.__init__(self)
        self.reactor = reactor
        self.cxn = cxn 
        self.initialize()

    @inlineCallbacks
    def initialize(self):
        if self.cxn is None:
            self.cxn = connection()
            cname = '{} - client'.format(self.name)
            yield self.cxn.connect(name=cname)
        try:
            self.populateGUI()
            yield self.connectSignals()
        except Exception as e:
            print(e)
            self.setDisable(True)

    def populateGUI(self):
        self.LockClient = LockClient(self.reactor, self.cxn,
                                     self.wlm_lock_servername, self)
        self.PIDClient = PIDClient(self.reactor, self.cxn,
                                   self.wlm_lock_servername, self)
        self.MSQClient = MSQClient(self.reactor, self.cxn, self.msquared_servername,
                                   self.msquared_devicename, self)
        
        self.HLine = QtWidgets.QFrame()
        self.HLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.HLine.setFrameShadow( QtWidgets.QFrame.Raised)
        self.VLine = QtWidgets.QFrame()
        self.VLine.setFrameShape(QtWidgets.QFrame.VLine)
        self.VLine.setFrameShadow( QtWidgets.QFrame.Raised)
        
        # lAYOUT #
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.LockClient, 1, 0, 2, 3)
        self.layout.addWidget(self.HLine, 3, 0, 1, 3)
        self.layout.addWidget(self.PIDClient, 4, 0, 4, 3)
        self.layout.addWidget(self.VLine, 1, 4, 7, 1)
        self.layout.addWidget(self.MSQClient, 1, 5, 7, 3)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)
        
        self.setWindowTitle(self.name)
        self.setLayout(self.layout)
        # self.setFixedSize(420*2, 530)

    @inlineCallbacks
    def connectSignals(self):
        self.context = yield self.cxn.context()
        
    def receive_update(self, c, signal_json):
        pass
    
    @inlineCallbacks
    def toggle_lock(self):
        task_state = self.LockClient.serverButton.isChecked()
        etalon_state = self.MSQClient.lockButton.isChecked()
        if not task_state or not etalon_state:
            yield self.LockClient.disableLock()
        else:
            self.LockClient.enableLock()
        
    def closeEvent(self, x):
        pass
        # super(WLMLockControllerClient, self).closeEvent(x)
        # self.PIDClient.wlm_lock_server.remove_etalon_lock(10) # TODO: Remove Etalon Lock when exit
        # try:
        #     self.reactor.stop()
        # except:
        #     pass


if __name__ == '__main__':
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    from client_tools import qt5reactor 
    qt5reactor.install()
    from twisted.internet import reactor
    
    class WLMLockClient(WLMLockControllerClient):
        
        name = 'WLM lock'
        wlm_servername = 'hf_wavemeter'
        msquared_servername = 'msquared'
        wlm_lock_servername = 'msquared_wlm_lock'
        msquared_devicename = 'M2Sprout'
        

    widgets = WLMLockClient(reactor)
    widgets.show()
    reactor.suggestThreadPoolSize(10)
    reactor.run()