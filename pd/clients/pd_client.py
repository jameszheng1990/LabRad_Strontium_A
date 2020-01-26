import json
import h5py
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from client_tools.connection import connection
from client_tools.widgets import NeatSpinBox
from client_tools.widgets import ClickableLabel

from pd.clients.data_tools.process_signal import process_signal
from pd.clients.data_tools.process_signal import fit_loading

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
    
    boxHeight = 50
    boxWidth = 220

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

        self.nameLabel1 = ClickableLabel('Parameter 1: ')
        self.nameLabel1.setFont(QtGui.QFont("Times", 18))
        self.nameBox1 = QtWidgets.QLineEdit()
        self.nameBox1.setFixedSize(self.boxWidth, self.boxHeight)
        
        self.valueLabel1 = ClickableLabel('Value 1: ')
        self.valueLabel1.setFont(QtGui.QFont("Times", 18))        
        self.valueBox1 = NeatSpinBox()
        self.valueBox1.setFixedSize(self.boxWidth, self.boxHeight)

        self.nameLabel2 = ClickableLabel('Parameter 2: ')
        self.nameLabel2.setFont(QtGui.QFont("Times", 18))
        self.nameBox2 = QtWidgets.QLineEdit()
        self.nameBox2.setFixedSize(self.boxWidth, self.boxHeight)
        
        self.valueLabel2 = ClickableLabel('Value 2: ')
        self.valueLabel2.setFont(QtGui.QFont("Times", 18))        
        self.valueBox2 = NeatSpinBox()
        self.valueBox2.setFixedSize(self.boxWidth, self.boxHeight)
        
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(1)
        self.layout.setContentsMargins(2, 2, 2, 2)
        
        self.layout.addWidget(self.nav, 1, 0, 1, 5)
        self.layout.addWidget(self.canvas, 2, 0, 4, 4)
        
        self.layout.addWidget(self.nameLabel1, 7, 0, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.nameBox1, 7, 1)
        self.layout.addWidget(self.valueLabel1, 7, 2, 1, 1,
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.valueBox1, 7, 3)

        # self.layout.addWidget(self.nameLabel2, 8, 0, 1, 1,
        #                       QtCore.Qt.AlignRight)
        # self.layout.addWidget(self.nameBox2, 8, 1)
        # self.layout.addWidget(self.valueLabel2, 8, 2, 1, 1,
        #                       QtCore.Qt.AlignRight)
        # self.layout.addWidget(self.valueBox2, 8, 3)
        
        self.setLayout(self.layout)
       
        width = self.canvas.width() + 20
        height = self.nav.height() + self.canvas.height() + self.nameBox1.height()*2 + 60
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
            elif (message_type == 'loading_rate') and (device_message is not None):
                print(message_type, message)
                sample_rate = message.get('sample_rate')
                loading_rate, loss_rate, volt_to_number = process_signal(sample_rate, device_message, message_type)
                # self.GetParameter()
                # self.GetValue()
                self.replot_loading(sample_rate, device_message, loading_rate, loss_rate)

    def replot(self, rel_data_path):
        abs_data_path = os.path.join(self.data_dir, rel_data_path) + '.hdf5'
        save_data_path = os.path.join(self.data_dir, rel_data_path) + '.png'
        with h5py.File(abs_data_path) as h5f:
            exp = h5f['exp']
            self.canvas.ax.clear()
            self.canvas.ax.plot(exp, label='exp')
            self.canvas.ax.legend()
            self.canvas.ax.set_xlabel('Points')
            self.canvas.ax.set_ylabel('Voltage [V]')
        self.canvas.fig.savefig(save_data_path)
        self.canvas.draw()
        
    def replot_loading(self, sample_rate, rel_data_path, loading_rate, loss_rate):
        abs_data_path = os.path.join(self.data_dir, rel_data_path) + '.hdf5'
        save_data_path = os.path.join(self.data_dir, rel_data_path) + '.png'
        with h5py.File(abs_data_path) as h5f:
            exp = h5f['exp']
            self.canvas.ax.clear()
            x = np.linspace(0, len(exp)/sample_rate, len(exp))
            self.canvas.ax.plot(x, exp, label='exp', c='black')
            self.canvas.ax.plot(x, fit_loading(x, loading_rate, loss_rate), label='fitted', c='red',
                          linestyle='dashed')
            self.canvas.ax.legend()
            self.canvas.ax.set_xlabel('Time [s]')
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
