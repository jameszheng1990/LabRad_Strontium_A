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
from twisted.internet.defer import inlineCallbacks
from client_tools.connection import connection

from client_tools.widgets import ClickableLabel
from client_tools.widgets import SuperSpinBox
import time, os


class PIDClient(QtWidgets.QWidget):
    
    wlm_lock_servername = None
    
    units = None
    units_list = ['nm', 'GHz']
    
    channel_list = ['1', '2', '3', '4']
    
    gain_range = (0, 100)
    gain_units = [(0, '')]
    gain_digits = 2
    
    setpoint_range = (0, 1e15)
    setpoint_units = [(0, '')]
    setpoint_digits = 6
    
    offset_range = (0, 100)  # Resonator offset
    offset_units = [(0, '%')]
    offset_digits = 4
    
    spinbox_height = 30
    spinbox_width = 80
    
    config_directory = 'C:\\LabRad\\SrA\\msquared_wlm_lock'
    
    def __init__(self, reactor, cxn, wlm_lock_servername, parent):
        super(PIDClient, self).__init__(None)
        try:
            self.reactor = reactor
            self.cxn = cxn
            self.wlm_lock_servername = wlm_lock_servername
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
        self.nameLabel =  ClickableLabel('<b> PID Settings </b>')
        
        self.loadButton = QtWidgets.QPushButton()
        self.loadButton.setText('Load Settings')
        self.loadButton.setFixedHeight(40)
        self.loadButton.setFixedWidth(100)
        self.saveButton = QtWidgets.QPushButton()
        self.saveButton.setText('Save Settings')
        self.saveButton.setFixedHeight(40)
        self.saveButton.setFixedWidth(self.spinbox_width*1.5)
        
        self.setpointLabel = ClickableLabel('Set point: ')
        self.setpointBox = SuperSpinBox(self.setpoint_range, self.setpoint_units,
                                        self.setpoint_digits)
        self.setpointBox.setFixedHeight(self.spinbox_height)
        self.setpointBox.setFixedWidth(self.spinbox_width*1.5)
    
        self.offsetLabel = ClickableLabel('Offset: ')
        self.offsetBox = SuperSpinBox(self.offset_range, self.offset_units,
                                        self.offset_digits)
        self.offsetBox.setFixedHeight(self.spinbox_height)
        self.offsetBox.setFixedWidth(self.spinbox_width*1.5)
        
        self.unitsLabel = ClickableLabel('<b> Setpoint Units: </b>')
        self.unitsBox = QtWidgets.QComboBox()
        self.unitsBox.addItems(self.units_list)
        
        self.channelLabel = ClickableLabel('<b> WLM Channel: </b>')
        self.channelBox = QtWidgets.QComboBox()
        self.channelBox.addItems(self.channel_list)
        
        self.OverallGainLabel = ClickableLabel('Overall Gain: ')
        self.OverallGainBox = SuperSpinBox(self.gain_range, self.gain_units,
                                        4)
        self.OverallGainBox.setFixedHeight(self.spinbox_height)
        self.OverallGainBox.setFixedWidth(self.spinbox_width)
        self.PGainLabel = ClickableLabel('P Gain: ')
        self.PGainBox = SuperSpinBox(self.gain_range, self.gain_units,
                                        self.gain_digits)
        self.PGainBox.setFixedHeight(self.spinbox_height)
        self.PGainBox.setFixedWidth(self.spinbox_width)
        self.IGainLabel = ClickableLabel('I Gain: ')
        self.IGainBox = SuperSpinBox(self.gain_range, self.gain_units,
                                        self.gain_digits)
        self.IGainBox.setFixedHeight(self.spinbox_height)
        self.IGainBox.setFixedWidth(self.spinbox_width)
        self.DGainLabel = ClickableLabel('D Gain: ')
        self.DGainBox = SuperSpinBox(self.gain_range, self.gain_units,
                                        self.gain_digits)
        self.DGainBox.setFixedHeight(self.spinbox_height)
        self.DGainBox.setFixedWidth(self.spinbox_width)
        
        
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.nameLabel, 1, 0, 3, 1, 
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.loadButton, 1, 1, 3, 2, 
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.saveButton, 1, 3, 3, 2, 
                              QtCore.Qt.AlignHCenter)
        
        self.layout.addWidget(self.setpointLabel, 4, 0, 3, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.setpointBox, 4, 1, 3, 3, 
                              QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.offsetLabel, 7, 0, 3, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.offsetBox, 7, 1, 3, 3, 
                              QtCore.Qt.AlignLeft)
        
        self.layout.addWidget(self.unitsLabel, 4, 3, 2, 2,
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.unitsBox, 6, 3, 2, 2,
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.channelLabel, 8, 3, 2, 2,
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.channelBox, 10, 3, 2, 2,
                              QtCore.Qt.AlignHCenter)
        
        self.layout.addWidget(self.OverallGainLabel, 10, 0, 3, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.OverallGainBox, 10, 1, 3, 1,
                              QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.PGainLabel, 13, 0, 3, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.PGainBox, 13, 1, 3, 1,
                              QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.IGainLabel, 16, 0, 3, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.IGainBox, 16, 1, 3, 1,
                              QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.DGainLabel, 19, 0, 3, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.DGainBox, 19, 1, 3, 1,
                              QtCore.Qt.AlignLeft)
        
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)
        self.setFixedSize(400, 300)

    # def updateParameters(self, parameter_values):
    #     self.parameter_values = parameter_values
    #     self.displaySequence(self.sequence)
    
    @inlineCallbacks
    def connectWidgets(self):
        self.wlm_lock_server = yield self.cxn.get_server(self.wlm_lock_servername)
        
        self.nameLabel.clicked.connect(self.getAll)
        self.loadButton.clicked.connect(self.browseLoad)
        self.saveButton.clicked.connect(self.browseSave)
        self.setpointBox.returnPressed.connect(self.onNewPIDsetpoint)
        self.offsetBox.returnPressed.connect(self.onNewPIDoffset)
        self.OverallGainBox.returnPressed.connect(self.onNewPIDparams)
        self.PGainBox.returnPressed.connect(self.onNewPIDparams)
        self.IGainBox.returnPressed.connect(self.onNewPIDparams)
        self.DGainBox.returnPressed.connect(self.onNewPIDparams)
        self.unitsBox.currentIndexChanged.connect(self.onUnitsChange)
        self.channelBox.currentIndexChanged.connect(self.onChannelChange)
        
        self.getAll()
    
    def disconnectWidgets(self):
        try:
            self.nameLabel.disconnect()
            self.loadButton.disconnect()
            self.saveButton.disconnect()
            self.setpointBox.disconnect()
            self.offsetBox.disconnect()
            self.OverallGainBox.disconnect()
            self.PGainBox.disconnect()
            self.IGainBox.disconnect()
            self.DGainBox.disconnect()
            self.unitsBox.disconnect()
            self.channelBox.disconnect()
        except:
            pass
    
    def disableAll(self):
        self.loadButton.setDisabled(True)
        self.saveButton.setDisabled(True)
        self.setpointBox.setDisabled(True)
        self.offsetBox.setDisabled(True)
        self.OverallGainBox.setDisabled(True)
        self.PGainBox.setDisabled(True)
        self.IGainBox.setDisabled(True)
        self.DGainBox.setDisabled(True)
        self.unitsBox.setDisabled(True)
        self.channelBox.setDisabled(True)
        self.disconnectWidgets()

    def enableAll(self):
        self.loadButton.setDisabled(False)
        self.saveButton.setDisabled(False)
        self.setpointBox.setDisabled(False)
        self.offsetBox.setDisabled(False)
        self.OverallGainBox.setDisabled(False)
        self.PGainBox.setDisabled(False)
        self.IGainBox.setDisabled(False)
        self.DGainBox.setDisabled(False)
        self.unitsBox.setDisabled(False)
        self.channelBox.setDisabled(False)
        self.connectWidgets()
    
    def getAll(self):
        self.getPID()
        self.getWLM()
    
    def disable_when_wlm_lock(self, state):
        self.unitsBox.setDisabled(state)
        self.channelBox.setDisabled(state)
        self.setpointBox.setDisabled(state)
        self.offsetBox.setDisabled(state)
        self.loadButton.setDisabled(state)
    
    @inlineCallbacks
    def loadSettingsFromServer(self):
        current_settings_json = yield self.wlm_lock_server.load_current_settings()
        current_settings = json.loads(current_settings_json)
        self.displaySettings(current_settings)

    def browseLoad(self):
        # timestr = time.strftime(self.time_format)
        directory = self.config_directory
        if not os.path.exists(directory):
            directory = self.config_directory.split('{}')[0]
        filepath = QtWidgets.QFileDialog().getOpenFileName(directory=directory)[0]  # Added [0]
        if filepath:
            self.loadConfig(filepath)
    
    def loadConfig(self, filepath):
        with open(filepath, 'r') as infile:
            settings = json.load(infile)
        self.displaySettings(settings)       
        
    def browseSave(self):
        directory = self.config_directory
        if not os.path.exists(directory):
            directory = self.config_directory.split('{}')[0]
        filepath = QtWidgets.QFileDialog().getSaveFileName(directory=directory)[0]
        if filepath:
            self.saveConfig(filepath)
    
    @inlineCallbacks
    def saveConfig(self, filepath):
        current_settings_json = yield self.wlm_lock_server.load_current_settings()
        with open(filepath, 'w') as f:
            f.write(current_settings_json)

    def displaySettings(self, settings):
        pid_settings = settings['pid']
        wlm_settings = settings['wlm']
        
        setpoint = pid_settings['setpoint']
        offset = pid_settings['offset']
        overall_gain = pid_settings['overall_gain']
        prop_gain = pid_settings['prop_gain']
        int_gain = pid_settings['int_gain']
        diff_gain = pid_settings['diff_gain']
        
        units = wlm_settings['units']
        channel = wlm_settings['channel']
        
        self.displayPIDsetpoint(setpoint)
        self.displayPIDoffset(offset)
        self.displayPIDparams(overall_gain, prop_gain, int_gain, diff_gain)
        self.displayUnits(units)
        self.displayChannel(channel)    


    def getPID(self):
        self.getPIDsetpoint()
        self.getPIDoffset()
        self.getPIDparams()
    
    @inlineCallbacks
    def getPIDsetpoint(self):
        setpoint = yield self.wlm_lock_server.get_setpoint()
        self.displayPIDsetpoint(setpoint)
        
    @inlineCallbacks
    def getPIDoffset(self):
        offset = yield self.wlm_lock_server.get_offset()
        self.displayPIDoffset(offset)
    
    @inlineCallbacks
    def getPIDparams(self):
        overall_gain = yield self.wlm_lock_server.get_gain()
        prop_gain = yield self.wlm_lock_server.get_prop_gain()
        int_gain = yield self.wlm_lock_server.get_int_gain()
        diff_gain = yield self.wlm_lock_server.get_diff_gain()
        self.displayPIDparams(overall_gain, prop_gain, int_gain, diff_gain)
    
    def displayPIDsetpoint(self, setpoint):
        self.setpointBox.display(setpoint)

    def displayPIDoffset(self, offset):
        self.offsetBox.display(offset)
        
    def displayPIDparams(self, overall_gain, prop_gain, int_gain, diff_gain):
        self.OverallGainBox.display(overall_gain)
        self.PGainBox.display(prop_gain)
        self.IGainBox.display(int_gain)
        self.DGainBox.display(diff_gain)
    
    def onNewPIDsetpoint(self):
        setpoint = self.setpointBox.value()
        self.setPIDsetpoint(setpoint)

    def onNewPIDoffset(self):
        offset = self.offsetBox.value()
        self.setPIDoffset(offset)
    
    def onNewPIDparams(self):
        overall_gain = self.OverallGainBox.value()
        prop_gain = self.PGainBox.value()
        int_gain = self.IGainBox.value()
        diff_gain = self.DGainBox.value()
        self.setPIDparams(overall_gain, prop_gain, int_gain, diff_gain)

    @inlineCallbacks
    def setPIDsetpoint(self, setpoint):
        yield self.wlm_lock_server.set_setpoint(setpoint)
        self.displayPIDsetpoint(setpoint)
        
    @inlineCallbacks
    def setPIDoffset(self, offset):
        yield self.wlm_lock_server.set_offset(offset)
        self.displayPIDoffset(offset)
        
    @inlineCallbacks
    def setPIDparams(self, overall_gain, prop_gain, int_gain, diff_gain):
        yield self.wlm_lock_server.set_gain(overall_gain)
        yield self.wlm_lock_server.set_prop_gain(prop_gain)
        yield self.wlm_lock_server.set_int_gain(int_gain)
        yield self.wlm_lock_server.set_diff_gain(diff_gain)
        self.displayPIDparams(overall_gain, prop_gain, int_gain, diff_gain)
    
    def getWLM(self):
        self.getUnits()
        self.getChannel() 
        
    def onUnitsChange(self):
        value = self.unitsBox.currentText()
        self.setUnits(value)
    
    @inlineCallbacks
    def setUnits(self, value):
        yield self.wlm_lock_server.set_units(value)
    
    @inlineCallbacks
    def getUnits(self):
        units = yield self.wlm_lock_server.get_units()
        self.displayUnits(units)
    
    def displayUnits(self, units):
        index = self.unitsBox.findText(units, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.unitsBox.setCurrentIndex(index)
    
    def onChannelChange(self):
        value = self.channelBox.currentText()
        self.setChannel(int(value))

    @inlineCallbacks
    def setChannel(self, value):
        yield self.wlm_lock_server.set_channel(value)
        
    @inlineCallbacks
    def getChannel(self):
        channel = yield self.wlm_lock_server.get_channel()
        self.displayChannel(channel)
        
    def displayChannel(self, channel):
        index = self.channelBox.findText(str(channel), QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.channelBox.setCurrentIndex(index)
    
    def closeEvent(self, x):
        # super(WLMLockControllerClient, self).closeEvent(x)
        # self.PIDClient.wlm_lock_server.remove_etalon_lock(10) # TODO: Remove Etalon Lock when exit
        try:
            self.reactor.stop()
            x.accept()
        except:
            pass       