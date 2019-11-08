import os
import sys
sys.path.append(os.getenv('PROJECT_LABRAD_TOOLS_PATH'))

from PyQt5 import QtGui, QtWidgets

from client_tools.widgets import SuperSpinBox

class DurationRow(QtWidgets.QWidget):
    """ row of boxes for sequence timing """
    def __init__(self, parent):
        super(DurationRow, self).__init__(None)
        self.parent = parent
        self.populate()

    def populate(self):
        units =  [(0, 's'), (-3, 'ms'), (-6, 'us'), (-9, 'ns')]
        self.boxes = [SuperSpinBox([500e-9, 60], units) for i in range(self.parent.max_columns)]
        self.layout = QtWidgets.QHBoxLayout()
        for db in self.boxes:
            self.layout.addWidget(db)
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

#    def setSequence(self, sequence):
#        self.sequence = sequence
    
    def displaySequence(self, sequence):
        shown = sum([1 for b in self.boxes if not b.isHidden()])
        num_to_show = len(sequence[self.parent.timing_channel])
        if shown > num_to_show:
            for b in self.boxes[num_to_show:shown][::-1]:
                b.hide()
        elif shown < num_to_show:
            for b in self.boxes[shown:num_to_show]:
                b.show()
        for b, s in zip(self.boxes[:num_to_show], sequence[self.parent.timing_channel]):
            b.display(s['dt'])

    def updateParameters(self, sequence_parameters):
        pass
    


