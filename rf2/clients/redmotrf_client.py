import json
import numpy as np
import os

from PyQt5 import QtWidgets, QtCore
from twisted.internet.defer import inlineCallbacks

from client_tools.widgets import ClickableLabel, SuperSpinBox

class RedMOTRFClient(QtWidgets.QGroupBox):
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
    spinboxWidth = 120
    
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
        self.stateButton = QtWidgets.QPushButton()
        self.stateButton.setCheckable(True)
        
        self.beatnoteLabel = ClickableLabel('Beatnote Freq: ')
        self.beatnoteBox = SuperSpinBox(self.device._frequency_range, 
                                          self.frequencyDisplayUnits, 
                                          self.frequencyDigits)
        self.beatnoteBox.setFixedWidth(self.spinboxWidth)
        
        self.isotopeLabel = ClickableLabel('Choose isotope: ')
        self.isotopeBox = QtWidgets.QComboBox()
        isotope = 'Sr-88'
        isotope_list = ['Sr-87, F=11/2', 'Sr-87, F=9/2', 'Sr-86', 'Sr-84']
        
        self.isotopeBox.addItem(isotope)
        self.isotopeBox.addItems(isotope_list)
        
        self.transitionfreqLabel = ClickableLabel('1S0-3P1 freq: ')
        self.transitionfreqBox = QtWidgets.QDoubleSpinBox()
        self.transitionfreqBox.setRange(0, 3e9)
        self.transitionfreqBox.setReadOnly(True)
        self.transitionfreqBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.transitionfreqBox.setDecimals(2)
        self.transitionfreqBox.setGroupSeparatorShown(True)
        self.transitionfreqBox.setSuffix(' MHz')
        
        self.redafreqLabel = ClickableLabel('Red-A freq: ')
        self.redafreqBox = QtWidgets.QDoubleSpinBox()
        self.redafreqBox.setRange(0, 3e9)
        self.redafreqBox.setReadOnly(True)
        self.redafreqBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.redafreqBox.setDecimals(2)
        self.transitionfreqBox.setGroupSeparatorShown(True)
        self.transitionfreqBox.setSuffix(' MHz')
        
        self.layout = QtWidgets.QGridLayout() 
        self.layout.addWidget(self.nameLabel, 0, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.stateButton, 0, 1)
        
        self.layout.addWidget(self.beatnoteLabel, 1, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.beatnoteBox, 1, 1)
        
        self.layout.addWidget(self.isotopeLabel, 2, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.isotopeBox, 2, 1)
        
        self.layout.addWidget(self.transitionfreqLabel, 3, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.transitionfreqBox, 3, 1)        

        self.layout.addWidget(self.redafreqLabel, 4, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.redafreqBox, 4, 1)   
        
        self.setLayout(self.layout)

        self.setWindowTitle(self.name)
        self.setFixedSize(120 + self.spinboxWidth, 180)
        
        self.connectSignals()
        self.reactor.callInThread(self.getAll)
        
    def getAll(self):
        self.getBeatnote()
        self.getTransitionFreq()
    
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
    
    def getBeatnote(self):
        frequency = self.device.freq1
        self.reactor.callFromThread(self.displayBeatnote, frequency)

    def displayBeatnote(self, frequency):
        self.beatnoteBox.display(frequency)
    
    def connectSignals(self):
        self.nameLabel.clicked.connect(self.onNameLabelClick)
        self.beatnoteLabel.clicked.connect(self.onBeatnoteLabelClick)
        
        self.stateButton.released.connect(self.onNewRFState)
        self.beatnoteBox.returnPressed.connect(self.onNewBeatnote)
        
        self.isotopeBox.currentIndexChanged.connect(self.onIsotopeBoxChange)
    
    def onIsotopeBoxChange(self):
        self.reactor.callInThread(self.getTransitionFreq)
    
    def getTransitionFreq(self):
        index = self.isotopeBox.currentIndex()
        self.reactor.callFromThread(self.displayTransitionFreq, index)
    
    def displayTransitionFreq(self, index):
        sr_88 = 434829121.300
        sr_87_F11_2 = 434827879.860
        sr_87_F9_2 = 434829343.010
        if index == 0:
            self.transitionfreqBox.setValue(sr_88)
        elif index == 1:
            self.transitionfreqBox.setValue(sr_87_F11_2)
        elif index == 2:
            self.transitionfreqBox.setValue(sr_87_F9_2)
    
    def onNameLabelClick(self):
        self.reactor.callInThread(self.getAll)
    
    def onBeatnoteLabelClick(self):
        self.reactor.callInThread(self.getBeatnote)
    
    def onNewRFState(self):
        rf_state = self.stateButton.isChecked()
        self.reactor.callInThread(self.setRFState, rf_state)
    
    def setRFState(self, rf_state):
        self.device.state = rf_state
        self.reactor.callFromThread(self.displayRFState, rf_state)

    def onNewBeatnote(self):
        frequency = self.beatnoteBox.value()
        self.reactor.callInThread(self.setBeatnote, frequency)

    def setBeatnote(self, frequency):
        self.device.freq1 = frequency
        self.reactor.callFromThread(self.displayBeatnote, frequency)
    
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
    from rf2.devices.beatnotesg import BEATNOTESGProxy

    class BeatnoteSGClient(RedMOTRFClient):
        name = 'Red-B beatnote'
        DeviceProxy = BEATNOTESGProxy
        
        frequencyDigits = 3
        amplitudeDigits = 2
    
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    from client_tools import qt5reactor 
    qt5reactor.install()
    from twisted.internet import reactor

    widget = BeatnoteSGClient(reactor)
            
    widget.show()
    reactor.suggestThreadPoolSize(30)
    reactor.run()
