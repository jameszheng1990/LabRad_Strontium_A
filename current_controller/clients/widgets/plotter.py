import json

import os
import sys
import time, datetime

from PyQt5 import QtGui, QtCore, QtWidgets
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class ScanArray(FigureCanvas):
    def __init__(self,parent):
        self.parent = parent        
        self.populate()
#        self.make_figure(self.x, self.y)
        
    def populate(self):
        self.fig = Figure()
        FigureCanvas.__init__(self, self.fig)
        self.axes = self.fig.add_subplot(111)
        self.axes.spines['top'].set_visible(True)
        self.axes.spines['bottom'].set_visible(True)
        self.axes.spines['left'].set_visible(True)
        self.axes.spines['right'].set_visible(True)
        self.axes.get_xaxis().set_visible(True)
        self.axes.get_yaxis().set_visible(True)
        self.axes.set_xlabel('Laser Current [mA]')
        self.axes.set_ylabel('Monitor Current [uA]')
        for label in (self.axes.get_xticklabels() + self.axes.get_yticklabels()):
            label.set_fontname('Arial')
            label.set_fontsize(6)
        self.setContentsMargins(0, 0, 0, 0)
#        self.fig.subplots_adjust(left=0, bottom = 0, right=1, top=1)
        
        
    def make_figure(self, x=None, y=None, path=None):
        self.axes.cla()
        self.axes.plot(x, y)
        self.axes.set_xlabel('Laser Current [mA]')
        self.axes.set_ylabel('Monitor Current [uA]')
        for label in (self.axes.get_xticklabels() + self.axes.get_yticklabels()):
            label.set_fontname('Arial')
            label.set_fontsize(6)
        self.fig.savefig(path)
        self.draw()

class PlotterClient(QtWidgets.QWidget):
    def __init__(self, reactor, parent=None):
        super(PlotterClient, self).__init__(parent)
        self.reactor = reactor
        self.parent = parent
        self.populate()
        
        
    def populate(self):
        self.array = ScanArray(self.parent)
        self.array.scrollArea = QtWidgets.QScrollArea()
        self.array.scrollArea.setWidget(self.array)
        self.array.scrollArea.setWidgetResizable(True)
        self.array.scrollArea.setHorizontalScrollBarPolicy(1)
        self.array.scrollArea.setVerticalScrollBarPolicy(1)
        self.array.scrollArea.setFrameShape(0)
        
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.array.scrollArea)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
    
    def plot(self, x, y, path):
        self.array.make_figure(x, y, path)