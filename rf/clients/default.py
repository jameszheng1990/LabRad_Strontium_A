import json
import numpy as np
import os

from PyQt5 import QtWidgets, QtCore
from twisted.internet.defer import inlineCallbacks

from client_tools.widgets import ClickableLabel, SuperSpinBox

class RFClient(QtWidgets.QGroupBox):
    name = None
    DeviceProxy = None
    updateID = np.random.randint(0, 2**31 - 1)
    amplitudeDisplayUnits = [(0, 'dBm')]
    amplitudeDigits = None
    frequencyDisplayUnits = [(-6, 'uHz'), (-3, 'mHz'), (0, 'Hz'), (3, 'kHz'), 
                             (6, 'MHz'), (9, 'GHz')]
    frequencyDigits = None
    fmfreqDisplayUnits = [(-6, 'uHz/V'), (-3, 'mHz/V'), (0, 'Hz/V'), (3, 'kHz/V'), 
                             (6, 'MHz/V'), (9, 'GHz/V')]
    fmfreqDigits = None
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
        self.fm_dev = self.device.fm_dev

    def populateGUI(self):
        self.nameLabel = ClickableLabel('<b>' + self.name + '</b>')
        self.stateButton = QtWidgets.QPushButton()
        self.stateButton.setCheckable(True)
        
        self.frequencyLabel = ClickableLabel('Frequency: ')
        self.frequencyBox = SuperSpinBox(self.device._frequency_range, 
                                          self.frequencyDisplayUnits, 
                                          self.frequencyDigits)
        self.frequencyBox.setFixedWidth(self.spinboxWidth)
        
        self.amplitudeLabel = ClickableLabel('Amplitude: ')
        self.amplitudeBox = SuperSpinBox(self.device._amplitude_range, 
                                          self.amplitudeDisplayUnits, 
                                          self.amplitudeDigits)
        self.amplitudeBox.setFixedWidth(self.spinboxWidth)
        
        self.fmstateButton = QtWidgets.QPushButton()
        self.fmfreqBox = SuperSpinBox(self.device._fmfreq_range,
                                      self.fmfreqDisplayUnits,
                                      self.fmfreqDigits)
        self.fmfreqBox.setFixedWidth(self.spinboxWidth)
        self.fmfreqBox.setReadOnly(True)
        
        self.fmstateButton.setCheckable(True)
        self.fmdevLabel = ClickableLabel('FM Dev: ')
        self.fmdevBox = QtWidgets.QDoubleSpinBox()
        self.fmdevBox.setKeyboardTracking(False)
        self.fmdevBox.setRange(*self.device._fmdev_range)
