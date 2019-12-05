import json
import numpy as np
import time
import os
import datetime

from twisted.internet.defer import inlineCallbacks
from twisted.internet import task
from twisted.internet.threads import deferToThread

from PyQt5 import QtCore, Qt, QtWidgets
import matplotlib
matplotlib.use('QT5Agg')

import matplotlib.pylab as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas 
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from current_controller.clients.widgets.plotter import PlotterClient
from client_tools.widgets import ClickableLabel

class CurrentControllerClient(QtWidgets.QGroupBox):
    name = None
    DeviceProxy = None
    
    lockedColor = '#80ff80'
    unlockedColor = '#ff8080'
    
    updateID = np.random.randint(0, 2**31 - 1)
    
    threshold = 0
    currentStepsize = 0.1
    scan_wait_time = 0.3 # in second
    relock_timeinterval = 20 # in second
    
    locki = 0
    lockf = 0
    
    relock_state = True
    relock_status = False
    stop_status = False
    
    def __init__(self, reactor):
        QtWidgets.QDialog.__init__(self)
        self.data_directory = []
        self.list_x = []
        self.list_y = []
        self.reactor = reactor
        reactor.callInThread(self.initialize)
        self.connectLabrad()
        
        time_format = '%Y%m%d'
        timestr = time.strftime(time_format)
        foldername = 'Blue Slave Lock Curve'
        self.data_directory = os.path.join(os.getenv('LABRADDATA'), foldername, timestr)
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
    
    @inlineCallbacks
    def connectLabrad(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name=self.name, host=os.getenv('LABRADHOST'), password='')
        yield self.cxn.update.signal__signal(self.updateID)
        yield self.cxn.update.addListener(listener=self.receiveUpdate, source=None, 
                                          ID=self.updateID)
        yield self.cxn.update.register(self.name)

    def receiveUpdate(self, c, updateJson):
        # 'Power' in functions means Monitor Current
        update = json.loads(updateJson)
        state = update.get('state')
        if state is not None:
            self.displayState(state)
        current = update.get('current')
        if current is not None:
            self.displayCurrent(current)
        moncurrent = update.get('moncurrent')
        if moncurrent is not None:
            self.displayPower(moncurrent)

    def initialize(self):
        import labrad
        cxn = labrad.connect(name=self.name, host=os.getenv('LABRADHOST'), password='')
        self.device = self.DeviceProxy(cxn)
        self.reactor.callFromThread(self.populateGUI)
        self.reactor.callFromThread(self.connectSignals)
    
    def populateGUI(self):
        self.nameLabel = ClickableLabel('<b>'+self.name+'</b>')
        self.stateText = QtWidgets.QLineEdit()
        self.stateText.setReadOnly(True)
        self.stateText.setAlignment(QtCore.Qt.AlignCenter)
        
        self.warmupLabel = ClickableLabel('Warm up: ')
        self.warmupButton = QtWidgets.QPushButton()
        self.shutoffLabel = ClickableLabel('Shut off: ')
        self.shutoffButton = QtWidgets.QPushButton()
        
        self.scanLabel = ClickableLabel('Scan: ')
        self.scanButton = QtWidgets.QPushButton()
        
        self.lockLabel = ClickableLabel('Lock: ')
        self.lockButton = QtWidgets.QPushButton()
        
        self.relockLabel = ClickableLabel('Enable ReLock: ')
        self.relockButton = QtWidgets.QCheckBox()
        
        self.currentLabel = ClickableLabel('Current [mA]: ')
        self.currentBox = QtWidgets.QDoubleSpinBox()
        self.currentBox.setKeyboardTracking(False)
        self.currentBox.setRange(*self.device._current_range)
        self.currentBox.setSingleStep(self.currentStepsize)
        self.currentBox.setDecimals(
                abs(int(np.floor(np.log10(self.currentStepsize)))))
