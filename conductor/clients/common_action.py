import json
import numpy as np
import sys
import os
import time

from PyQt5 import QtGui, QtCore, Qt, QtWidgets
from PyQt5.QtCore import pyqtSignal
from twisted.internet.defer import inlineCallbacks

from ecdl.clients.default import ParameterLabel

from client_tools.connection import connection
from client_tools.widgets import SuperSpinBox

from conductor.experiment import Experiment

ACTION_WIDTH = 200
ACTION_HEIGHT = 50

class ButtonActionWidget(QtWidgets.QPushButton):
    name = None
    servername = None
    
    ni_servername = 'ni'

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
            
        self.populateGUI()
        yield self.connectSignals()
    
    def populateGUI(self):
        self.action_button = QtWidgets.QPushButton()
        self.action_button.setText(self.name)
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.action_button)
        self.setText(self.name)
        
        self.setWindowTitle(self.name)
#        self.setLayout(self.layout)
        self.setFixedSize(ACTION_WIDTH , ACTION_HEIGHT)

    @inlineCallbacks
    def connectSignals(self):
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)
        self.action_button.released.connect(self.onButtonPressed)
        self.released.connect(self.onButtonPressed)
    
    @inlineCallbacks
    def onButtonPressed(self):
        pass
    
    def reinitialize(self):
        self.setDisabled(False)

    def disable(self):
        self.setDisabled(True)

    def closeEvent(self, x):
        self.reactor.stop()

class RunBlueMOT(ButtonActionWidget):
    name = 'Run Steady-state Blue MOT'
    servername = 'conductor'
    
    @inlineCallbacks
    def onButtonPressed(self):
        request = {
            'name' : 'blue_mot_ss',
            'parameters': {},  # passed to reload_parameters
            'parameter_values': {'sequencer.sequence':[
                        'blue_mot_ss',] },
            'loop' : False,
            }
        request_json = json.dumps(request)
        
        server = yield self.cxn.get_server(self.servername)
        
        yield server.queue_experiment(request_json, True)
        yield server.ao_off()
        yield server.trigger_on()

class StopExperiment(ButtonActionWidget):
    name = 'Stop Experiment'
    servername = 'conductor'

    @inlineCallbacks
    def onButtonPressed(self):
        server = yield self.cxn.get_server(self.servername)
        yield server.trigger_off()
        
class MultipleActionsContainer(QtWidgets.QWidget):
    name = None
    def __init__(self, client_list, reactor, cxn=None):
        QtWidgets.QDialog.__init__(self)
        self.client_list = client_list
        self.reactor = reactor
        self.initialize()
 
    def initialize(self):
        self.populateGUI()

    def populateGUI(self):
        self.layout = QtWidgets.QVBoxLayout()
        for client in self.client_list:
            self.layout.addWidget(client)
        self.setFixedSize(ACTION_WIDTH + 20 , (ACTION_HEIGHT + 12) * len(self.client_list) )
        self.setLayout(self.layout)
        self.setWindowTitle('conductor - common actions')

    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == '__main__':
    
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    from client_tools import qt5reactor
    qt5reactor.install()
    from twisted.internet import reactor
    widgets = [
        RunBlueMOT(reactor),
        StopExperiment(reactor),
        ]
    widget = MultipleActionsContainer(widgets, reactor)
    widget.show()
    reactor.run()