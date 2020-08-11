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


class MSQClient(QtWidgets.QWidget):
    """ Widget for Msquared server control """
    msquared_servername = None
    msquared_devicename = None 
    wlm_servername = None
    
    update_time1 = 2500 # [ms]
    update_time2 = 5000 # [ms]
    lock_update_time = 2500 # [ms]
    is_on_OneShot = False
    
    frequency_units = ['THz', 'GHz']
    wavelength_units = ['nm', 'um']
    
    etalon_range = (0, 100)  # Etalon tuner
    etalon_units = [(0, '%')]
    etalon_digits = 2
    etalon_max = 196
    
    resonator_range = (0, 100)  # Resonator tuner
    resonator_units = [(0, '%')]
    resonator_digits = 4
    resonator_max = 196
    
    fineresonator_range = (0, 100)  # Resonator Fine tuner
    fineresonator_units = [(0, '%')]
    fineresonator_digits = 2
        
    PD_range = (0, 100)
    PD_units = [(0, 'V')]
    PD_digits = 4

    xy_range = (0, 100)  # X, Y tuner
    xy_units = [(0, '%')]
    xy_digits = 2

    wl_range = (696, 877)  # Rough wavelength
    wl_units = [(0, 'nm')]
    wl_digits = 1
        
    spinbox_height = 30
    spinbox_width = 80
    update_id = np.random.randint(0, 2**31 - 1)
    
    def __init__(self, reactor, cxn, msquared_servername, msquared_devicename, 
                                     wlm_servername, parent):
        super(MSQClient, self).__init__()
        try:
            self.reactor = reactor
            self.cxn = cxn
            self.msquared_servername = msquared_servername
            self.msquared_devicename = msquared_devicename
            self.wlm_servername = wlm_servername 
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
        self.nameLabel = ClickableLabel('<b> MSquared Laser Control </b>')

        self.statusLabel = ClickableLabel('<b> MSquared Status: </b>')
        self.statusText = QtWidgets.QLineEdit()
        self.statusText.setReadOnly(True)
        self.statusText.setAlignment(QtCore.Qt.AlignCenter)
        self.statusText.setFixedHeight(40)
        self.statusText.setFont(QtGui.QFont('Arial', 10))
        
        self.wlmLabel = ClickableLabel('<b> HF Wavemeter: </b>')
        self.wlmText = QtWidgets.QLineEdit()
        self.wlmText.setReadOnly(True)
        self.wlmText.setAlignment(QtCore.Qt.AlignCenter)
        self.wlmText.setFixedHeight(40)
        self.wlmText.setFont(QtGui.QFont('Arial', 10))
           
        self.lockButton = QtWidgets.QPushButton()
        self.lockButton.setCheckable(True)
        self.lockButton.setFixedHeight(40)
        self.lockButton.setFixedWidth(120)
        
        self.oneshotButton = QtWidgets.QPushButton()
        self.oneshotButton.setFixedHeight(40)
        self.oneshotButton.setFixedWidth(120)
        self.oneshotButton.setText('One Shot Alignment')
        
        self.manualButton = QtWidgets.QPushButton()
        self.manualButton.setFixedHeight(40)
        self.manualButton.setFixedWidth(120)
        self.manualButton.setText('Manual Alignment')
        
        self.EtalonTunerLabel = ClickableLabel('Etalon Tuner: ')
        self.EtalonTunerBox = SuperSpinBox(self.etalon_range, self.etalon_units,
                                        self.etalon_digits)
        self.EtalonTunerBox.setFixedHeight(self.spinbox_height)
        self.EtalonTunerBox.setFixedWidth(self.spinbox_width)
      
        self.ResonatorTunerLabel = ClickableLabel('Resonator Tuner: ')
        self.ResonatorTunerBox = SuperSpinBox(self.resonator_range, self.resonator_units,
                                        self.resonator_digits)
        self.ResonatorTunerBox.setFixedHeight(self.spinbox_height)
        self.ResonatorTunerBox.setFixedWidth(self.spinbox_width)
        
        self.ResonatorFineTunerLabel = ClickableLabel('Resonator Fine \n Tuner:')
        self.ResonatorFineTunerLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.ResonatorFineTunerBox = SuperSpinBox(self.fineresonator_range, self.fineresonator_units,
                                        self.fineresonator_digits)
        self.ResonatorFineTunerBox.setFixedHeight(self.spinbox_height)
        self.ResonatorFineTunerBox.setFixedWidth(self.spinbox_width)
        
        self.XLabel = ClickableLabel('X Tuner: ')
        self.XBox = SuperSpinBox(self.xy_range, self.xy_units,
                                        self.xy_digits)
        self.XBox.setFixedHeight(self.spinbox_height)
        self.XBox.setFixedWidth(self.spinbox_width)
        
        self.YLabel = ClickableLabel('Y Tuner: ')
        self.YBox = SuperSpinBox(self.xy_range, self.xy_units,
                                        self.xy_digits)
        self.YBox.setFixedHeight(self.spinbox_height)
        self.YBox.setFixedWidth(self.spinbox_width)        
        
        self.wavelengthLabel = ClickableLabel('Preset wavelength: \n (rough tune)')
        self.wavelengthLabel.setAlignment(QtCore.Qt.AlignRight| QtCore.Qt.AlignVCenter)
        self.wavelengthBox = SuperSpinBox(self.wl_range, self.wl_units,
                                        self.wl_digits)
        self.wavelengthBox.setFixedHeight(self.spinbox_height)
        self.wavelengthBox.setFixedWidth(self.spinbox_width)   
        
        self.EtalonPDLabel = ClickableLabel('Etalon PD DC:')
        self.EtalonPDLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.EtalonPDBox = SuperSpinBox(self.PD_range, self.PD_units,
                                        self.PD_digits)
        self.EtalonPDBox.setFixedHeight(self.spinbox_height)
        self.EtalonPDBox.setFixedWidth(self.spinbox_width)
        self.EtalonPDBox.setReadOnly(True)
        
        self.OutputPDLabel = ClickableLabel('Output PD:')
        self.OutputPDLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.OutputPDBox = SuperSpinBox(self.PD_range, self.PD_units,
                                        self.PD_digits)
        self.OutputPDBox.setFixedHeight(self.spinbox_height)
        self.OutputPDBox.setFixedWidth(self.spinbox_width)
        self.OutputPDBox.setReadOnly(True)
        
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.nameLabel, 1, 0, 1, 6,
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.statusLabel, 2, 0, 2, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.statusText, 2, 1, 2, 5)
        self.layout.addWidget(self.wlmLabel, 4, 0, 2, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.wlmText, 4, 1, 2, 5)
        self.layout.addWidget(self.lockButton, 6, 0, 2, 2,
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.oneshotButton, 6, 2, 2, 2,
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.manualButton, 6, 4, 2, 2,
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.EtalonTunerLabel, 8, 0, 2, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.EtalonTunerBox, 8, 1, 2, 2, 
                              QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.XLabel, 8, 3, 2, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.XBox, 8, 4, 2, 2, 
                              QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.ResonatorTunerLabel, 10, 0, 2, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ResonatorTunerBox, 10, 1, 2, 2, 
                              QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.YLabel, 10, 3, 2, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.YBox, 10, 4, 2, 2, 
                              QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.ResonatorFineTunerLabel, 12, 0, 2, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ResonatorFineTunerBox, 12, 1, 2, 2, 
                              QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.wavelengthLabel, 12, 3, 2, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.wavelengthBox, 12, 4, 2, 2, 
                              QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.EtalonPDLabel, 14, 0, 2, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.EtalonPDBox, 14, 1, 2, 2, 
                              QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.OutputPDLabel, 14, 3, 2, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.OutputPDBox, 14, 4, 2, 2, 
                              QtCore.Qt.AlignLeft)
        
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)
        self.setFixedSize(450, 450)
        
    @inlineCallbacks
    def connectWidgets(self):
        self.msquared_server = yield self.cxn.get_server(self.msquared_servername)
        yield self.msquared_server.signal__update(self.update_id)
        yield self.msquared_server.addListener(listener=self.receive_update, source=None, 
                                       ID=self.update_id)
        self.wlm_server = yield self.cxn.get_server(self.wlm_servername)
        self.nameLabel.clicked.connect(self.onNameLabelClick)
        self.wlmLabel.clicked.connect(self.getWLM)
        self.lockButton.released.connect(self.onLockButton)
        self.oneshotButton.released.connect(self.onOneShotButton)
        self.manualButton.released.connect(self.onManualButton)
        self.XBox.returnPressed.connect(self.onX)
        self.YBox.returnPressed.connect(self.onY)
        self.wavelengthBox.returnPressed.connect(self.onWavelength)
        self.EtalonPDLabel.clicked.connect(self.getEtalonPD)
        self.OutputPDLabel.clicked.connect(self.getOutputPD)
        
        self.timer1 = QtCore.QTimer(self)
        self.timer1.timeout.connect(self.timer_task1)
        self.timer1.start(self.update_time1)
        
        self.timer2 = QtCore.QTimer(self)
        self.timer2.timeout.connect(self.timer_task2)
        self.timer2.start(self.update_time2)
        
        self.lock_timer = QtCore.QTimer(self)
        self.lock_timer.timeout.connect(self.lock_timer_task)
        
        self.getAll()
    
    def receive_update(self, c, signal_json):
        signal = json.loads(signal_json)
        message = signal.get('alignment_x_auto')
        if message is not None:
            value = message[self.msquared_devicename]
            self.displayX(value)
        message = signal.get('alignment_y_auto')
        if message is not None:
            value = message[self.msquared_devicename]
            self.displayY(value)
            
    def disable_when_wlm_lock(self, state):
        self.lockButton.setDisabled(state)
        self.EtalonTunerBox.setDisabled(state)
        self.wavelengthBox.setDisabled(state)
        
        resonator_state = not bool(state ^ self.lockButton.isChecked())
        self.ResonatorTunerBox.setDisabled(resonator_state)
        self.ResonatorFineTunerBox.setDisabled(resonator_state)
    
    def onNameLabelClick(self):
        self.getAll()
    
    def timer_task1(self):
        if self.lockButton.isChecked():
            self.getLockState()
        if self.parent.LockClient.lockButton.isChecked():
            self.lock_timer.start(self.lock_update_time)
        else:
            self.lock_timer.stop()
    
    def timer_task2(self):
        if self.is_on_OneShot:
            self.getOneShotState()
            self.getOutputPD()
            self.getEtalonPD()
            
    def lock_timer_task(self):
        self.getWLM()
        self.getResonatorTuner()
        self.getEtalonPD()
        self.getOutputPD()
    
    def getAll(self):
        self.getLockState()
        self.getEtalonTuner()
        self.getResonatorTuner()
        self.getX()
        self.getY()
        self.getWavelength()
        self.getWLM()
        self.getEtalonPD()
        self.getOutputPD()
            
    def onLockButton(self):
        lock_state = self.lockButton.isChecked()
        self.setLockState(lock_state)
        
    @inlineCallbacks
    def setLockState(self, lock_state):
        if lock_state:
            request_json = json.dumps({self.msquared_devicename: True})
        else:
            request_json = json.dumps({self.msquared_devicename: False})
        yield self.msquared_server.etalon_lock(request_json)
        self.displayLockState(lock_state)

    @inlineCallbacks
    def getLockState(self):
        request_json = json.dumps({self.msquared_devicename: None})
        response_json = yield self.msquared_server.etalon_lock(request_json)
        response = json.loads(response_json)
        message = response[self.msquared_devicename]
        if message == True:
            lock_state = True
        elif message == False:
            lock_state = False
        else:
            lock_state = False
            self.statusText.setText(message)
            request_json = json.dumps({self.msquared_devicename: False})
            yield self.msquared_server.etalon_lock(request_json)
        self.displayLockState(lock_state)
    
    def displayLockState(self, lock_state):
        if lock_state == True:
            self.lockButton.setChecked(1)
            self.lockButton.setText('Remove Etalon Lock')
            self.statusText.setText('Etalon lock ON')
            self.ResonatorTunerBox.setDisabled(False)
            self.ResonatorFineTunerBox.setDisabled(False)
        else:
            self.lockButton.setChecked(0)
            self.lockButton.setText('Apply Etalon Lock')
            self.statusText.setText('Etalon lock OFF')
            self.ResonatorTunerBox.setDisabled(True)
            self.ResonatorFineTunerBox.setDisabled(True)
        self.parent.toggle_lock()
            
    @inlineCallbacks
    def onOneShotButton(self):
        if not self.is_on_OneShot:
            self.is_on_OneShot = True
            mode = 4 # 4 for One Shot
            request_json = json.dumps({self.msquared_devicename: mode})
            yield self.msquared_server.beam_alignment(request_json)
            self.statusText.setText('One Shot Alignment Started...')
            self.oneshotButton.setDisabled(True)
            self.manualButton.setEnabled(True)
            self.XBox.setDisabled(True)
            self.YBox.setDisabled(True)
        else:
            pass
        
    @inlineCallbacks
    def getOneShotState(self):
        if self.is_on_OneShot:
            request_json = json.dumps({self.msquared_devicename: None})
            response_json = yield self.msquared_server.beam_alignment(request_json)
            status = json.loads(response_json).get(self.msquared_devicename)
            if status == True:
                self.is_on_OneShot = False
                self.statusText.setText('One Shot Alignment Completed')
                self.oneshotButton.setDisabled(False)
                self.XBox.setDisabled(False)
                self.YBox.setDisabled(False)
            else:
                pass
        else:
            pass
        
    @inlineCallbacks
    def onNewEtalonTuner(self):
        value = self.EtalonTunerBox.value()
        request_json = json.dumps({self.msquared_devicename: value})
        yield self.msquared_server.etalon_tune(request_json)
        self.displayEtalonTuner(value)
    
    @inlineCallbacks
    def getEtalonTuner(self):
        request_json = json.dumps({self.msquared_devicename: None})
        response_json = yield self.msquared_server.etalon_tune(request_json)
        response = json.loads(response_json)
        value = response.get(self.msquared_devicename)
        value_percentage = value/self.etalon_max*100
        self.displayEtalonTuner(value_percentage)
    
    def displayEtalonTuner(self, value):
        self.EtalonTunerBox.display(value)
     
    @inlineCallbacks
    def onNewResonatorTuner(self):
        value = self.ResonatorTunerBox.value()
        request_json = json.dumps({self.msquared_devicename: value})
        yield self.msquared_server.resonator_tune(request_json)
        self.displayResonatorTuner(value)
    
    @inlineCallbacks
    def getResonatorTuner(self):
        request_json = json.dumps({self.msquared_devicename: None})
        response_json = yield self.msquared_server.resonator_tune(request_json)
        response = json.loads(response_json)
        value = response.get(self.msquared_devicename)
        value_percentage = value/self.resonator_max*100
        self.displayResonatorTuner(value_percentage)
    
    def displayResonatorTuner(self, value):
        self.ResonatorTunerBox.display(value)        
     
    @inlineCallbacks
    def onManualButton(self):
        self.is_on_OneShot = False
        self.oneshotButton.setDisabled(False)
        self.XBox.setDisabled(False)
        self.YBox.setDisabled(False)
        mode = 1 # 1 for Manual
        request_json = json.dumps({self.msquared_devicename: mode})
        yield self.msquared_server.beam_alignment(request_json)
    
    @inlineCallbacks
    def onX(self):
        value = self.XBox.value()
        request_json = json.dumps({self.msquared_devicename: value})
        yield self.msquared_server.alignment_x(request_json)
        self.displayX(value)
        
    @inlineCallbacks
    def getX(self):
        request_json = json.dumps({self.msquared_devicename: None})
        response_json = yield self.msquared_server.alignment_x(request_json)
        response = json.loads(response_json)
        value = response.get(self.msquared_devicename)
        self.displayX(value)
    
    def displayX(self, value):
        self.XBox.display(value)

    @inlineCallbacks
    def onY(self):
        value = self.YBox.value()
        request_json = json.dumps({self.msquared_devicename: value})
        yield self.msquared_server.alignment_y(request_json)
        self.displayY(value)
            
    @inlineCallbacks
    def getY(self):
        request_json = json.dumps({self.msquared_devicename: None})
        response_json = yield self.msquared_server.alignment_y(request_json)
        response = json.loads(response_json)
        value = response.get(self.msquared_devicename)
        self.displayY(value)
        
    def displayY(self, value):
        self.YBox.display(value)
        
    @inlineCallbacks
    def onWavelength(self):
        value = self.wavelengthBox.value()
        request_json = json.dumps({self.msquared_devicename : value})
        yield self.msquared_server.wavelength(request_json)
        self.displayWavelength(value)
    
    @inlineCallbacks
    def getWavelength(self):
        request_json = json.dumps({self.msquared_devicename: None})
        response_json = yield self.msquared_server.wavelength(request_json)
        response = json.loads(response_json)
        value = response.get(self.msquared_devicename)
        self.displayWavelength(value)
    
    def displayWavelength(self, value):
        self.wavelengthBox.display(value)
   
    @inlineCallbacks
    def getWLM(self):
        units = self.parent.PIDClient.unitsBox.currentText()
        channel = self.parent.PIDClient.channelBox.currentText()
        if units in self.frequency_units:
            value = yield self.wlm_server.get_frequency(int(channel))
        elif units in self.wavelength_units:
            value = yield self.wlm_server.get_wavelength(int(channel))
        self.displayWLM(value, units)
    
    def displayWLM(self, value, units):
        self.wlmText.setText('{} {}'.format(value, units))
        
    @inlineCallbacks    
    def getEtalonPD(self):
        request_json = json.dumps({self.msquared_devicename: None})
        response_json = yield self.msquared_server.etalon_pd(request_json)
        response = json.loads(response_json)
        value = response.get(self.msquared_devicename)
        self.displayEtalonPD(value)
        
    def displayEtalonPD(self, value):
        self.EtalonPDBox.display(value)
        
    @inlineCallbacks    
    def getOutputPD(self):
        request_json = json.dumps({self.msquared_devicename: None})
        response_json = yield self.msquared_server.output_pd(request_json)
        response = json.loads(response_json)
        value = response.get(self.msquared_devicename)
        self.displayOutputPD(value)
        
    def displayOutputPD(self, value):
        self.OutputPDBox.display(value)
    
    def closeEvent(self, x):
        pass
        
        
        