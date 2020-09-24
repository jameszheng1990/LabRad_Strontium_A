import json
import numpy as np
import os

from PyQt5 import QtWidgets, QtCore
from twisted.internet.defer import inlineCallbacks

from client_tools.widgets import ClickableLabel, SuperSpinBox

class MoglabsARF_RFClient(QtWidgets.QGroupBox):
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
        
        self.fmstateButton1 = QtWidgets.QPushButton()
        self.fmstateButton1.setCheckable(True)
        self.fmgainBox1 = SuperSpinBox(self.device._fmgain_range,
                                      self.fmgainDisplayUnits,
                                      self.fmgainDigits)
        self.fmgainBox1.setFixedWidth(self.spinboxWidth)
        
        self.amstateButton1 = QtWidgets.QPushButton()
        self.amstateButton1.setCheckable(True)
        self.amgainBox1 = SuperSpinBox(self.device._amgain_range,
                                      self.amgainDisplayUnits,
                                      self.amgainDigits)
        self.amgainBox1.setFixedWidth(self.spinboxWidth)
        
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
        
        self.fmstateButton2 = QtWidgets.QPushButton()
        self.fmstateButton2.setCheckable(True)
        self.fmgainBox2 = SuperSpinBox(self.device._fmgain_range,
                                      self.fmgainDisplayUnits,
                                      self.fmgainDigits)
        self.fmgainBox2.setFixedWidth(self.spinboxWidth)
        
        self.amstateButton2 = QtWidgets.QPushButton()
        self.amstateButton2.setCheckable(True)
        self.amgainBox2 = SuperSpinBox(self.device._amgain_range,
                                      self.amgainDisplayUnits,
                                      self.amgainDigits)
        self.amgainBox2.setFixedWidth(self.spinboxWidth)
        
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
        
        self.layout.addWidget(self.fmstateButton1, 4, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.fmgainBox1, 4, 1)        
        self.layout.addWidget(self.amstateButton1, 5, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.amgainBox1, 5, 1)
        
        self.layout.addWidget(self.channelLabel2, 6, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.stateButton2, 6, 1)
        self.layout.addWidget(self.frequencyLabel2, 7, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.frequencyBox2, 7, 1)
        self.layout.addWidget(self.amplitudeLabel2, 8, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.amplitudeBox2, 8, 1)
        
        self.layout.addWidget(self.fmstateButton2, 9, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.fmgainBox2, 9, 1)
        self.layout.addWidget(self.amstateButton2, 10, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.amgainBox2, 10, 1)
        
        self.setLayout(self.layout)

        self.setWindowTitle(self.name)
        self.setFixedSize(120 + self.spinboxWidth, 320)
        
        self.connectSignals()
        self.reactor.callInThread(self.getAll)
        
    def getAll(self):
        self.getRFState1()
        self.getFrequency1()
        self.getAmplitude1()
        self.getFMState1()
        self.getFMgain1()
        self.getAMState1()
        self.getAMgain1()
        
        self.getRFState2()
        self.getFrequency2()
        self.getAmplitude2()
        self.getFMState2()
        self.getFMgain2()
        self.getAMState2()
        self.getAMgain2()
    
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

    def getFMState1(self):
        fm_state1 = self.device.fm_state1
        self.reactor.callFromThread(self.displayFMState1, fm_state1)

    def displayFMState1(self, fm_state1):
        if fm_state1:
            self.fmstateButton1.setChecked(1)
            self.fmstateButton1.setText('FM ON')
        else:
            self.fmstateButton1.setChecked(0)
            self.fmstateButton1.setText('FM OFF')
            
    def getFMgain1(self):
        fm_gain1 = self.device.fm_gain1
        self.reactor.callFromThread(self.displayFMgain1, fm_gain1)
        
    def displayFMgain1(self, fm_gain1):
        self.fmgainBox1.display(fm_gain1)
        
    def getAMState1(self):
        am_state1 = self.device.am_state1
        self.reactor.callFromThread(self.displayAMState1, am_state1)

    def displayAMState1(self, am_state1):
        if am_state1:
            self.amstateButton1.setChecked(1)
            self.amstateButton1.setText('AM ON')
        else:
            self.amstateButton1.setChecked(0)
            self.amstateButton1.setText('AM OFF')
            
    def getAMgain1(self):
        am_gain1 = self.device.am_gain1
        self.reactor.callFromThread(self.displayAMgain1, am_gain1)
        
    def displayAMgain1(self, am_gain1):
        self.amgainBox1.display(am_gain1)

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
    
    def getFMState2(self):
        fm_state2 = self.device.fm_state2
        self.reactor.callFromThread(self.displayFMState2, fm_state2)

    def displayFMState2(self, fm_state2):
        if fm_state2:
            self.fmstateButton2.setChecked(1)
            self.fmstateButton2.setText('FM ON')
        else:
            self.fmstateButton2.setChecked(0)
            self.fmstateButton2.setText('FM OFF')
            
    def getFMgain2(self):
        fm_gain2 = self.device.fm_gain2
        self.reactor.callFromThread(self.displayFMgain2, fm_gain2)
        
    def displayFMgain2(self, fm_gain2):
        self.fmgainBox2.display(fm_gain2)

    def getAMState2(self):
        am_state2 = self.device.am_state2
        self.reactor.callFromThread(self.displayAMState2, am_state2)

    def displayAMState2(self, am_state2):
        if am_state2:
            self.amstateButton2.setChecked(1)
            self.amstateButton2.setText('AM ON')
        else:
            self.amstateButton2.setChecked(0)
            self.amstateButton2.setText('AM OFF')
            
    def getAMgain2(self):
        am_gain2 = self.device.am_gain2
        self.reactor.callFromThread(self.displayAMgain2, am_gain2)
        
    def displayAMgain2(self, am_gain2):
        self.amgainBox2.display(am_gain2)

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
        self.fmstateButton1.released.connect(self.onNewFMState1)
        self.amstateButton1.released.connect(self.onNewAMState1)
        self.frequencyBox1.returnPressed.connect(self.onNewFrequency1)
        self.amplitudeBox1.returnPressed.connect(self.onNewAmplitude1)
        self.fmgainBox1.returnPressed.connect(self.onNewFMGain1)
        self.amgainBox1.returnPressed.connect(self.onNewAMGain1)
        
        self.frequencyLabel2.clicked.connect(self.onFrequencyLabelClick2)
        self.amplitudeLabel2.clicked.connect(self.onAmplitudeLabelClick2)
        
        self.stateButton2.released.connect(self.onNewRFState2)
        self.fmstateButton2.released.connect(self.onNewFMState2)
        self.amstateButton2.released.connect(self.onNewAMState2)
        self.frequencyBox2.returnPressed.connect(self.onNewFrequency2)
        self.amplitudeBox2.returnPressed.connect(self.onNewAmplitude2)
        self.fmgainBox2.returnPressed.connect(self.onNewFMGain2)
        self.amgainBox2.returnPressed.connect(self.onNewAMGain2)
    
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

    def onNewFMState1(self):
        fm_state1 = self.fmstateButton1.isChecked()
        self.reactor.callInThread(self.setFMState1, fm_state1)
    
    def setFMState1(self, fm_state1):
        self.device.fm_state1 = fm_state1
        self.reactor.callFromThread(self.displayFMState1, fm_state1)
        
    def onNewFMGain1(self):
        fm_gain1 = self.fmgainBox1.value()
        self.reactor.callInThread(self.setFMGain1, fm_gain1)
    
    def setFMGain1(self, fm_gain1):
        self.device.fm_gain1 = fm_gain1
        self.reactor.callFromThread(self.displayFMgain1, fm_gain1)

    def onNewAMState1(self):
        am_state1 = self.amstateButton1.isChecked()
        self.reactor.callInThread(self.setAMState1, am_state1)
    
    def setAMState1(self, am_state1):
        self.device.am_state1 = am_state1
        self.reactor.callFromThread(self.displayAMState1, am_state1)
        
    def onNewAMGain1(self):
        am_gain1 = self.amgainBox1.value()
        self.reactor.callInThread(self.setAMGain1, am_gain1)
    
    def setAMGain1(self, am_gain1):
        self.device.am_gain1 = am_gain1
        self.reactor.callFromThread(self.displayAMgain1, am_gain1)

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

    def onNewFMState2(self):
        fm_state2 = self.fmstateButton2.isChecked()
        self.reactor.callInThread(self.setFMState2, fm_state2)
    
    def setFMState2(self, fm_state2):
        self.device.fm_state2 = fm_state2
        self.reactor.callFromThread(self.displayFMState2, fm_state2)
        
    def onNewFMGain2(self):
        fm_gain2  = self.fmgainBox2.value()
        self.reactor.callInThread(self.setFMGain2, fm_gain2)
    
    def setFMGain2(self, fm_gain2):
        self.device.fm_gain2 = fm_gain2
        self.reactor.callFromThread(self.displayFMgain2, fm_gain2)
        
    def onNewAMState2(self):
        am_state2 = self.amstateButton2.isChecked()
        self.reactor.callInThread(self.setAMState2, am_state2)
    
    def setAMState2(self, am_state2):
        self.device.am_state2 = am_state2
        self.reactor.callFromThread(self.displayAMState2, am_state2)
        
    def onNewAMGain2(self):
        am_gain2 = self.amgainBox2.value()
        self.reactor.callInThread(self.setAMGain2, am_gain2)
    
    def setAMGain2(self, am_gain2):
        self.device.am_gain2 = am_gain2
        self.reactor.callFromThread(self.displayAMgain2, am_gain2)
        
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
        fm_gain1 = update.get('fm_gain1')
        if fm_gain1 is not None:
            self.displayFMgain1(fm_gain1)
            
        state2 = update.get('state2')
        if state2 is not None:
            self.displayState2(state2)
        frequency2 = update.get('frequency2')
        if frequency2 is not None:
            self.displayFrequency2(frequency2)
        amplitude2 = update.get('amplitude2')
        if amplitude2 is not None:
            self.displayAmplitude2(amplitude2)
        fm_gain2 = update.get('fm_gain2')
        if fm_gain2 is not None:
            self.displayFMgain2(fm_gain2)
    
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
    from rf2.devices.moglabs_ARF import MoglabsARFProxy

    class MoglabsARFClient(MoglabsARF_RFClient):
        name = 'Moglabs_ARF'
        DeviceProxy = MoglabsARFProxy
        
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
            MoglabsARFClient(reactor),
            ]
    
    widget = MultipleClientContainer(widgets, reactor)
    widget.show()
    reactor.suggestThreadPoolSize(30)
    reactor.run()
