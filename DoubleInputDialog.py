from PyQt5 import QtWidgets, QtCore


class DoubleInputDialog(QtWidgets.QDialog):

    def __init__(self, parent, *args, time = 0, value = 0, maxValue = 1, fixedTime = False, fixedValue = False, name = None, point = None, **kwargs):
        super(DoubleInputDialog, self).__init__(parent, *args, **kwargs)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose) # <-- this leads to a RuntimeError

        if point is not None:
            time = point.time
            value = point.value
            fixedTime = point.fixedTime
            fixedValue = point.fixedValue
            name = point.name

        self.setWindowTitle('(?)' if name is None else name)

        self.precision = 3

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.layout.addWidget(QtWidgets.QLabel("time / sec:", self))
        self.timeBox = QtWidgets.QDoubleSpinBox(self)
        self.timeBox.setDecimals(self.precision)
        self.timeBox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.timeBox.setValue(time)
        self.timeBox.setEnabled(not fixedTime)
        self.layout.addWidget(self.timeBox)

        self.layout.addWidget(QtWidgets.QLabel("value:", self))
        self.valueBox = QtWidgets.QDoubleSpinBox(self)
        self.valueBox.setMaximum(maxValue)
        self.valueBox.setDecimals(self.precision)
        self.valueBox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.valueBox.setValue(value)
        self.valueBox.setEnabled(not fixedValue)
        self.layout.addWidget(self.valueBox)

        if not fixedTime:
            self.timeBox.selectAll()
        elif not fixedValue:
            self.valueBox.selectAll()

        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)
