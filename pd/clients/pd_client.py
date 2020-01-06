import json
import h5py
import os
from PyQt5 import QtWidgets, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from client_tools.connection import connection

class MplCanvas(FigureCanvas):
    def __init__(self):
        # fig, ax = plt.subplots(1)
        # self.fig = fig
        # self.ax = ax
        self.fig = Figure()

        self.fig.set_tight_layout(True)

        FigureCanvas.__init__(self, self.fig)
        self.ax = self.fig.add_subplot(111)
        self.setFixedSize(800, 500)

class PDViewer(QtWidgets.QDialog):
    pd_name = None
    data_dir = None

    def __init__(self, reactor, cxn=None):
        super(PDViewer, self).__init__(None)
        self.reactor = reactor
        self.cxn = cxn
        print(self.data_dir)

        self.update_id = np.random.randint(0, 2**31 - 1)
        self.loading = False
        self.connect()
   
    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection()
            cname = 'pd - {} - client'.format(self.pd_name)
            yield self.cxn.connect(name=cname)

        self.populate()
        yield self.connect_signals()

    def populate(self):
        self.setWindowTitle(self.pd_name)
        self.canvas = MplCanvas()
        self.nav = NavigationToolbar(self.canvas, self)
        
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.layout.addWidget(self.nav)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)
       
        width = self.canvas.width()
        height = self.nav.height() + self.canvas.height() + 20
        self.setFixedSize(width, height)
        self.setWindowTitle('pd_viewer')

    @inlineCallbacks
    def connect_signals(self):
        pd_server = yield self.cxn.get_server('pd')
        yield pd_server.signal__update(self.update_id)
        yield pd_server.addListener(listener=self.receive_update, source=None, 
                                     ID=self.update_id)

    def receive_update(self, c, signal_json):
        signal = json.loads(signal_json)
        for message_type, message in signal.items():
            device_message = message.get(self.pd_name)
            if (message_type == 'record') and (device_message is not None):
                print(message_type, message)
                self.replot(device_message)

    def replot(self, rel_data_path):
        abs_data_path = os.path.join(self.data_dir, rel_data_path) + '.hdf5'
        save_data_path = os.path.join(self.data_dir, rel_data_path) + '.png'
        with h5py.File(abs_data_path) as h5f:
            # gnd = h5f['gnd']
            # exc = h5f['exc']
            # bac = h5f['bac']
            # self.canvas.ax.clear()
            # self.canvas.ax.plot(gnd, label='gnd')
            # self.canvas.ax.plot(exc, label='exc')
            # self.canvas.ax.plot(bac, label='bac')
            # self.canvas.ax.legend()
            exp = h5f['exp']
            self.canvas.ax.clear()
            self.canvas.ax.plot(exp, label='exp')
            self.canvas.ax.legend()
            self.canvas.ax.set_xlabel('Points')
            self.canvas.ax.set_ylabel('Voltage [V]')
        self.canvas.fig.savefig(save_data_path)
        self.canvas.draw()

    
    def closeEvent(self, x):
        self.reactor.stop()
        

class MyViewer(PDViewer):
    pd_name = 'ThorlabsPD'
    data_dir = os.path.join(os.getenv('LABRADDATA'),'data')

if __name__ == '__main__':
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    from client_tools import qt5reactor 
    qt5reactor.install()
    from twisted.internet import reactor
    
    widget = MyViewer(reactor)
    widget.show()
    reactor.suggestThreadPoolSize(10)
    reactor.run()
