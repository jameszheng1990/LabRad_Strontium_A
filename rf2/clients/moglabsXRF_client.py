import json
import numpy as np
import os

from PyQt5 import QtWidgets, QtCore
from twisted.internet.defer import inlineCallbacks

from client_tools.widgets import ClickableLabel, SuperSpinBox

class MoglabsXRF_RFClient(QtWidgets.QGroupBox):
    name = None
    DeviceProxy = None
    updateID = np.random.randint(0, 2**31 - 1)
    amplitudeDisplayUnits = [(0, 'dBm')]
    amplitudeDigits = None
    frequencyDisplayUnits = [(-6, 'uHz'), (-3, 'mHz'), (0, 'Hz'), (3, 'kHz'), 
                             (6, 'MHz'), (9, 'GHz')]
    frequencyDigits = None
    fmgainDisplayUnits = [  (6, 'MHz/V')]
    fmgainDigits = None
    amgainDisplayUnits = [(0, '%')]
    amgainDigits = None
    
    spinboxWidth = 100
    
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
        # self.fm_dev1 = self.device.fm_dev1

    def populateGUI(self):
        self.nameLabel = ClickableLabel('<b>' + self.name + '</b>')
        
        self.channelLabel1 =  ClickableLabel('<b>' + 'CH 1' + '</b>')
        self.stateButton1 = QtWidgets.QPushButton()
        self.stateButton1.setCheckable(True)
        
        self.frequencyLabel1 = ClickableLabel('Frequency: ')
        self.frequencyBox1 = SuperSpinBox(self.device._frequency_range, 
                                          self.frequencyDisplayUnits, 
                                          self.frequencyDigits)
        self.frequencyBox1.setFixedWidth(self.spinboxWidth)
        
        self.amplitudeLabel1 = ClickableLabel('Amplitude: ')
        self.amplitudeBox1 = SuperSpinBox(self.device._amplitude_range, 
                                          self.amplitudeDisplayUnits, 
                                          self.amplitudeDigits)
        self.amplitudeBox1.setFixedWidth(self.spinboxWidth)
        
        #############
        
        self.channelLabel2 =  ClickableLabel('<b>' + 'CH 2' + '</b>')
        self.stateButton2 = QtWidgets.QPushButton()
        self.stateButton2.setCheckable(True)
        
        self.frequencyLabel2 = ClickableLabel('Frequency: ')
        self.frequencyBox2 = SuperSpinBox(self.device._frequency_range, 
                                          self.frequencyDisplayUnits, 
                                          self.frequencyDigits)
        self.frequencyBox2.setFixedWidth(self.spinboxWidth)
        
        self.amplitudeLabel2 = ClickableLabel('Amplitude: ')
        self.amplitudeBox2 = SuperSpinBox(self.device._amplitude_range, 
                                          self.amplitudeDisplayUnits, 
                                          self.amplitudeDigits)
        self.amplitudeBox2.setFixedWidth(self.spinboxWidth)
        
        ##############
        
        self.layout = QtWidgets.QGridLayout() 
        self.layout.addWidget(self.nameLabel, 0, 0, 1, 2,
                              QtCore.Qt.AlignHCenter)
        
        self.layout.addWidget(self.channelLabel1, 1, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.stateButton1, 1, 1)
        self.layout.addWidget(self.frequencyLabel1, 2, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.frequencyBox1, 2, 1)
        self.layout.addWidget(self.amplitudeLabel1, 3, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.amplitudeBox1, 3, 1)
        
        self.layout.addWidget(self.channelLabel2, 4, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.stateButton2, 4, 1)
        self.layout.addWidget(self.frequencyLabel2, 5, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.frequencyBox2, 5, 1)
        self.layout.addWidget(self.amplitudeLabel2, 6, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.amplitudeBox2, 6, 1)
        
        self.setLayout(self.layout)

        self.setWindowTitle(self.name)
        self.setFixedSize(120 + self.spinboxWidth, 250)
        
        self.connectSignals()
        self.reactor.callInThread(self.getAll)
        
    def getAll(self):
        self.getRFState1()
        self.getFrequency1()
        self.getAmplitude1()
        
        self.getRFState2()
        self.getFrequency2()
        self.getAmplitude2()
    
    def getRFState1(self):
        rf_state1 = self.device.rf_state1
        self.reactor.callFromThread(self.displayRFState1, rf_state1)

    def displayRFState1(self, rf_state1):
        if rf_state1:
            self.stateButton1.setChecked(1)
            self.stateButton1.setText('RF ON')
        else:
            self.stateButton1.setChecked(0)
            self.stateButton1.setText('RF OFF')

    def getFrequency1(self):
        frequency1 = self.device.frequency1
        self.reactor.callFromThread(self.displayFrequency1, frequency1)

    def displayFrequency1(self, frequency1):
        self.frequencyBox1.display(frequency1)
    
    def getAmplitude1(self):
        amplitude1 = self.device.amplitude1
        self.reactor.callFromThread(self.displayAmplitude1, amplitude1)

    def displayAmplitude1(self, amplitude1):
        self.amplitudeBox1.display(amplitude1)
    
    def getRFState2(self):
        rf_state2 = self.device.rf_state2
        self.reactor.callFromThread(self.displayRFState2, rf_state2)

    def displayRFState2(self, rf_state2):
        if rf_state2:
            self.stateButton2.setChecked(1)
            self.stateButton2.setText('RF ON')
        else:
            self.stateButton2.setChecked(0)
            self.stateButton2.setText('RF OFF')
    
    def getFrequency2(self):
        frequency2 = self.device.frequency2
        self.reactor.callFromThread(self.displayFrequency2, frequency2)

    def displayFrequency2(self, frequency2):
        self.frequencyBox2.display(frequency2)
    
    def getAmplitude2(self):
        amplitude2 = self.device.amplitude2
        self.reactor.callFromThread(self.displayAmplitude2, amplitude2)

    def displayAmplitude2(self, amplitude2):
        self.amplitudeBox2.display(amplitude2)
        
    def connectSignals(self):
        self.nameLabel.clicked.connect(self.onNameLabelClick)
        
        self.frequencyLabel1.clicked.connect(self.onFrequencyLabelClick1)
        self.amplitudeLabel1.clicked.connect(self.onAmplitudeLabelClick1)
        
        self.stateButton1.released.connect(self.onNewRFState1)
        self.frequencyBox1.returnPressed.connect(self.onNewFrequency1)
        self.amplitudeBox1.returnPressed.connect(self.onNewAmplitude1)
        
        self.frequencyLabel2.clicked.connect(self.onFrequencyLabelClick2)
        self.amplitudeLabel2.clicked.connect(self.onAmplitudeLabelClick2)
        
        self.stateButton2.released.connect(self.onNewRFState2)
        self.frequencyBox2.returnPressed.connect(self.onNewFrequency2)
        self.amplitudeBox2.returnPressed.connect(self.onNewAmplitude2)
    
    def onNameLabelClick(self):
        self.reactor.callInThread(self.getAll)
    
    def onFrequencyLabelClick1(self):
        self.reactor.callInThread(self.getFrequency1)
    
    def onAmplitudeLabelClick1(self):
        self.reactor.callInThread(self.getAmplitude1)
    
    def onNewRFState1(self):
        rf_state1 = self.stateButton1.isChecked()
        self.reactor.callInThread(self.setRFState1, rf_state1)
    
    def setRFState1(self, rf_state1):
        self.device.rf_state1 = rf_state1
        self.reactor.callFromThread(self.displayRFState1, rf_state1)

    def onNewFrequency1(self):
        frequency1 = self.frequencyBox1.value()
        self.reactor.callInThread(self.setFrequency1, frequency1)

    def setFrequency1(self, frequency1):
        self.device.frequency1 = frequency1
        self.reactor.callFromThread(self.displayFrequency1, frequency1)
    
    def onNewAmplitude1(self):
        amplitude1 = self.amplitudeBox1.value()
        self.reactor.callInThread(self.setAmplitude1, amplitude1)

    def setAmplitude1(self, amplitude1):
        self.device.amplitude1 = amplitude1
        self.reactor.callFromThread(self.displayAmplitude1, amplitude1)
    
    ######################
    
    def onFrequencyLabelClick2(self):
        self.reactor.callInThread(self.getFrequency2)
    
    def onAmplitudeLabelClick2(self):
        self.reactor.callInThread(self.getAmplitude2)
    
    def onNewRFState2(self):
        rf_state2 = self.stateButton2.isChecked()
        self.reactor.callInThread(self.setRFState2, rf_state2)
    
    def setRFState2(self, rf_state2):
        self.device.rf_state2 = rf_state2
        self.reactor.callFromThread(self.displayRFState2, rf_state2)

    def onNewFrequency2(self):
        frequency2 = self.frequencyBox2.value()
        self.reactor.callInThread(self.setFrequency2, frequency2)

    def setFrequency2(self, frequency2):
        self.device.frequency2 = frequency2
        self.reactor.callFromThread(self.displayFrequency2, frequency2)
    
    def onNewAmplitude2(self):
        amplitude2 = self.amplitudeBox2.value()
        self.reactor.callInThread(self.setAmplitude2, amplitude2)

    def setAmplitude2(self, amplitude2):
        self.device.amplitude2 = amplitude2
        self.reactor.callFromThread(self.displayAmplitude2, amplitude2)
        
    @inlineCallbacks
    def connectLabrad(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name=self.name, host=os.getenv('LABRADHOST'), password='')
        yield self.cxn.update.signal__signal(self.updateID)
        yield self.cxn.update.addListener(listener=self.receiveUpdate, source=None, 
                                          ID=self.updateID)
        yield self.cxn.update.register(self.name)
    
    def receiveUpdate(self, c, updateJson):
        # to be updated
        update = json.loads(updateJson)
        
        state1 = update.get('state1')
        if state1 is not None:
            self.displayState1(state1)
        frequency1 = update.get('frequency1')
        if frequency1 is not None:
            self.displayFrequency1(frequency1)
        amplitude1 = update.get('amplitude1')
        if amplitude1 is not None:
            self.displayAmplitude1(amplitude1)
            
        state2 = update.get('state2')
        if state2 is not None:
            self.displayState2(state2)
        frequency2 = update.get('frequency2')
        if frequency2 is not None:
            self.displayFrequency2(frequency2)
        amplitude2 = update.get('amplitude2')
        if amplitude2 is not None:
            self.displayAmplitude2(amplitude2)
    
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
        self.setFixedSize(240 * len(self.client_list), 270)
        self.setWindowTitle(self.name)
        self.setLayout(self.layout)

    def closeEvent(self, x):
        super(MultipleClientContainer, self).closeEvent(x)
        self.reactor.stop()

if __name__ == '__main__':
    from rf2.devices.moglabs_XRF import MoglabsXRFProxy

    class MoglabsXRFClient(MoglabsXRF_RFClient):
        name = 'Moglabs_XRF'
        DeviceProxy = MoglabsXRFProxy
        
        frequencyDigits = 6
        amplitudeDigits = 2
        fmgainDigits = 1
        amgainDigits = 1
    
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    from client_tools import qt5reactor 
    qt5reactor.install()
    from twisted.internet import reactor

    widgets = [
            MoglabsXRFClient(reactor),
            ]
    
    widget = MultipleClientContainer(widgets, reactor)
    widget.show()
    reactor.suggestThreadPoolSize(30)
    reactor.run()
