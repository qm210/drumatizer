from PyQt5 import QtWidgets, QtCore


class SettingsDialog(QtWidgets.QDialog):

    def __init__(self, parent, *args, **kwargs):
        # catch extra parameters, e.g. for type of envelope, here
        self.type = kwargs.pop('type') if 'type' in kwargs else None
        self.name = kwargs.pop('name') if 'name' in kwargs else None
        super(SettingsDialog, self).__init__(parent, *args, **kwargs)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose) # <-- gives RuntimeError
        # self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)

        if self.name:
            self.mode = 'edit'
            self.setWindowTitle('Edit {}'.format(self.type))
        else:
            self.mode = 'new'
            self.setWindowTitle('New {} env.'.format(self.type))

        self.PRECISION = 3

        self.cloneButton = QtWidgets.QPushButton('Clone Current', self)
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        self.buttonBox.addButton(self.cloneButton, QtWidgets.QDialogButtonBox.AcceptRole)

        self.buttonBox.accepted.connect(self.accept)
        self.cloneButton.clicked.connect(self.cloneCurrent)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.editName = QtWidgets.QLineEdit(self)
        self.editName.setPlaceholderText('Envelope Name')
        self.editName.setFocus(True)
        self.layout.addWidget(self.editName)

        if self.name:
            self.editName.setText(self.name)

        self.editPointNumber = QtWidgets.QSpinBox(self)
        self.editPointNumber.setSuffix(' points')
        if self.type == 'frequency':
            self.editPointNumber.setValue(3)
            self.editPointNumber.setRange(1, 3)
        elif self.type == 'amplitude':
            self.editPointNumber.setValue(4)
            self.editPointNumber.setRange(2, 10)
        else:
            self.editPointNumber.setValue(4)
            self.editPointNumber.setRange(1, 10)
        self.layout.addWidget(self.editPointNumber)

        # TODO: implement this, until then -- greyed out!
        self.editPointNumber.setEnabled(False)

        self.editSinglePointValue = QtWidgets.QDoubleSpinBox(self)
        self.editSinglePointValue.setPrefix('const value = ')
        self.editSinglePointValue.setValue(1)
        self.editSinglePointValue.setDecimals(3)
        self.editSinglePointValue.setRange(1e-3, 2e4)
        self.editSinglePointValue.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.editSinglePointValue.hide()
        self.layout.addWidget(self.editSinglePointValue)
        self.editPointNumber.valueChanged.connect(self.toggleSinglePoint)

        self.verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.layout.addItem(self.verticalSpacer)

        self.assignToLayerChkBox = QtWidgets.QCheckBox('Assign to current layer now', self)
        self.layout.addWidget(self.assignToLayerChkBox)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.clone = False

    def getName(self):
        return self.editName.text() or '(unnamed)'

    def getPointNumber(self):
        return self.editPointNumber.value()

    def getSinglePointValue(self):
        return self.editSinglePointValue.value()

    def getWhetherToAssign(self):
        return self.assignToLayerChkBox.isChecked()

    def cloneCurrent(self):
        self.clone = True
        self.accept()

    def toggleSinglePoint(self):
        self.editSinglePointValue.setVisible(self.editPointNumber.value() == 1)