import json
import numpy as np
import time
import os
import datetime

from twisted.internet.defer import inlineCallbacks
from twisted.internet import task
from twisted.internet.threads import deferToThread

from client_tools.widgets import SuperSpinBox

from PyQt5 import QtCore, Qt, QtWidgets
import matplotlib
matplotlib.use('QT5Agg')

import matplotlib.pylab as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas 
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from client_tools.widgets import ClickableLabel

class AFGControllerClient(QtWidgets.QGroupBox):
    name = None
    DeviceProxy = None
    
    vStepsize = 0.01
    voltage_units = [(0, 'V')]
    voltage_digits = 3
    spinbox_width = 80
    
    lockedColor = '#80ff80'
    unlockedColor = '#ff8080'
    
    updateID = np.random.randint(0, 2**31 - 1)
        
    def __init__(self, reactor):
        QtWidgets.QDialog.__init__(self)
        self.reactor = reactor
        reactor.callInThread(self.initialize)
        self.connectLabrad()
            
    @inlineCallbacks
    def connectLabrad(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name=self.name, host=os.getenv('LABRADHOST'), password='')
        yield self.cxn.update.signal__signal(self.updateID)
        yield self.cxn.update.addListener(listener=self.receiveUpdate, source=None, 
                                          ID=self.updateID)
        yield self.cxn.update.register(self.name)

    def receiveUpdate(self, c, updateJson):
        update = json.loads(updateJson)
        dc = update.get('dc')
        if dc is not None:
            self.displayDc(dc)

    def initialize(self):
        import labrad
        cxn = labrad.connect(name=self.name, host=os.getenv('LABRADHOST'), password='')
        self.device = self.DeviceProxy(cxn)
        self.reactor.callFromThread(self.populateGUI)
        self.reactor.callFromThread(self.connectSignals)
    
    def populateGUI(self):
        self.AFGnameLabel = ClickableLabel('<b> RED MOT AFG </b>')
        
        self.ch1Label = ClickableLabel('CH1 RAMP: ')
        self.ch1Button = QtWidgets.QPushButton()
        self.ch1Button.setText('Configure')
        
        self.vh1Label = ClickableLabel('V_HIGH [V]: ')
        self.vh1Box = QtWidgets.QDoubleSpinBox()
        self.vh1Box.setKeyboardTracking(False)
        self.vh1Box.setRange(*self.device._v_range)
        self.vh1Box.setSingleStep(self.vStepsize) # Mininum Step Size at 
        self.vh1Box.setDecimals(
                abs(int(np.floor(np.log10(self.vStepsize)))))
        
        self.vl1Label = ClickableLabel('V_LOW [V]: ')
        self.vl1Box = QtWidgets.QDoubleSpinBox()
        self.vl1Box.setKeyboardTracking(False)
        self.vl1Box.setRange(*self.device._v_range)
        self.vl1Box.setSingleStep(self.vStepsize) # Mininum Step Size at 
        self.vl1Box.setDecimals(
                abs(int(np.floor(np.log10(self.vStepsize)))))
        
        self.rate1Label = ClickableLabel('Rate [kHz]: ')
        self.rate1Box = QtWidgets.QDoubleSpinBox()
        self.rate1Box.setKeyboardTracking(False)
        self.rate1Box.setRange(*self.device._rate_range)
        self.rate1Box.setSingleStep(0.1) # Mininum Step Size at 
        self.rate1Box.setDecimals(
                abs(int(np.floor(np.log10(0.1)))))
        
        self.dur1Label = ClickableLabel('Duration [ms]: ')
        self.dur1Box = QtWidgets.QDoubleSpinBox()
        self.dur1Box.setKeyboardTracking(False)
        self.dur1Box.setRange(*self.device._duration_range)
        self.dur1Box.setSingleStep(1) # Mininum Step Size at 
        self.dur1Box.setDecimals(
                abs(int(np.floor(np.log10(1)))))
        
        self.symm1Label = ClickableLabel('Symmetry [%]: ')
        self.symm1Box = QtWidgets.QDoubleSpinBox()
        self.symm1Box.setKeyboardTracking(False)
        self.symm1Box.setRange(*self.device._symmetry_range)
        self.symm1Box.setSingleStep(0.1) # Mininum Step Size at 
        self.symm1Box.setDecimals(
                abs(int(np.floor(np.log10(0.1)))))
        
        self.phase1Label = ClickableLabel('Phase [Degree]: ')
        self.phase1Box = QtWidgets.QDoubleSpinBox()
        self.phase1Box.setKeyboardTracking(False)
        self.phase1Box.setRange(*self.device._phase_range)
        self.phase1Box.setSingleStep(1) # Mininum Step Size at 
        self.phase1Box.setDecimals(
                abs(int(np.floor(np.log10(1)))))
    
        # lAYOUT #
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.AFGnameLabel, 0, 1, 1, 1,
                              QtCore.Qt.AlignHCenter)
        
        self.layout.addWidget(self.ch1Label, 1, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ch1Button, 1, 1)
        
        self.layout.addWidget(self.vh1Label, 2, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.vh1Box, 2, 1)
        self.layout.addWidget(self.vl1Label, 2, 2, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.vl1Box, 2, 3)
        
        self.layout.addWidget(self.rate1Label, 3, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.rate1Box, 3, 1)
        self.layout.addWidget(self.dur1Label, 3, 2, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.dur1Box, 3, 3)
        
        self.layout.addWidget(self.symm1Label, 4, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.symm1Box, 4, 1)
        self.layout.addWidget(self.phase1Label, 4, 2, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.phase1Box, 4, 3)
        
        self.setWindowTitle(self.name)
        self.setLayout(self.layout)
        self.setFixedSize(370, 150)
    
        self.reactor.callInThread(self.getAll)
    
    def getAll(self):
        self.getVH1()
        self.getVL1()
        self.getRATE1()
        self.getDUR1()
        self.getSYMM1()
        self.getPHASE1()
    
    def connectSignals(self):
        self.AFGnameLabel.clicked.connect(self.onNameLabelClick)
        self.ch1Button.released.connect(self.onConfigure1)
        
        self.vh1Box.valueChanged.connect(self.onNewVH1)
        self.vl1Box.valueChanged.connect(self.onNewVL1)
        self.rate1Box.valueChanged.connect(self.onNewRATE1)
        self.dur1Box.valueChanged.connect(self.onNewDUR1)
        self.symm1Box.valueChanged.connect(self.onNewSYMM1)
        self.phase1Box.valueChanged.connect(self.onNewPHASE1)

    def onNameLabelClick(self):
        self.reactor.callInThread(self.getAll)   
    
    def onConfigure1(self):
        vh1 = self._v_high1
        vl1 = self._v_low1
        symm1 = self._symmetry1
        phase1 = self._phase1
        rate1 = self._rate1
        dur1 = self._duration1
        self.reactor.callInThread(self.setConfig1, vh1, vl1, symm1, phase1, rate1, dur1)
    
    def setConfig1(self, v_high, v_low, symmetry, phase, rate, duration):
        self.device.configure1(v_high, v_low, symmetry, phase, rate, duration)
    
    def onNewVH1(self):
        self._v_high1 = self.vh1Box.value()
    
    def getVH1(self):
        vh1 = self._v_high1
        self.reactor.callFromThread(self.displayVH1, vh1)
    
    def displayVH1(self, vh1):
        self.vh1Box.setValue(vh1)

    def onNewVL1(self):
        self._v_low1 = self.vl1Box.value()
    
    def getVL1(self):
        vl1 = self._v_low1
        self.reactor.callFromThread(self.displayVL1, vl1)
    
    def displayVL1(self, vl1):
        self.vl1Box.setValue(vl1)
        
    def onNewRATE1(self):
        self._rate1 = self.rate1Box.value()
        
    def getRATE1(self):
        rate1 = self._rate1
        self.reactor.callFromThread(self.displayRATE1, rate1)
    
    def displayRATE1(self, rate1):
        self.rate1Box.setValue(rate1)
        
    def onNewDUR1(self):
        self._duration1 = self.dur1Box.value()
        
    def getDUR1(self):
        dur1 = self._duration1
        self.reactor.callFromThread(self.displayDUR1, dur1)
    
    def displayDUR1(self, dur1):
        self.dur1Box.setValue(dur1)
        
    def onNewSYMM1(self):
        self._symmetry1 = self.symm1Box.value()
        
    def getSYMM1(self):
        symm1 = self._symmetry1
        self.reactor.callFromThread(self.displaySYMM1, symm1)
    
    def displaySYMM1(self, symm1):
        self.symm1Box.setValue(symm1)
        
    def onNewPHASE1(self):
        self._phase1 = self.phase1Box.value()
        
    def getPHASE1(self):
        phase1 = self._phase1
        self.reactor.callFromThread(self.displayPHASE1, phase1)
    
    def displayPHASE1(self, phase1):
        self.phase1Box.setValue(phase1)
    
    def closeEvent(self, x):
        super(AFGControllerClient, self).closeEvent(x)
        self.reactor.stop()

