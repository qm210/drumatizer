#############################################################
#
#       the new aMaySyn Drumatizer (Matzes Drum Editor)
#       ihr seid erstmal ruhig
#       Copyright 2019 qm / Team210
#
#############################################################

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, QTimer

from mayDrumatizer import MayDrumatizer
from mayRenderer import MayRenderer
from mayStyle import mayStyle

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('QoodMood')
        self.setGeometry(300,0,1600,1000)
        self.initState()
        self.initUI()
        self.show()

        self.timerAutosave = QTimer(self)
        self.timerAutosave.timeout.connect(self.autosave)
        self.timerAutosave.start(self.autosaveInterval)
        self.renderWidget.shouldsave.connect(self.autosave)

        self.autoload()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            #QApplication.quit()

        # CTRL pressed
        if event.modifiers() & Qt.ControlModifier:

            if event.key() == Qt.Key_Return:
                self.renderWidget.pasteClipboard()
                self.renderWidget.renderShaderAndPlay()

            if event.key() == Qt.Key_S:
                self.autosave()

            if event.key() == Qt.Key_L:
                self.autoload()

    def initState(self):
        self.autosaveInterval = 30e3 # every 30 sec

    def initUI(self):
        self.drumWidget = MayDrumatizer(self)
        self.renderWidget = MayRenderer(self)
        self.drumWidget.shaderCreated.connect(self.sendShaderToRenderer)

        self.initLayouts()
        self.setStyleSheet(mayStyle)

    def initLayouts(self):
        self.mainSplit = QHBoxLayout()
        self.mainSplit.addWidget(self.drumWidget, 68)
        self.mainSplit.addWidget(self.renderWidget, 32)
        self.setLayout(self.mainSplit)

    def autoload(self):
        try:
            self.drumWidget.drumImport(name = 'auto.drumset')
        except FileNotFoundError:
            self.drumWidget.initData()

    def autosave(self):
        try:
            self.drumWidget.drumExport(name = 'auto.drumset')
        except Exception as ex:
            print('Autosave failed...', ex)

    def sendShaderToRenderer(self, shaderSource):
        self.renderWidget.paste(shaderSource)
        self.renderWidget.renderShaderAndPlay()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    returnCode = app.exec_()
    # print('\n'.join(repr(w) for w in app.allWidgets()))
    sys.exit(returnCode)