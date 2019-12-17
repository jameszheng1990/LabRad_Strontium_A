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

class WLMLockControllerClient(QtWidgets.QGroupBox):
    name1 = None
    DeviceProxy1 = None
    name2 = None
    DeviceProxy2 = None
    vStepsize = 0.001
    
#    voltage_range = (-10., 10.)
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
        self.cxn = yield connectAsync(name=self.name1, host=os.getenv('LABRADHOST'), password='')
        yield self.cxn.update.signal__signal(self.updateID)
        yield self.cxn.update.addListener(listener=self.receiveUpdate, source=None, 
                                          ID=self.updateID)
        yield self.cxn.update.register(self.name1)

    def receiveUpdate(self, c, updateJson):
        # 'Power' in functions means Monitor Current
        update = json.loads(updateJson)
        dc = update.get('dc')
        if dc is not None:
            self.displayDc(dc)

    def initialize(self):
        import labrad
        cxn = labrad.connect(name=self.name1, host=os.getenv('LABRADHOST'), password='')
        self.device1 = self.DeviceProxy1(cxn)
        self.device2 = self.DeviceProxy2(cxn)
        self.reactor.callFromThread(self.populateGUI)
        self.reactor.callFromThread(self.connectSignals)
    
    def populateGUI(self):
        self.SGname1Label = ClickableLabel('<b> 679 nm: </b>')
        
        self.dc1Label = ClickableLabel('set DC [V]: ')
        self.dc1Box = QtWidgets.QDoubleSpinBox()
        self.dc1Box.setKeyboardTracking(False)
        self.dc1Box.setRange(*self.device2._v_range)
        self.dc1Box.setSingleStep(self.vStepsize* 5) # Mininum Step Size at 
        self.dc1Box.setDecimals(
                abs(int(np.floor(np.log10(self.vStepsize)))))
        
        self.SGname2Label = ClickableLabel('<b> 707 nm: </b>')
        
        self.dc2Label = ClickableLabel('set DC [V]: ')
        self.dc2Box = QtWidgets.QDoubleSpinBox()
        self.dc2Box.setKeyboardTracking(False)
        self.dc2Box.setRange(*self.device2._v_range)
        self.dc2Box.setSingleStep(self.vStepsize* 5) # Mininum Step Size at 
        self.dc2Box.setDecimals(
                abs(int(np.floor(np.log10(self.vStepsize)))))
        
        self.WLMname1Label = ClickableLabel('<b> WLM Ch1 (nm) :</b>')
        
        self.ch1Box = QtWidgets.QDoubleSpinBox()
        self.ch1Box.setRange(0, 1e10)
        self.ch1Box.setReadOnly(True)
        self.ch1Box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.ch1Box.setDecimals(5)
        
        self.WLMname2Label = ClickableLabel('<b> WLM Ch2 (nm) :</b>')
        
        self.ch2Box = QtWidgets.QDoubleSpinBox()
        self.ch2Box.setRange(0, 1e10)
        self.ch2Box.setReadOnly(True)
        self.ch2Box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.ch2Box.setDecimals(5)
        
        self.WLMname3Label = ClickableLabel('<b> WLM Ch3 (nm) :</b>')
        
        self.ch3Box = QtWidgets.QDoubleSpinBox()
        self.ch3Box.setRange(0, 1e10)
        self.ch3Box.setReadOnly(True)
        self.ch3Box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.ch3Box.setDecimals(5)
        
        self.WLMname4Label = ClickableLabel('<b> WLM Ch4 (nm) :</b>')
        
        self.ch4Box = QtWidgets.QDoubleSpinBox()
        self.ch4Box.setRange(0, 1e10)
        self.ch4Box.setReadOnly(True)
        self.ch4Box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.ch4Box.setDecimals(5)
            
        # lAYOUT #
        
        
    
        # lAYOUT #
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.SGname1Label, 1, 0, 1, 1, 
                              QtCore.Qt.AlignHCenter)
        
        self.layout.addWidget(self.dc1Label, 2, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.dc1Box, 2, 1)
        
        self.layout.addWidget(self.SGname2Label, 3, 0, 1, 1, 
                              QtCore.Qt.AlignHCenter)
        
        self.layout.addWidget(self.dc2Label, 4, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.dc2Box, 4, 1)
        
        self.layout.addWidget(self.WLMname1Label, 5, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ch1Box, 5, 1)
        self.layout.addWidget(self.WLMname2Label, 6, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ch2Box, 6, 1)
        self.layout.addWidget(self.WLMname3Label, 7, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ch3Box, 7, 1)
        self.layout.addWidget(self.WLMname4Label, 8, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ch4Box, 8, 1)
        
        self.setWindowTitle(self.name1)
        self.setLayout(self.layout)
        self.setFixedSize(220, 200)
    
        self.reactor.callInThread(self.getAll)
    
    def getAll(self):
        self.getDc1()
        self.getDc2()
        self.getCh1()
        self.getCh2()
        self.getCh3()
        self.getCh4()
            
    def getDc1(self):
        voltage = self.device2.dc1
        self.reactor.callFromThread(self.displayDc1, voltage)

    def displayDc1(self, voltage):
        self.dc1Box.setValue(voltage)
    
    def getDc2(self):
        voltage = self.device2.dc2
        self.reactor.callFromThread(self.displayDc2, voltage)

    def displayDc2(self, voltage):
        self.dc2Box.setValue(voltage)
    
    def connectSignals(self):
        self.dc1Box.valueChanged.connect(self.onNewDc1)
        self.dc2Box.valueChanged.connect(self.onNewDc2)
        
        self.WLMname1Label.clicked.connect(self.onNameLabelWLM1Click)
        self.WLMname2Label.clicked.connect(self.onNameLabelWLM2Click)
        self.WLMname3Label.clicked.connect(self.onNameLabelWLM3Click)
        self.WLMname4Label.clicked.connect(self.onNameLabelWLM4Click)
        
    def onNewDc1(self):
        voltage = self.dc1Box.value()
        self.reactor.callInThread(self.setDc1, voltage)
        time.sleep(0.1)