#        self.currentBox.setAccelerated(True)

        self.powerLabel = ClickableLabel('MonCurrent [uA]: ')
        self.powerBox = QtWidgets.QDoubleSpinBox()
        self.powerBox.setRange(0, 3e3)
        self.powerBox.setReadOnly(True)
        self.powerBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.powerBox.setDecimals(1)
        
        self.scaniLabel = ClickableLabel('Scan i [mA]: ')
        self.scaniBox = QtWidgets.QDoubleSpinBox()
        self.scaniBox.setKeyboardTracking(False)
        self.scaniBox.setRange(*self.device._current_range)
        self.scaniBox.setSingleStep(self.currentStepsize)
        self.scaniBox.setDecimals(
                abs(int(np.floor(np.log10(self.currentStepsize)))))
        
        self.scanfLabel = ClickableLabel('Scan f [mA]: ')
        self.scanfBox = QtWidgets.QDoubleSpinBox()
        self.scanfBox.setKeyboardTracking(False)
        self.scanfBox.setRange(*self.device._current_range)
        self.scanfBox.setSingleStep(self.currentStepsize)
        self.scanfBox.setDecimals(
                abs(int(np.floor(np.log10(self.currentStepsize)))))
        
        self.lockiLabel = ClickableLabel('Lock i [mA]: ')
        self.lockiBox = QtWidgets.QDoubleSpinBox()
        self.lockiBox.setRange(0, 1e3)
        self.lockiBox.setReadOnly(True)
        self.lockiBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.lockiBox.setDecimals(1)
        
        self.lockfLabel = ClickableLabel('Lock f [mA]: ')
        self.lockfBox = QtWidgets.QDoubleSpinBox()
        self.lockfBox.setRange(0, 1e3)
        self.lockfBox.setReadOnly(True)
        self.lockfBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.lockfBox.setDecimals(1)
            
        self.thresholdLabel = ClickableLabel('Lock threshold [uA]: ')
        self.thresholdBox = QtWidgets.QDoubleSpinBox()
        self.thresholdBox.setRange(0, 3e3)
        self.thresholdBox.setReadOnly(True)
        self.thresholdBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.thresholdBox.setDecimals(1)
        
        self.plotterClient = PlotterClient(self.reactor, self)
        self.grapherLabel = ClickableLabel('Scan Curve {}: '.format(self.name[-1]))
        self.grapher = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.grapher.addWidget(self.plotterClient)
        
        self.stopLabel = ClickableLabel('Stop relock: ')
        self.stopButton = QtWidgets.QPushButton()
        
        self.statusLabel = ClickableLabel('Status: ')
        self.statusText = QtWidgets.QLineEdit()
        self.statusText.setReadOnly(True)
        self.statusText.setAlignment(QtCore.Qt.AlignCenter)
        
        # lAYOUT #
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.nameLabel, 1, 0, 1, 1, 
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.stateText, 1, 1,)
        
        self.layout.addWidget(self.warmupLabel, 2, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.warmupButton, 2, 1)
        self.layout.addWidget(self.shutoffLabel, 2, 2, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.shutoffButton, 2, 3)
        
        self.layout.addWidget(self.currentLabel, 3, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.currentBox, 3, 1)
        self.layout.addWidget(self.powerLabel, 3, 2, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.powerBox, 3, 3)
        
        self.layout.addWidget(self.scanLabel, 4, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.scanButton, 4, 1)
        self.layout.addWidget(self.relockLabel, 4, 2, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.relockButton, 4, 3)
        
        self.layout.addWidget(self.lockLabel, 5, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.lockButton, 5, 1)
        self.layout.addWidget(self.stopLabel, 5, 2, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.stopButton, 5, 3)
        
        self.layout.addWidget(self.scaniLabel, 6, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.scaniBox, 6, 1)
        self.layout.addWidget(self.scanfLabel, 6, 2, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.scanfBox, 6, 3)
        
        self.layout.addWidget(self.lockiLabel, 7, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.lockiBox, 7, 1)
        self.layout.addWidget(self.lockfLabel, 7, 2, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.lockfBox, 7, 3)
        
        self.layout.addWidget(self.thresholdLabel, 8, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.thresholdBox, 8, 1)
        
        
        self.layout.addWidget(self.grapherLabel, 9, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.statusLabel, 9, 2, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.statusText, 9, 3)
        self.layout.addWidget(self.grapher, 10, 0, 4, 4)
        
        self.setWindowTitle(self.name)
        self.setLayout(self.layout)
        self.setFixedSize(390, 580)
    
        self.reactor.callInThread(self.getAll)
    
    def getAll(self):
        self.getState()
        self.getCurrent()
        self.getPower()
        self.getRelockState()
        self.getScanI()
        self.getScanF()
        self.getLockI()
        self.getLockF()
        self.getThreshold()
        self.getRelockStatus()
    
    def getState(self):
        state = self.device.state
        self.reactor.callFromThread(self.displayState, state)

    def displayState(self, state):
        if state:
            self.stateText.setText('Laser ON')
            self.stateText.setStyleSheet('QWidget {background-color: %s}' % self.lockedColor)
        else:
            self.stateText.setText('Laser OFF')
            self.stateText.setStyleSheet('QWidget {background-color: %s}' % self.unlockedColor)
    
    def getCurrent(self):
        current = self.device.current
        self.reactor.callFromThread(self.displayCurrent, current)

    def displayCurrent(self, current):
        self.currentBox.setValue(current)
    
    def getPower(self):
        moncurrent = self.device.moncurrent
        self.reactor.callFromThread(self.displayPower, moncurrent)

    def displayPower(self, moncurrent):
        self.powerBox.setValue(moncurrent)
        if hasattr(self.device, '_locked_threshold'):
            if moncurrent > self.threshold:
                self.powerBox.setStyleSheet('QWidget {background-color: %s}' % self.lockedColor)
            else:
                self.powerBox.setStyleSheet('QWidget {background-color: %s}' % self.unlockedColor)
    
    def startWarmup(self):
        def warmup_parent():
            self.reactor.callInThread(warmup)
        
        def warmup():
            if self.j == 0:
                self.device.state = 1
                self.displayState(1)
                self.j += 1
            elif 0 < self.j < self.warmup_num:
                self.reactor
                self.device.current = self.warmup_list[self.j]
                self.j += 1
                time.sleep(0.5)
                self.getCurrent()
                self.getPower()
            else:
                self.getCurrent()
                self.getPower()
                print('{} warm-up finished!'.format(self.name))
                self.onNewStatus('ON')
                self.warmup_task.stop()
            
        state = self.device.state
        if state == True:
            print('{} is already on.'.format(self.name))
        else:
            print("{} warming up... Wait for about 20 second to settle down".format(self.name))
            self.onNewStatus('Warming up...')
            self.getState()
            self.warmup_task = task.LoopingCall(warmup_parent)
            self.warmup_task.start(3)
    
    def onWarmup(self):
        self.warmup_list = [0, 40, 70, 100, 130]
        self.warmup_num = len(self.warmup_list)
        self.j = 0
        self.reactor.callInThread(self.startWarmup)
    
    def startShutoff(self):
        def shutoff_parent():
            self.reactor.callInThread(shutoff)
            
        def shutoff():
            if self.k < self.shutoff_num:
                self.device.current = self.shutoff_list[self.k]
                self.k += 1
                time.sleep(0.5)
                self.getCurrent()
                self.getPower()
            elif self.k == self.shutoff_num:
                self.device.state = 0
                self.displayState(0)
                self.k += 1
            else:
                self.getCurrent()
                self.getPower()
                print('{} shut-off finished!'.format(self.name))
                self.onNewStatus('OFF')
                self.shutoff_task.stop()
        
        state = self.device.state
        if state == False:
            print('{} is already off.'.format(self.name))
        else:
            print("{} shutting off... Wait for about 10 second to settle down".format(self.name))
            self.onNewStatus('Shutting off...')
            self.getState()
            self.shutoff_task = task.LoopingCall(shutoff_parent)
            self.shutoff_task.start(3)
            
    def onShutoff(self):
        self.shutoff_list = [120, 80, 40, 0]
        self.shutoff_num = len(self.shutoff_list)
        self.k = 0
        self.reactor.callInThread(self.startShutoff)
    
    def onNewStatus(self, text):
        self.reactor.callInThread(self.setStatus, text)
        
    def setStatus(self, text):
        self.statusText.setText(text)
    
    def connectSignals(self):
        self.currentBox.valueChanged.connect(self.onNewCurrent)
        self.nameLabel.clicked.connect(self.onNameLabelClick)
        
        self.warmupButton.released.connect(self.onWarmup)
        self.shutoffButton.released.connect(self.onShutoff)
        
        self.scaniBox.valueChanged.connect(self.onNewScanI)
        self.scanfBox.valueChanged.connect(self.onNewScanF)
        
        self.scanButton.released.connect(self.onScan)
        self.lockButton.released.connect(self.onLock)
        self.relockButton.released.connect(self.onRelockState)
        self.stopButton.released.connect(self.onStopClick)
    
    def onNewCurrent(self):
        current = self.currentBox.value()
        self.reactor.callInThread(self.setCurrent, current)
    
    def onNameLabelClick(self):
        self.reactor.callInThread(self.getAll)

    def onPowerLabelClick(self):
        self.reactor.callInThread(self.getPower)

    def setCurrent(self, current):
        self.device.current = current
        self.reactor.callFromThread(self.displayCurrent, current)
        time.sleep(self.scan_wait_time)
        self.getPower()
        
    def getRelockState(self):
        relock_state = self.relock_state
        self.reactor.callFromThread(self.displayRelockEnable, relock_state)
    
    def onRelockState(self):
        self.reactor.callInThread(self.setRelockState)
    
    def setRelockState(self):
        self.relock_state = not self.relock_state
        self.reactor.callFromThread(self.displayRelockEnable, self.relock_state)
    
    def displayRelockEnable(self, relock_state):
        if relock_state:
            self.relockButton.setChecked(1)
            self.relockButton.setText('On')
            self.relockButton.setStyleSheet('QWidget {background-color: %s}' % self.lockedColor)
        else:
            self.relockButton.setChecked(0)
            self.relockButton.setText('Off')
            self.relockButton.setStyleSheet('QWidget {background-color: %s}' % self.unlockedColor)
    
    def getRelockStatus(self):
        relock_status = self.relock_status
        self.reactor.callFromThread(self.displayRelockStatus, relock_status)
    
    def displayRelockStatus(self, relock_status):
        if relock_status == True:
            self.lockButton.setText('Relock On')
            self.lockButton.setStyleSheet('QWidget {background-color: %s}' % self.lockedColor)
        else:
            self.lockButton.setText('Relock Off')
            self.lockButton.setStyleSheet('QWidget {background-color: %s}' % self.unlockedColor)
    
    def getThreshold(self):
        threshold = self.threshold 
        self.reactor.callFromThread(self.displayThreshold, threshold)
    
    def displayThreshold(self, threshold):
        self.thresholdBox.setValue(threshold)
    
    def getScanI(self):
        scani = self.scani
        self.reactor.callFromThread(self.displayScanI, scani)
    
    def onNewScanI(self):
        self.scani = self.scaniBox.value()
        self.reactor.callFromThread(self.displayScanI, self.scani)
    
    def displayScanI(self, scani):
        self.scaniBox.setValue(scani)
       
    def getScanF(self):
        scanf = self.scanf
        self.reactor.callFromThread(self.displayScanF, scanf)
    
    def onNewScanF(self):
        self.scanf = self.scanfBox.value()
        self.reactor.callFromThread(self.displayScanF, self.scanf)
    
    def displayScanF(self, scanf):
        self.scanfBox.setValue(scanf)
        
    def getLockI(self):
        locki = self.locki
        self.reactor.callFromThread(self.displayLockI, locki)
    
    def displayLockI(self, locki):
        self.lockiBox.setValue(locki)
    
    def getLockF(self):
        lockf = self.lockf
        self.reactor.callFromThread(self.displayLockF, lockf)
    
    def displayLockF(self, lockf):
        self.lockfBox.setValue(lockf)
    
    def onScan(self):
        self.reactor.callInThread(self.startScan)
    
    def lockListGen(self, scani, scanf):
        return list(reversed(np.around(np.arange(scanf, scani+self.step, self.step), decimals=1)))

    def startScan(self):
        LASstate = self.device.state
        if LASstate:
            if self.relock_status == False:        
                self.list_scan = []
                self.list_moncurrent = []
                self.list_moncurrent_diff = []
                self.list_y = []
                self.step = self.device._relock_stepsize
                self.list_x = list(np.around(np.arange(self.scanf, self.scani+self.step, self.step), decimals=1))
                self.list_scan = list(reversed(self.list_x))
                print('{} started scanning, please wait...'.format(self.name))
                self.onNewStatus('Scanning...')
                for i in self.list_scan:
                    self.device.current = i
                    self.reactor.callFromThread(self.displayCurrent, i)
                    time.sleep(self.scan_wait_time)
                    self.getPower()
                    mon = self.device.moncurrent
                    self.list_moncurrent.append(mon)
                    self.list_y = list(reversed(self.list_moncurrent))
            
                # find scanf
                self.list_moncurrent_diff = [round(j-i, 2) for i,j in zip(self.list_moncurrent[:-1], self.list_moncurrent[1:])]
                scanfIndex = np.array(self.list_moncurrent_diff).argmin()
                self.lockf = round(self.list_scan[scanfIndex], 2) + 0.2
        
                # find scani
                scaniIndex = 0
                for i in range(len(self.list_moncurrent) - 4):
                    if self.list_moncurrent[i] < self.list_moncurrent[i+4]:
                        scaniIndex = i
                        break;
                self.locki = round(self.list_scan[scaniIndex] + 0.2, 2) 
                self.threshold = int((self.list_moncurrent[scanfIndex] + self.list_moncurrent[scanfIndex + 2])/2)
                        
                self.currentDT = datetime.datetime.now()
                self.file_name = self.name + '_' + self.currentDT.strftime("%H_%M_%S") + '.png'
                self.save_path = os.path.join(self.data_directory, self.file_name)
        
                self.plotterClient.plot(self.list_x, self.list_y, self.save_path)
                
                self.getLockI()
                self.getLockF()
                self.getThreshold()
                self.lock_list = self.lockListGen(self.locki, self.lockf)
            
                print('{} scan finished!'.format(self.name))
                self.onNewStatus('Scan done!')
                print('{} locked points: {} mA, {} mA, and threshold {} uA.'.format(self.name, self.locki, self.lockf, self.threshold))
            
            else:
                print('Relock on, stop relocking first!')
        else:
            self.getPower()
            print('Turn on Laser first!')
        
    def onLock(self):
        self.reactor.callInThread(self.startLock)
        
    def startLock(self):
        if self.threshold == 0:
            print('Threshold is 0, scan first!')
            return
        
        elif self.threshold > 0:
            relock_state = self.relock_state
            
            if relock_state == False:
                # Will only lock once
                self.onNewStatus('Locking...')
                for i in self.lock_list:
                    self.device.current = i
                    self.reactor.callFromThread(self.displayCurrent, i)
                    time.sleep(self.scan_wait_time)
                    self.getPower()
                print('{} is locked at {} mA'.format(self.name, self.lockf)) 
                time.sleep(3)
                self.onNewStatus('Locked')
            
            if relock_state == True:
                if self.relock_status == True:
                    # Only start locking/relock when relock_status is False and relock is enable
                    print('Relock is already running!')
                    pass
                    
                elif self.relock_status == False:
                    # Will start relocking
                    self.relock_status = True
                    self.stop_status = False 
                    self.getRelockStatus()
                    self.onNewStatus('Locking...')
                    self.relock_task = task.LoopingCall(self.startRelock_parent)
                    self.relock_task.start(self.relock_timeinterval)
    
    def startRelock_parent(self):
        self.reactor.callInThread(self.startRelock)
    
    def startRelock(self):
        def try_lock_parent():
            self.reactor.callInThread(try_lock)
        
        def try_lock():
            if self.i < self.num_stop:
                self.device.current = self.lock_list[self.i]
                print('{} starts relocking: {} mA, {} uA'.format(self.name, self.lock_list[self.i], self.device.moncurrent))
                self.i = self.i+ 1
                time.sleep(self.scan_wait_time)
                self.getCurrent()
                self.getPower()
            else:
                self.try_relock_task.stop()
                
        if self.stop_status == False:
            mon = self.device.moncurrent
            if mon >= self.threshold:
                print('{} stays locked.'.format(self.name))
                self.onNewStatus('Locked.')
                self.getCurrent()
                self.getPower()
            else:
                print('{} has came unlocked.'.format(self.name))
                self.num_stop = len(self.lock_list)
                self.i = 0
                self.try_relock_task = task.LoopingCall(try_lock_parent)
                self.try_relock_task.start(self.scan_wait_time+0.2)
                self.onNewStatus('Relocking...')
                self.getCurrent()
                self.getPower()

        else:
            self.relock_status = False
            print('{} relock program stopped.'.format(self.name))
            self.getRelockStatus()
            self.getCurrent()
            self.getPower()
            self.relock_task.stop()
            
        
    def onStopClick(self):
        self.reactor.callInThread(self.onStop)
    
    def onStop(self):
        if self.relock_status == True:
            self.stop_status = True
            self.getPower()
            print('{} stops relocking, wait...'.format(self.name))
            self.onNewStatus('Stop relocking.')
            
        else:
            pass
    
    def closeEvent(self, x):
        super(CurrentControllerClient, self).closeEvent(x)
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
        self.setFixedSize(410 * len(self.client_list), 600)
        self.setWindowTitle(self.name)
        self.setLayout(self.layout)

    def closeEvent(self, x):
        super(MultipleClientContainer, self).closeEvent(x)
        self.reactor.stop()

if __name__ == '__main__':
    from current_controller.devices.blue_slave_1 import BlueSlave1Proxy
    from current_controller.devices.blue_slave_2 import BlueSlave2Proxy
    from current_controller.devices.blue_slave_3 import BlueSlave3Proxy

    class BlueSlave1Client(CurrentControllerClient):
        name = 'Blue Slave 1'
        DeviceProxy = BlueSlave1Proxy
        scani = 129
        scanf = 125
    
    class BlueSlave2Client(CurrentControllerClient):
        name = 'Blue Slave 2'
        DeviceProxy = BlueSlave2Proxy
        scani = 128
        scanf = 124

    class BlueSlave3Client(CurrentControllerClient):
        name = 'Blue Slave 3'
        DeviceProxy = BlueSlave3Proxy
        scani = 132
        scanf = 128
    
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    from client_tools import qt5reactor 
    qt5reactor.install()
    from twisted.internet import reactor

    widgets = [
            BlueSlave1Client(reactor),
            BlueSlave2Client(reactor),
            BlueSlave3Client(reactor),
            ]
    
    widget = MultipleClientContainer(widgets, reactor)
    widget.show()
    reactor.suggestThreadPoolSize(30)
    reactor.run()