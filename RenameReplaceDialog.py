from PyQt5 import QtWidgets, QtCore


class RenameReplaceDialog(QtWidgets.QDialog):

    RENAME, REPLACE = range(2)

    def __init__(self, parent, *args, **kwargs):
        self.name = kwargs.pop('name') if 'name' in kwargs else ''
        super(RenameReplaceDialog, self).__init__(parent, *args, **kwargs)
        self.setWindowTitle('Rename / Replace')

        self.replaceButton = QtWidgets.QPushButton('Replace Current', self)
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, self)
        self.buttonBox.addButton(self.replaceButton, QtWidgets.QDialogButtonBox.AcceptRole)

        self.buttonBox.accepted.connect(self.accept)
        self.replaceButton.clicked.connect(self.replaceCurrent)
        self.buttonBox.rejected.connect(self.reject)

        self.editName = QtWidgets.QLineEdit(self)
        self.editName.setPlaceholderText('New name...')
        self.editName.setText(self.name)
        self.editName.setFocus(True)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.editName)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.mode = self.RENAME

    def getName(self):
        return self.editName.text()

    def replaceCurrent(self):
        self.mode = self.REPLACE
        self.accept()