#        self.getCh1()
#        self.getCh2()
        self.getCh3()
#        self.getCh4()
        
    def setDc1(self, voltage):
        self.device2.dc1 = voltage
        self.reactor.callFromThread(self.displayDc1, voltage)
        
    def onNewDc2(self):
        voltage = self.dc2Box.value()
        self.reactor.callInThread(self.setDc2, voltage)
        time.sleep(0.1)
#        self.getCh1()
        self.getCh2()
#        self.getCh3()
#        self.getCh4()
        
    def setDc2(self, voltage):
        self.device2.dc2 = voltage
        self.reactor.callFromThread(self.displayDc2, voltage)    
        
    #############################################################
    
    def onNameLabelWLM1Click(self):
        self.reactor.callInThread(self.getCh1)
    
    def getCh1(self):
        response = self.device1.get_wavelength(1)
        self.reactor.callFromThread(self.displayCh1, response)
    
    def displayCh1(self, response):
        self.ch1Box.setValue(response)
    
    def onNameLabelWLM2Click(self):
        self.reactor.callInThread(self.getCh2)
    
    def getCh2(self):
        response = self.device1.get_wavelength(2)
        self.reactor.callFromThread(self.displayCh2, response)
    
    def displayCh2(self, response):
        self.ch2Box.setValue(response)
    
    def onNameLabelWLM3Click(self):
        self.reactor.callInThread(self.getCh3)
    
    def getCh3(self):
        response = self.device1.get_wavelength(3)
        self.reactor.callFromThread(self.displayCh3, response)
    
    def displayCh3(self, response):
        self.ch3Box.setValue(response)
    
    def onNameLabelWLM4Click(self):
        self.reactor.callInThread(self.getCh4)
    
    def getCh4(self):
        response = self.device1.get_wavelength(4)
        self.reactor.callFromThread(self.displayCh4, response)
    
    def displayCh4(self, response):
        self.ch4Box.setValue(response)
        
    def closeEvent(self, x):
        super(WLMLockControllerClient, self).closeEvent(x)
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
        self.setFixedSize(250* len(self.client_list), 250)
        self.setWindowTitle(self.name)
        self.setLayout(self.layout)

    def closeEvent(self, x):
        super(MultipleClientContainer, self).closeEvent(x)
        self.reactor.stop()

if __name__ == '__main__':
    from wavemeter_lock.devices.repump_sg import RepumpSGProxy
    from wavemeter_lock.devices.hf_wlm import HFWLMProxy

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
            WLMSubClient(reactor)
            ]
    widget = MultipleClientContainer(widgets, reactor)
    widget.show()
    reactor.suggestThreadPoolSize(10)
    reactor.run()