class MultipleClientContainer(QtWidgets.QWidget):
    name = None
    def __init__(self, client_list, reactor):
        QtWidgets.QDialog.__init__(self)
        self.client_list = client_list
        self.reactor = reactor
        self.populateGUI()
 
    def populateGUI(self):
        self.layout = QtWidgets.QHBoxLayout()
        for client in self.client_list:
            self.layout.addWidget(client)
        self.setFixedSize(400* len(self.client_list), 200)
        self.setWindowTitle(self.name)
        self.setLayout(self.layout)

    def closeEvent(self, x):
        super(MultipleClientContainer, self).closeEvent(x)
        self.reactor.stop()

if __name__ == '__main__':
    from arbitrary_function_generator.devices.Red_AFG import RedAFGProxy

    class AFGSubClient(AFGControllerClient):
        name = 'RED AFG'
        DeviceProxy = RedAFGProxy

        _v_high1 = 0
        _v_low1 = -2
        _symmetry1 = 50
        _phase1 = 90    # 90: starting from VH
        _rate1 = 20   # in kHz
        _duration1 = 300  # in ms
        

    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    from client_tools import qt5reactor 
    qt5reactor.install()
    from twisted.internet import reactor

    widgets = [
            AFGSubClient(reactor)
            ]
    widget = MultipleClientContainer(widgets, reactor)
    widget.show()
    reactor.suggestThreadPoolSize(10)
    reactor.run()