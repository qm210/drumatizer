from PyQt5 import QtWidgets, QtCore


class SettingsDialog(QtWidgets.QDialog):

    EDIT, NEW, CLONE = range(3)

    def __init__(self, parent, envelope, *args, **kwargs):
        # catch extra parameters, e.g. for type of envelope, here
        self.mode = kwargs.pop('mode') if 'mode' in kwargs else SettingsDialog.EDIT
        self.type = envelope.type
        self.name = envelope.name if self.mode == SettingsDialog.EDIT else ''
        super(SettingsDialog, self).__init__(parent, *args, **kwargs)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose) # <-- gives RuntimeError
        # self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)

        if self.mode == SettingsDialog.EDIT:
            self.setWindowTitle('Edit {}'.format(self.type))
        else:
            self.setWindowTitle('New {} env.'.format(self.type))

        self.cloneButton = QtWidgets.QPushButton('Clone Current', self) # TODO: handle case "there is no current" :P
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
            self.editPointNumber.setRange(1, 3)
        elif self.type == 'amplitude':
            self.editPointNumber.setRange(2, 10)
        else:
            self.editPointNumber.setRange(1, 10)
        self.editPointNumber.setValue(envelope.pointNumber())
        self.layout.addWidget(self.editPointNumber)

        self.editSinglePointValue = QtWidgets.QDoubleSpinBox(self)
        self.editSinglePointValue.setPrefix('const value = ')
        self.editSinglePointValue.setDecimals(3)
        self.editSinglePointValue.setRange(1e-3, 2e4)
        self.editSinglePointValue.setValue(envelope.points[0].value)
        self.editSinglePointValue.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        if envelope.pointNumber() > 1:
            self.editSinglePointValue.hide()
        self.layout.addWidget(self.editSinglePointValue)
        self.editPointNumber.valueChanged.connect(self.toggleSinglePoint)

        self.verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.layout.addItem(self.verticalSpacer)

        # TODO: "What to randomize..?" Times? Values? Both?
        # TODO: change "maxTime", "maxValue"..? - use Strg+T for now

        self.assignToLayerChkBox = QtWidgets.QCheckBox('Assign to current layer now', self)
        self.layout.addWidget(self.assignToLayerChkBox)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.clone = False

    def getName(self):
        return self.editName.text()

    def getPointNumber(self):
        return self.editPointNumber.value()

    def getSinglePointValue(self):
        return self.editSinglePointValue.value()

    def getWhetherToAssign(self):
        return self.assignToLayerChkBox.isChecked()

    def cloneCurrent(self):
        self.mode = SettingsDialog.CLONE
        self.accept()

    def toggleSinglePoint(self):
        self.editSinglePointValue.setVisible(self.editPointNumber.value() == 1)