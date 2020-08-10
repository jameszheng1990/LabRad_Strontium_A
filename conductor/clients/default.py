import json
import numpy as np
import sys
import os
import time

from PyQt5 import QtWidgets
from twisted.internet.defer import inlineCallbacks
from client_tools.connection import connection
from client_tools.widgets import ClickableLabel, SuperSpinBox

from conductor.clients.widgets.commonaction_widgets import CommonActionClient
from conductor.clients.widgets.node_widgets import NodeClient

class ConductorControl(QtWidgets.QGroupBox):
    name = None
    servername = 'conductor'
    
    updateID = np.random.randint(0, 2**31 - 1)
    
    
    def __init__(self, reactor, cxn=None):
        QtWidgets.QDialog.__init__(self)
        self.reactor = reactor
        self.cxn = cxn 
        self.initialize()

    @inlineCallbacks
    def initialize(self):
        if self.cxn is None:
            self.cxn = connection()
            cname = '{} - {} - client'.format(self.servername, self.name)
            yield self.cxn.connect(name=cname)
        try:
            self.populateGUI()
            yield self.connectSignals()
        except Exception as e:
            print(e)
            # self.setDisable(True)
    
    def populateGUI(self):
        self.CommonActionClient = CommonActionClient(self.reactor, self.cxn,
                                     self.servername, self)
        self.NodeClient = NodeClient(self.reactor, self.cxn, self)
        
        self.VLine = QtWidgets.QFrame()
        self.VLine.setFrameShape(QtWidgets.QFrame.VLine)
        self.VLine.setFrameShadow( QtWidgets.QFrame.Raised)
        
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.CommonActionClient, 1, 0, 1, 2)
        self.layout.addWidget(self.VLine, 1, 3, 1, 1)
        self.layout.addWidget(self.NodeClient, 1, 4, 1, 3)
        
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        self.setWindowTitle(self.name)
        self.setLayout(self.layout)
        self.setFixedSize(800, 300)

    @inlineCallbacks
    def connectSignals(self):
        self.context = yield self.cxn.context()
        conductor_server = yield self.cxn.get_server('conductor')
        yield conductor_server.signal__update(self.updateID)
        yield conductor_server.addListener(listener=self.receive_update, source=None, 
                                     ID=self.updateID)
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)

    def receive_update(self, c, signal_json):
        signal = json.loads(signal_json)
        for message_type, message in signal.items():
            if (message_type == 'pause_toggle') and (message is not None):
                self.CommonActionClient.getPauseState()
            if (message_type == 'is_running') and (message is not None):
                self.NodeClient.disableAll(message)
                self.CommonActionClient.disableWhenRunning(message)

    @inlineCallbacks
    def reinitialize(self):
        self.CommonActionClient.disableAll(False)
        self.NodeClient.disableAll(False)
        
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.updateID, context=self.context)
        try:
            yield server.removeListener(listener=self.receive_update, source=None,
                                   ID=self.updateID, context=self.context)
        except:
            pass
        yield server.addListener(listener=self.receive_update, source=None,
                                  ID=self.updateID, context=self.context)

    def disable(self):
        self.CommonActionClient.disableAll(True)
        self.NodeClient.disableAll(True)

    def closeEvent(self, x):
        self.reactor.stop()
    
if __name__ == '__main__':

    class ConductorControl_Client(ConductorControl):
        name = 'Conductor control'
        
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    from client_tools import qt5reactor
    qt5reactor.install()
    from twisted.internet import reactor
    widget = ConductorControl_Client(reactor)
    widget.show()
    reactor.run()