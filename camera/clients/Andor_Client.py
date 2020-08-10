from PyQt5 import QtWidgets, QtCore
import h5py
import json
import matplotlib as mpl
import numpy as np
import os
import sys
from time import strftime

from twisted.internet.defer import inlineCallbacks
from client_tools.widgets import ClickableLabel, SuperSpinBox

from client_tools.connection import connection
import pyqtgraph as pg
from camera.clients.cmap_to_colormap import cmapToColormap

cmap = mpl.cm.get_cmap('magma')
MyColorMap = pg.ColorMap(*zip(*cmapToColormap(cmap)))

from camera.clients.data_tools.process_image import process_image

class CameraClient(QtWidgets.QWidget):
    andor_servername = 'andor'
    andor_serial_number = 0
    
    servername = 'camera'
    update_id = np.random.randint(0, 2**31 - 1)
    data_directory = os.path.join(os.getenv('LABRADDATA'), 'data')
    name = None
    cxn  = None
    
    timeRange = (0, 1e9)
    timeDisplayUnits = [(0, 's'), (-3, 'ms'), (-6, 'us')]
    timeDigits = 2

    def __init__(self, reactor):
        super(CameraClient, self).__init__()
        self.reactor = reactor
        self.connect()
    
    @inlineCallbacks
    def connect(self):        
        if self.cxn is None:
            self.cxn = connection()
            cname = '{} - {} - client'.format(self.servername, self.name)
            yield self.cxn.connect(name=cname)
        try:
            self.populate()
            yield self.connectSignals()
        except Exception as e:
            print(e)

    def populate(self):
        self.andorLabel = ClickableLabel('<b>' + 'IXon - 888' +  '</b>')
        
        self.tempLabel = ClickableLabel('Temp: ')
        self.tempBox = QtWidgets.QDoubleSpinBox()
        self.tempBox.setRange(-150, 50)
        self.tempBox.setReadOnly(True)
        self.tempBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.tempBox.setDecimals(0)
        self.tempBox.setSuffix(' \u00b0 C')
        self.tempBox.setFixedWidth(80)
        
        self.emgainLabel = ClickableLabel('EM Gain: ')
        self.emgainBox = QtWidgets.QDoubleSpinBox()
        self.emgainBox.setRange(0, 300)
        self.emgainBox.setReadOnly(True)
        self.emgainBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.emgainBox.setDecimals(0)
        self.emgainBox.setFixedWidth(80)
        
        self.exposureLabel = ClickableLabel('Exposure Time: ')
        self.exposureBox = SuperSpinBox(self.timeRange,
                                        self.timeDisplayUnits,
                                        self.timeDigits)
        self.exposureBox.setReadOnly(True)
        self.exposureBox.setFixedWidth(80)
                
        self.accumulationLabel = ClickableLabel('Accumulation Time: ')
        self.accumulationBox = SuperSpinBox(self.timeRange,
                                        self.timeDisplayUnits,
                                        self.timeDigits)
        self.accumulationBox.setReadOnly(True)
        self.accumulationBox.setFixedWidth(80)
        
        self.kineticLabel = ClickableLabel('Kinetic Time: ')
        self.kineticBox = SuperSpinBox(self.timeRange,
                                        self.timeDisplayUnits,
                                        self.timeDigits)
        self.kineticBox.setReadOnly(True)
        self.kineticBox.setFixedWidth(80)
        
        self.readoutLabel = ClickableLabel('Readout Time: ')
        self.readoutBox = SuperSpinBox(self.timeRange,
                                        self.timeDisplayUnits,
                                        self.timeDigits)
        self.readoutBox.setReadOnly(True)
        self.readoutBox.setFixedWidth(80)
        
        self.imageView = pg.ImageView()
        self.imageView.setColorMap(MyColorMap)
        self.imageView.show()
        
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        self.layout.addWidget(self.andorLabel, 1, 0, 1, 1)        
        self.layout.addWidget(self.tempLabel, 2, 0, 1, 1,
                              QtCore.Qt.AlignRight)      
        self.layout.addWidget(self.tempBox, 2, 1, 1, 1)     
        self.layout.addWidget(self.emgainLabel, 2, 2, 1, 1,
                              QtCore.Qt.AlignRight)      
        self.layout.addWidget(self.emgainBox, 2, 3, 1, 1)   
        self.layout.addWidget(self.exposureLabel, 2, 4, 1, 1,
                              QtCore.Qt.AlignRight)      
        self.layout.addWidget(self.exposureBox, 2, 5, 1, 1)
        self.layout.addWidget(self.accumulationLabel, 2, 6, 1, 1,
                              QtCore.Qt.AlignRight)      
        self.layout.addWidget(self.accumulationBox, 2, 7, 1, 1)
        self.layout.addWidget(self.kineticLabel, 2, 8, 1, 1,
                              QtCore.Qt.AlignRight)      
        self.layout.addWidget(self.kineticBox, 2, 9, 1, 1)
        self.layout.addWidget(self.readoutLabel, 2, 10, 1, 1,
                              QtCore.Qt.AlignRight)      
        self.layout.addWidget(self.readoutBox, 2, 11, 1, 1)
        self.layout.addWidget(self.imageView, 3, 0, 15, 15)
        self.setLayout(self.layout)
        self.setFixedSize(1200, 800)
        self.setWindowTitle('{} - {} - client'.format(
                            self.servername, self.name))
    
    @inlineCallbacks
    def connectSignals(self):
        self.context = yield self.cxn.context()
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id)
        yield server.addListener(listener=self.receive_update, source=None, 
                                 ID=self.update_id)
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)
        
        self.imageView.scene.sigMouseClicked.connect(self.handle_click)
        
        self.andorLabel.clicked.connect(self.getAll)
        self.tempLabel.clicked.connect(self.getTemperature)
        self.emgainLabel.clicked.connect(self.getEMGain)
        self.getAll()

    @inlineCallbacks
    def reinitialize(self):
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id, context=self.context)
        # try:
        #     yield server.removeListener(listener=self.receive_update, source=None,
        #                            ID=self.update_id, context=self.context)
        # except:
        #     pass
        yield server.addListener(listener=self.receive_update, source=None,
                                  ID=self.update_id, context=self.context)

    def disable(self):
        pass
        
    def getAll(self):
        self.getTemperature()
        self.getEMGain()
        self.getAcquisitionTiming()
        self.getReadOutTime()
        
    @inlineCallbacks
    def getTemperature(self):
        server = yield self.cxn.get_server(self.andor_servername)
        temp = yield server.get_temperature(self.andor_serial_number)
        self.DisplayTemperature(temp[1])
    
    def DisplayTemperature(self, temp):
        self.tempBox.setValue(temp)
    
    @inlineCallbacks
    def getEMGain(self):
        server = yield self.cxn.get_server(self.andor_servername)
        error, emgain = yield server.get_emccd_gain(self.andor_serial_number)
        self.DisplayEMGain(emgain)
        
    def DisplayEMGain(self, emgain):
        self.emgainBox.setValue(emgain)
    
    @inlineCallbacks
    def getAcquisitionTiming(self):
        server = yield self.cxn.get_server(self.andor_servername)
        error, exposure, accumulation, kinetic = yield server.get_acquisition_timings(self.andor_serial_number)
        self.DisplayExposure(exposure)
        self.DisplayAccumulation(accumulation)
        self.DisplayKinetic(kinetic)
    
    def DisplayExposure(self, exposure):
        self.exposureBox.display(exposure)
    
    def DisplayAccumulation(self, accumulation):
        self.accumulationBox.display(accumulation)
        
    def DisplayKinetic(self, kinetic):
        self.kineticBox.display(kinetic)
        
    @inlineCallbacks
    def getReadOutTime(self):
        server = yield self.cxn.get_server(self.andor_servername)
        error, readoutTime = yield server.get_read_out_time(self.andor_serial_number)
        self.DisplayReadOutTime(readoutTime)
        
    def DisplayReadOutTime(self, readoutTime):
        self.readoutBox.display(readoutTime)
        
    def handle_click(self, mouseClickEvent):
        print(mouseClickEvent.double())
        if mouseClickEvent.double():
            scenePos = mouseClickEvent.scenePos()
            print(scenePos)
            pos = self.imageView.getView().mapSceneToView(scenePos)
            if not hasattr(self, 'crosshairs'):
                self.crosshairs = {
                    'x': pg.InfiniteLine(angle=90, pen='g'),
                    'y': pg.InfiniteLine(angle=0, pen='g'),
                    }
                self.imageView.addItem(self.crosshairs['x'])
                self.imageView.addItem(self.crosshairs['y'])
            
            self.crosshairs['x'].setPos(pos.x())
            self.crosshairs['y'].setPos(pos.y())
        
    def receive_update(self, c, signal):
        signal = json.loads(signal)
        for key, value in signal.items():
            if key == self.name:
                self.getAll()
                record_path = value['record_path']
                record_type = value['record_type']
                image_path = self.data_directory.format(*record_path)
                image_path = os.path.join(self.data_directory, *record_path.split('/')) + '.hdf5'
                self.plot(image_path, record_type)
                
    def plot(self, image_path, record_type):
        image = process_image(image_path, record_type)
        image = np.rot90(image)
        self.imageView.setImage(image, autoRange=False, autoLevels=False)

    def closeEvent(self, x):
        self.reactor.stop()


