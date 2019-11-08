from PyQt5 import QtGui, QtWidgets

class AddDltButton(QtWidgets.QWidget):
    def __init__(self):
        super(AddDltButton, self).__init__(None)
        self.add = QtWidgets.QPushButton('+')
        self.dlt = QtWidgets.QPushButton('-')
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.add)
        self.layout.addWidget(self.dlt)
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)


class AddDltRow(QtWidgets.QWidget):
    """ row of '+'/'-' """
    def __init__(self, parent):
        super(AddDltRow, self).__init__(None)
        self.parent = parent
        self.populate()

    def populate(self):
        self.buttons = [AddDltButton() for i in range(self.parent.max_columns)]
        self.layout = QtWidgets.QHBoxLayout()
        for ad in self.buttons:
            self.layout.addWidget(ad)
        self.setLayout(self.layout)
        
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
    
    def displaySequence(self, sequence):
        shown = sum([1 for b in self.buttons if not b.isHidden()])
        num_to_show = len(sequence[self.parent.timing_channel])
        if shown > num_to_show:
            for b in self.buttons[num_to_show: shown][::-1]:
                b.hide()
        elif shown < num_to_show:
            for b in self.buttons[shown:num_to_show]:
                b.show()

    def updateParameters(self, parameter_values):
        pass


