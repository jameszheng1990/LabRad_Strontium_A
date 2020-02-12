import json, time
import numpy as np
import os

from PyQt5 import QtWidgets, QtCore
from twisted.internet.defer import inlineCallbacks

from client_tools.widgets import ClickableLabel, SuperSpinBox

class Repump_RFClient(QtWidgets.QGroupBox):
    name = None
    DeviceProxy = None
    updateID = np.random.randint(0, 2**31 - 1)
    
    frequencyDisplayUnits = [(0, 'Hz')]
    frequencyDigits = None

    voltageDisplayUnits = [(-3, 'mV'), (0, 'V')]
    voltageDigits = None

    state = None
    
    spinboxWidth = 80
    
    def __init__(self, reactor, cxn=None):
        QtWidgets.QDialog.__init__(self)
        self.reactor = reactor
        reactor.callInThread(self.initialize)
        self.connectLabrad()
    
    def initialize(self):
        import labrad
        cxn = labrad.connect(name=self.name, host=os.getenv('LABRADHOST') , password = '')
        self.device = self.DeviceProxy(cxn)
        self.reactor.callFromThread(self.populateGUI)

    def populateGUI(self):
        self.nameLabel = ClickableLabel('<b>' + self.name + '</b>')
        
        self.shape1Label = ClickableLabel('679 nm :')
        
        self.shape1Button = QtWidgets.QPushButton()
        self.shape1Button.setCheckable(True)
        
        self.dc1Label = ClickableLabel('DC 1 Voltage: ')
        self.dc1Box = SuperSpinBox(self.device._dc_v_range,
                                   self.voltageDisplayUnits, 
                                   self.voltageDigits)
        self.dc1Box.setFixedWidth(self.spinboxWidth)
        
        self.ramp1Label = ClickableLabel('Ramp 1 Freq : ')
        self.ramp1AmpLabel = ClickableLabel('Ramp 1 Amp :')
        self.ramp1OffsetLabel = ClickableLabel('Ramp 1 Offset :')
        
        self.ramp1FreqBox = SuperSpinBox(self.device._ramp_freq_range,
                                   self.frequencyDisplayUnits, 
                                   self.frequencyDigits)
        self.ramp1FreqBox.setFixedWidth(self.spinboxWidth)
        
        self.ramp1AmpBox = SuperSpinBox(self.device._dc_v_range,
                                   self.voltageDisplayUnits, 
                                   self.voltageDigits)
        self.ramp1AmpBox.setFixedWidth(self.spinboxWidth)
        
        self.ramp1OffsetBox = SuperSpinBox(self.device._dc_v_range,
                                   self.voltageDisplayUnits, 
                                   self.voltageDigits)
        self.ramp1OffsetBox.setFixedWidth(self.spinboxWidth)

        self.shape2Label = ClickableLabel('707 nm :')
        
        self.shape2Button = QtWidgets.QPushButton()
        self.shape2Button.setCheckable(True)
        
        self.dc2Label = ClickableLabel('DC 2 Voltage: ')
        self.dc2Box = SuperSpinBox(self.device._dc_v_range,
                                   self.voltageDisplayUnits, 
                                   self.voltageDigits)
        self.dc2Box.setFixedWidth(self.spinboxWidth)
        
        self.ramp2Label = ClickableLabel('Ramp 2 Freq : ')
        self.ramp2AmpLabel = ClickableLabel('Ramp 2 Amp :')
        self.ramp2OffsetLabel = ClickableLabel('Ramp 2 Offset :')
        
        self.ramp2FreqBox = SuperSpinBox(self.device._ramp_freq_range,
                                   self.frequencyDisplayUnits, 
                                   self.frequencyDigits)
        self.ramp2FreqBox.setFixedWidth(self.spinboxWidth)
        
        self.ramp2AmpBox = SuperSpinBox(self.device._dc_v_range,
                                   self.voltageDisplayUnits, 
                                   self.voltageDigits)
        self.ramp2AmpBox.setFixedWidth(self.spinboxWidth)
        
        self.ramp2OffsetBox = SuperSpinBox(self.device._dc_v_range,
                                   self.voltageDisplayUnits, 
                                   self.voltageDigits)
        self.ramp2OffsetBox.setFixedWidth(self.spinboxWidth)
        
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.nameLabel, 0, 0, 1, 2, 
                              QtCore.Qt.AlignCenter)
        
        self.layout.addWidget(self.shape1Label, 1, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.shape1Button, 1, 1)
        
        self.layout.addWidget(self.dc1Label, 2, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.dc1Box, 2, 1)
        
        self.layout.addWidget(self.ramp1Label, 3, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ramp1FreqBox, 3, 1)
        
        self.layout.addWidget(self.ramp1AmpLabel, 4, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ramp1AmpBox, 4, 1)
        self.layout.addWidget(self.ramp1OffsetLabel, 5, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ramp1OffsetBox, 5, 1)
        
        self.layout.addWidget(self.shape2Label, 6, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.shape2Button, 6, 1)
        
        self.layout.addWidget(self.dc2Label, 7, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.dc2Box, 7, 1)
        
        self.layout.addWidget(self.ramp2Label, 8, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ramp2FreqBox, 8, 1)
        
        self.layout.addWidget(self.ramp2AmpLabel, 9, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ramp2AmpBox, 9, 1)
        self.layout.addWidget(self.ramp2OffsetLabel, 10, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.ramp2OffsetBox, 10, 1)
        
        self.setLayout(self.layout)

        self.setWindowTitle(self.name)
        self.setFixedSize(120 + self.spinboxWidth, 300)
        
        self.connectSignals()
        self.reactor.callInThread(self.getAll)

    def getAll(self):
        self.getShape1()
        self.getShape2()
    
    def onShape1Button(self):
        shape1 = self.shape1Button.isChecked()
        self.reactor.callInThread(self.setShape1, shape1)
        
    def setShape1(self, shape1):
        self.device.shape1 = shape1
        self.reactor.callFromThread(self.displayShape1, shape1) 
        
    def getShape1(self):
        shape1 = self.device.shape1
        self.reactor.callFromThread(self.displayShape1, shape1)
            
    def displayShape1(self, shape1):
        if shape1:
            self.shape1Button.setChecked(1)
            self.shape1Button.setText('DC')
            self.DC1Enable(True)
            self.Ramp1Enable(False)
            self.reactor.callInThread(self.getDC1)
        else:
            self.shape1Button.setChecked(0)
            self.shape1Button.setText('Ramp')
            self.DC1Enable(False)
            self.Ramp1Enable(True)
            self.reactor.callInThread(self.getRamp1)
    
    def DC1Enable(self, boolean):
        if boolean:
            self.dc1Box.setEnabled(True)
        else:
            self.dc1Box.setDisabled(True)
    
    def Ramp1Enable(self, boolean):
        if boolean:
            self.ramp1FreqBox.setEnabled(True)
            self.ramp1AmpBox.setEnabled(True)
            self.ramp1OffsetBox.setEnabled(True)
        else:
            self.ramp1FreqBox.setDisabled(True)
            self.ramp1AmpBox.setDisabled(True)
            self.ramp1OffsetBox.setDisabled(True)

    def onShape2Button(self):
        shape2 = self.shape2Button.isChecked()
        self.reactor.callInThread(self.setShape2, shape2)
        
    def setShape2(self, shape2):
        self.device.shape2 = shape2
        self.reactor.callFromThread(self.displayShape2, shape2) 
        
    def getShape2(self):
        shape2 = self.device.shape2
        self.reactor.callFromThread(self.displayShape2, shape2)
            
    def displayShape2(self, shape2):
        if shape2:
            self.shape2Button.setChecked(1)
            self.shape2Button.setText('DC')
            self.DC2Enable(True)
            self.Ramp2Enable(False)
            self.reactor.callInThread(self.getDC2)
        else:
            self.shape2Button.setChecked(0)
            self.shape2Button.setText('Ramp')
            self.DC2Enable(False)
            self.Ramp2Enable(True)
            self.reactor.callInThread(self.getRamp2)
    
    def DC2Enable(self, boolean):
        if boolean:
            self.dc2Box.setEnabled(True)
        else:
            self.dc2Box.setDisabled(True)
    
    def Ramp2Enable(self, boolean):
        if boolean:
            self.ramp2FreqBox.setEnabled(True)
            self.ramp2AmpBox.setEnabled(True)
            self.ramp2OffsetBox.setEnabled(True)
        else:
            self.ramp2FreqBox.setDisabled(True)
            self.ramp2AmpBox.setDisabled(True)
            self.ramp2OffsetBox.setDisabled(True)
            
    def connectSignals(self):
        self.nameLabel.clicked.connect(self.onNameLabelClick)
        
        self.shape1Button.released.connect(self.onShape1Button)
        self.shape2Button.released.connect(self.onShape2Button)
        
        self.dc1Box.returnPressed.connect(self.onNewDC1)
        self.dc2Box.returnPressed.connect(self.onNewDC2)
        
        self.ramp1FreqBox.returnPressed.connect(self.onNewRamp1)
        self.ramp1AmpBox.returnPressed.connect(self.onNewRamp1)
        self.ramp1OffsetBox.returnPressed.connect(self.onNewRamp1)
        
        self.ramp2FreqBox.returnPressed.connect(self.onNewRamp2)
        self.ramp2AmpBox.returnPressed.connect(self.onNewRamp2)
        self.ramp2OffsetBox.returnPressed.connect(self.onNewRamp2)
    
    def onNameLabelClick(self):
        self.reactor.callInThread(self.getAll)
        
    def onNewDC1(self):
        dc1 = self.dc1Box.value()
        self.reactor.callInThread(self.setDC1, dc1)
     
    def setDC1(self, dc1):
        self.device.dc1 = dc1
        self.reactor.callFromThread(self.displayDC1, dc1)
        
    def getDC1(self):
        dc1 = self.device.dc1
        self.reactor.callFromThread(self.displayDC1, dc1)
        
    def displayDC1(self, dc1):
        self.dc1Box.display(dc1)
        
    def onNewRamp1(self):
        freq1 = self.ramp1FreqBox.value()
        amp1 = self.ramp1AmpBox.value()
        offset1 = self.ramp1OffsetBox.value()
        self.reactor.callInThread(self.setRamp1, freq1, amp1, offset1)
    
    def setRamp1(self, freq1, amp1, offset1):
        self.device.ramp1 = (freq1, amp1, offset1)
        self.reactor.callFromThread(self.displayRamp1, freq1, amp1, offset1)

    def getRamp1(self):
        freq1 = self.device.ramp1[0]
        amp1 = self.device.ramp1[1]
        offset1 = self.device.ramp1[2]
        self.reactor.callFromThread(self.displayRamp1, freq1, amp1, offset1)
        
    def displayRamp1(self, freq1, amp1, offset1):
        self.ramp1FreqBox.display(freq1)
        self.ramp1AmpBox.display(amp1)
        self.ramp1OffsetBox.display(offset1)
        
    def onNewDC2(self):
        dc2 = self.dc2Box.value()
        self.reactor.callInThread(self.setDC2, dc2)
     
    def setDC2(self, dc2):
        self.device.dc2 = dc2
        self.reactor.callFromThread(self.displayDC2, dc2)
        
    def getDC2(self):
        dc2 = self.device.dc2
        self.reactor.callFromThread(self.displayDC2, dc2)
        
    def displayDC2(self, dc2):
        self.dc2Box.display(dc2)
        
    def onNewRamp2(self):
        freq2 = self.ramp2FreqBox.value()
        amp2 = self.ramp2AmpBox.value()
        offset2 = self.ramp2OffsetBox.value()
        self.reactor.callInThread(self.setRamp2, freq2, amp2, offset2)
    
    def setRamp2(self, freq2, amp2, offset2):
        self.device.ramp2 = (freq2, amp2, offset2)
        self.reactor.callFromThread(self.displayRamp2, freq2, amp2, offset2)

    def getRamp2(self):
        freq2 = self.device.ramp2[0]
        amp2 = self.device.ramp2[1]
        offset2 = self.device.ramp2[2]
        self.reactor.callFromThread(self.displayRamp2, freq2, amp2, offset2)
        
    def displayRamp2(self, freq2, amp2, offset2):
        self.ramp2FreqBox.display(freq2)
        self.ramp2AmpBox.display(amp2)
        self.ramp2OffsetBox.display(offset2)
        
    @inlineCallbacks
    def connectLabrad(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name=self.name, host=os.getenv('LABRADHOST'), password='')
        yield self.cxn.update.signal__signal(self.updateID)
        yield self.cxn.update.addListener(listener=self.receiveUpdate, source=None, 
                                          ID=self.updateID)
        yield self.cxn.update.register(self.name)
    
    def receiveUpdate(self, c, updateJson):
        pass
        # update = json.loads(updateJson)
        
        # frequency = update.get('frequency')
        # if frequency is not None:
        #     self.displayFrequency(frequency)
    
    def closeEvent(self, x):
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
        self.setFixedSize(240 * len(self.client_list), 340)
        self.setWindowTitle(self.name)
        self.setLayout(self.layout)

    def closeEvent(self, x):
        super(MultipleClientContainer, self).closeEvent(x)
        self.reactor.stop()

if __name__ == '__main__':
    from rf2.devices.rigol_repumps import RepumpSGProxy

    class RepumpSGClient(Repump_RFClient):
        name = 'Repumps RF'
        DeviceProxy = RepumpSGProxy
        
        frequencyDigits = 1
        voltageDigits = 2
            
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    from client_tools import qt5reactor 
    qt5reactor.install()
    from twisted.internet import reactor

    widgets = [
            RepumpSGClient(reactor),
            ]
    
    widget = MultipleClientContainer(widgets, reactor)
    widget.show()
    reactor.suggestThreadPoolSize(20)
    reactor.run()
