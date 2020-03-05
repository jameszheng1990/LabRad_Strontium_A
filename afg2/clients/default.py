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
    
    updateID = np.random.randint(0, 2**31 - 1)
    
    scaleDisplayUnits = [(0, '%')]
    scaleDigits = 1
    
    offsetDisplayUnits = [(-3, 'mV'), (0, 'V')]
    offsetDigits = 3
    
    spinboxWidth = 100
        
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
        
        self.ch1Label = ClickableLabel('CH1: ')
        self.ch1Button = QtWidgets.QPushButton()
        self.ch1Button.setText('Configure')
        
        self.scale1Label = ClickableLabel('Scale 1: ')
        self.scale1Box = SuperSpinBox(self.device.scaleRange, 
                                      self.scaleDisplayUnits, 
                                      self.scaleDigits)
        self.scale1Box.setFixedWidth(self.spinboxWidth)
        
        self.offset1Label = ClickableLabel('Offset 1: ')
        self.offset1Box = SuperSpinBox(self.device.offsetRange, 
                                      self.offsetDisplayUnits, 
                                      self.offsetDigits)
        self.offset1Box.setFixedWidth(self.spinboxWidth)
        
        self.ch2Label = ClickableLabel('CH2: ')
        self.ch2Button = QtWidgets.QPushButton()
        self.ch2Button.setText('Configure')
        
        self.scale2Label = ClickableLabel('Scale 2: ')
        self.scale2Box = SuperSpinBox(self.device.scaleRange, 
                                      self.scaleDisplayUnits, 
                                      self.scaleDigits)
        self.scale2Box.setFixedWidth(self.spinboxWidth)
        
        self.offset2Label = ClickableLabel('Offset 2: ')
        self.offset2Box = SuperSpinBox(self.device.offsetRange, 
                                      self.offsetDisplayUnits, 
                                      self.offsetDigits)
        self.offset2Box.setFixedWidth(self.spinboxWidth)
        
        # lAYOUT #
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.AFGnameLabel, 0, 0, 1, 2,
                              QtCore.Qt.AlignHCenter)
        
        self.layout.addWidget(self.ch1Label, 1, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ch1Button, 1, 1)
        self.layout.addWidget(self.scale1Label, 2, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.scale1Box, 2, 1)
        self.layout.addWidget(self.offset1Label, 3, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.offset1Box, 3, 1)
        
        self.layout.addWidget(self.ch2Label, 4, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ch2Button, 4, 1)
        self.layout.addWidget(self.scale2Label, 5, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.scale2Box, 5, 1)
        self.layout.addWidget(self.offset2Label, 6, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.offset2Box, 6, 1)        
        
        self.setWindowTitle(self.name)
        self.setLayout(self.layout)
        self.setFixedSize(180, 200)
    
        self.reactor.callInThread(self.getAll)
    
    def getAll(self):
        self.getScale1()
        self.getScale2()
    
    def connectSignals(self):
        self.AFGnameLabel.clicked.connect(self.onNameLabelClick)
        
        self.scale1Box.returnPressed.connect(self.onNewScale1)
        self.ch1Button.released.connect(self.onConfigure1)
        self.scale2Box.returnPressed.connect(self.onNewScale2)
        self.ch2Button.released.connect(self.onConfigure2)
    
    def onNameLabelClick(self):
        self.reactor.callInThread(self.getAll)   
    
    def onConfigure1(self):
        self.reactor.callInThread(self.setConfigure1)
        
    def setConfigure1(self):
        self.device.stop = 1
        self.device.run = 1
    
    def onConfigure2(self):
        self.reactor.callInThread(self.setConfigure2)
        
    def setConfigure2(self):
        self.device.stop = 1
        self.device.run = 1
    
    def getScale1(self):
        scale1 = self.device.scale1
        self.reactor.callFromThread(self.displayScale1, scale1)
        
    def displayScale1(self, scale1):
        self.scale1Box.display(scale1)

    def onNewScale1(self):
        scale = self.scale1Box.value()
        self.reactor.callInThread(self.setScale1, scale)

    def setScale1(self, scale):
        self.device.scale1 = scale
        self.reactor.callFromThread(self.displayScale1, scale)
        
    def getScale2(self):
        scale2 = self.device.scale2
        self.reactor.callFromThread(self.displayScale2, scale2)
        
    def displayScale2(self, scale2):
        self.scale2Box.display(scale2)

    def onNewScale2(self):
        scale = self.scale2Box.value()
        self.reactor.callInThread(self.setScale2, scale)

    def setScale2(self, scale):
        self.device.scale2 = scale
        self.reactor.callFromThread(self.displayScale2, scale)
    
    def closeEvent(self, x):
        super(AFGControllerClient, self).closeEvent(x)
        self.reactor.callFromThread(self.reactor.stop)

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
        self.setFixedSize(200* len(self.client_list), 240)
        self.setWindowTitle(self.name)
        self.setLayout(self.layout)

    def closeEvent(self, x):
        super(MultipleClientContainer, self).closeEvent(x)
        self.reactor.callFromThread(self.reactor.stop)

if __name__ == '__main__':
    from afg2.devices.Red_AFG import RedAFGProxy

    class AFGSubClient(AFGControllerClient):
        name = 'RED AFG'
        DeviceProxy = RedAFGProxy
        

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