#        self.fmdevBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.fmdevBox.setDecimals(0)
        
        self.layout = QtWidgets.QGridLayout() 
        self.layout.addWidget(self.nameLabel, 0, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.stateButton, 0, 1)
        self.layout.addWidget(self.frequencyLabel, 1, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.frequencyBox, 1, 1)
        self.layout.addWidget(self.amplitudeLabel, 2, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.amplitudeBox, 2, 1)
        
        self.layout.addWidget(self.fmstateButton, 3, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.fmfreqBox, 3, 1)
        self.layout.addWidget(self.fmdevLabel, 4, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.fmdevBox, 4, 1)
        
        self.setLayout(self.layout)

        self.setWindowTitle(self.name)
        self.setFixedSize(120 + self.spinboxWidth, 180)
        
        self.connectSignals()
        self.reactor.callInThread(self.getAll)
        
    def getAll(self):
        self.getRFState()
        self.getFMState()
        self.getFrequency()
        self.getAmplitude()
        self.getFMdev()
        self.getFMfreq()
    
    def getFMdev(self):
        fm_dev = self.fm_dev
        self.reactor.callFromThread(self.displayFMdev, fm_dev)
        
    def displayFMdev(self, fm_dev):
        self.fmdevBox.setValue(fm_dev)
    
    def getFMfreq(self):
        fm_freq = 3200*2**int(self.fm_dev)
        self.reactor.callFromThread(self.displayFMfreq, fm_freq)
        
    def displayFMfreq(self, fm_freq):
        self.fmfreqBox.display(fm_freq)
    
    def getRFState(self):
        rf_state = self.device.state
        self.reactor.callFromThread(self.displayRFState, rf_state)

    def displayRFState(self, rf_state):
        if rf_state:
            self.stateButton.setChecked(1)
            self.stateButton.setText('RF ON')
        else:
            self.stateButton.setChecked(0)
            self.stateButton.setText('RF OFF')
    
    def getFMState(self):
        fm_state = self.device.fm
        self.reactor.callFromThread(self.displayFMState, fm_state)

    def displayFMState(self, fm_state):
        if fm_state:
            self.fmstateButton.setChecked(1)
            self.fmstateButton.setText('FM ON')
        else:
            self.fmstateButton.setChecked(0)
            self.fmstateButton.setText('FM OFF')
            
    def getFrequency(self):
        frequency = self.device.frequency
        self.reactor.callFromThread(self.displayFrequency, frequency)

    def displayFrequency(self, frequency):
        self.frequencyBox.display(frequency)
    
    def getAmplitude(self):
        amplitude = self.device.amplitude
        self.reactor.callFromThread(self.displayAmplitude, amplitude)

    def displayAmplitude(self, amplitude):
        self.amplitudeBox.display(amplitude)

    def connectSignals(self):
        self.nameLabel.clicked.connect(self.onNameLabelClick)
        self.frequencyLabel.clicked.connect(self.onFrequencyLabelClick)
        self.amplitudeLabel.clicked.connect(self.onAmplitudeLabelClick)
        
        self.stateButton.released.connect(self.onNewRFState)
        self.fmstateButton.released.connect(self.onNewFMState)
        
        self.frequencyBox.returnPressed.connect(self.onNewFrequency)
        self.amplitudeBox.returnPressed.connect(self.onNewAmplitude)
        
        self.fmdevBox.valueChanged.connect(self.onNewFMDev)
    
    def onNameLabelClick(self):
        self.reactor.callInThread(self.getAll)
    
    def onFrequencyLabelClick(self):
        self.reactor.callInThread(self.getFrequency)
    
    def onAmplitudeLabelClick(self):
        self.reactor.callInThread(self.getAmplitude)
    
    def onNewRFState(self):
        rf_state = self.stateButton.isChecked()
        self.reactor.callInThread(self.setRFState, rf_state)
    
    def setRFState(self, rf_state):
        self.device.state = rf_state
        self.reactor.callFromThread(self.displayRFState, rf_state)

    def onNewFMState(self):
        fm_state = self.fmstateButton.isChecked()
        self.reactor.callInThread(self.setFMState, fm_state)
    
    def setFMState(self, fm_state):
        self.device.fm = fm_state
        self.reactor.callFromThread(self.displayFMState, fm_state)
        
    def onNewFMDev(self):
        self.fm_dev = self.fmdevBox.value()
        fm_dev = self.fm_dev
        self.reactor.callInThread(self.setFMDev, fm_dev)
    
    def setFMDev(self, fm_dev):
        self.device.set_fm_dev(fm_dev)
        self.getFMdev()
        self.getFMfreq()
    
    def onNewFrequency(self):
        frequency = self.frequencyBox.value()
        self.reactor.callInThread(self.setFrequency, frequency)

    def setFrequency(self, frequency):
        self.device.frequency = frequency
        self.reactor.callFromThread(self.displayFrequency, frequency)
    
    def onNewAmplitude(self):
        amplitude = self.amplitudeBox.value()
        self.reactor.callInThread(self.setAmplitude, amplitude)

    def setAmplitude(self, amplitude):
        self.device.amplitude = amplitude
        self.reactor.callFromThread(self.displayAmplitude, amplitude)
    
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
        state = update.get('state')
        if state is not None:
            self.displayState(state)
        frequency = update.get('frequency')
        if frequency is not None:
            self.displayFrequency(frequency)
        amplitude = update.get('amplitude')
        if amplitude is not None:
            self.displayAmplitude(amplitude)
    
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
        self.setFixedSize(240 * len(self.client_list), 220)
        self.setWindowTitle(self.name)
        self.setLayout(self.layout)

    def closeEvent(self, x):
        super(MultipleClientContainer, self).closeEvent(x)
        self.reactor.stop()

if __name__ == '__main__':
    from rf.devices.dim3000reda import DIM3000REDAProxy
    from rf.devices.dim3000blue2 import DIM3000BLUE2Proxy

    class DIM3000REDAClient(RFClient):
        name = 'RED_A'
        DeviceProxy = DIM3000REDAProxy
        
        frequencyDigits = 6
        amplitudeDigits = 2
        fmfreqDigits = 1
        
    class DIM3000BLUE2Client(RFClient):
        name = 'BLUE_2'
        DeviceProxy = DIM3000BLUE2Proxy
        
        frequencyDigits = 6
        amplitudeDigits = 2
        fmfreqDigits = 1
    
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    from client_tools import qt5reactor 
    qt5reactor.install()
    from twisted.internet import reactor

    widgets = [
            DIM3000REDAClient(reactor),
            DIM3000BLUE2Client(reactor),
            ]
    
    widget = MultipleClientContainer(widgets, reactor)
    widget.show()
    reactor.suggestThreadPoolSize(30)
    reactor.run()
