from PyQt5 import QtWidgets


class DoubleInputDialog(QtWidgets.QDialog):

    def __init__(self, *args, time = 0, value = 0, maxValue = 1, **kwargs):
        super(DoubleInputDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle('enter time/value')

        self.PRECISION = 3

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(QtWidgets.QLabel("time / sec:"))
        self.timeBox = QtWidgets.QDoubleSpinBox()
        self.timeBox.setDecimals(self.PRECISION)
        self.timeBox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.timeBox.setValue(time)
        self.timeBox.selectAll()
        #self.timeBox.setFocus(True)
        self.layout.addWidget(self.timeBox)

        self.layout.addWidget(QtWidgets.QLabel("value:"))
        self.valueBox = QtWidgets.QDoubleSpinBox()
        self.valueBox.setMaximum(maxValue)
        self.valueBox.setDecimals(self.PRECISION)
        self.valueBox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.valueBox.setValue(value)
        self.layout.addWidget(self.valueBox)

        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

    def open(self):
        if self.exec_() == QtWidgets.QDialog.Accepted:
            return round(self.timeBox.value(), self.PRECISION), round(self.valueBox.value(), self.PRECISION)
        else:
            return None, None