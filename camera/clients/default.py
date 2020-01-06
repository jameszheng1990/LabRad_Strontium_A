from PyQt5 import QtWidgets, QtCore
import h5py
import json
import matplotlib as mpl
import numpy as np
import os
import sys
from time import strftime

from twisted.internet.defer import inlineCallbacks

from client_tools.connection import connection
import pyqtgraph as pg
from camera.clients.cmap_to_colormap import cmapToColormap

cmap = mpl.cm.get_cmap('magma')
MyColorMap = pg.ColorMap(*zip(*cmapToColormap(cmap)))

from camera.clients.data_tools.process_image import process_image

class CameraClient(QtWidgets.QWidget):
    servername = 'camera'
    update_id = np.random.randint(0, 2**31 - 1)
    data_directory = os.path.join(os.getenv('LABRADDATA'), 'data')
    name = None

    def __init__(self, reactor):
        super(CameraClient, self).__init__()
        self.reactor = reactor
        self.populate()
        self.connect()
    
    @inlineCallbacks
    def connect(self):
        self.cxn = connection()
        cname = '{} - {} - client'.format(self.servername, self.name)
        yield self.cxn.connect(name=cname)
        self.context = yield self.cxn.context()
        yield self.connectSignals()

    def populate(self):
        self.imageView = pg.ImageView()
        self.imageView.setColorMap(MyColorMap)
        self.imageView.show()
        
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.layout.addWidget(self.imageView)
        self.setLayout(self.layout)
        self.setWindowTitle('{} - {} - client'.format(
                            self.servername, self.name))
    
    @inlineCallbacks
    def connectSignals(self):
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id)
        yield server.addListener(listener=self.receive_update, source=None, 
                                 ID=self.update_id)
        self.imageView.scene.sigMouseClicked.connect(self.handle_click)

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


