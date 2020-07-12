import json
import numpy as np
import sys
import os
import time

from PyQt5 import QtWidgets
# from PyQt5.QtCore import pyqtSignal
from twisted.internet.defer import inlineCallbacks

# from ecdl.clients.default import ParameterLabel

from client_tools.connection import connection
# from client_tools.widgets import SuperSpinBox

# from conductor.experiment import Experiment

ACTION_WIDTH = 200
ACTION_HEIGHT = 50

class ButtonActionWidget(QtWidgets.QPushButton):
    name = None
    servername = None
    
    ni_servername = 'ni'
    update_id = np.random.randint(0, 2**31 - 1)
    
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
        self.context = yield self.cxn.context()
        try:
            self.populateGUI()
            yield self.connectSignals()
        except Exception as e:
            print(e)
            self.setDisable(True)
    
    def populateGUI(self):
        # self.action_button = QtWidgets.QPushButton()
        # self.action_button.setText(self.name)
        # self.layout = QtWidgets.QGridLayout()
        # self.layout.addWidget(self.action_button)
        self.setText(self.name)
        
        self.setWindowTitle(self.name)
#        self.setLayout(self.layout)
        self.setFixedSize(ACTION_WIDTH , ACTION_HEIGHT)

    @inlineCallbacks
    def connectSignals(self):
        conductor_server = yield self.cxn.get_server('conductor')
        yield conductor_server.signal__update(self.update_id)
        yield conductor_server.addListener(listener=self.receive_update, source=None, 
                                     ID=self.update_id)
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)
        # self.action_button.released.connect(self.onButtonPressed)
        self.released.connect(self.onButtonPressed)
        self.getAll()
    
    def receive_update(self, c, signal_json):
        pass
    
    def getAll(self):
        pass
    
    @inlineCallbacks
    def onButtonPressed(self):
        pass
    
    @inlineCallbacks
    def reinitialize(self):
        self.setDisabled(False)
        # server = yield self.cxn.get_server(self.servername)
        # yield server.signal__update(self.update_id, context=self.context)
        # yield server.addListener(listener=self.receive_update, source=None,
        #                           ID=self.update_id, context=self.context)

    def disable(self):
        self.setDisabled(True)

    # def closeEvent(self, x):
    #     # self.reactor.stop()
    #     pass

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
        is_running = yield server.check_running()
        if is_running:
            print('Experiment running, please stop first.')
            pass
        else:
            yield server.queue_experiment(request_json, True)
            yield server.trigger_on()
    
    def receive_update(self, c, signal_json):
        pass
        
    def getAll(self):
        pass

class StopExperiment(ButtonActionWidget):
    name = 'Stop Experiment'
    servername = 'conductor'

    @inlineCallbacks
    def onButtonPressed(self):
        server = yield self.cxn.get_server(self.servername)
        yield server.trigger_off()
    
    def receive_update(self, c, signal_json):
        pass
    
    def getAll(self):
        pass

class PauseToggle(ButtonActionWidget):
    name = 'PauseToggle'
    servername = 'conductor'
    
    @inlineCallbacks
    def onButtonPressed(self):
        server = yield self.cxn.get_server(self.servername)
        yield server.pause_experiment_toggle()
        yield self.getPauseState()
        
    def getAll(self):
        self.getPauseState()
    
    @inlineCallbacks
    def getPauseState(self):
        server = yield self.cxn.get_server(self.servername)
        pause_state = yield server.check_pause()
        self.DisplayNewPauseState(pause_state)
    
    def DisplayNewPauseState(self, pause_state):
        # print(pause_state)
        if pause_state:
            self.setChecked(1)
            self.setText('Resume Experiment')
        else:
            self.setChecked(0)
            self.setText('Pause Experiment')
            
    def receive_update(self, c, signal_json):
        signal = json.loads(signal_json)
        for message_type, message in signal.items():
            if (message_type == 'pause_toggle') and (message is not None):
                # self.reactor.callInThread(self.getPauseState)
                self.getPauseState()
    
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
        # pass

if __name__ == '__main__':
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    from client_tools import qt5reactor
    qt5reactor.install()
    from twisted.internet import reactor
    widgets = [
        RunBlueMOT(reactor),
        StopExperiment(reactor),
        PauseToggle(reactor),
        ]
    widget = MultipleActionsContainer(widgets, reactor)
    widget.show()
    reactor.run()