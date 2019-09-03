#!/usr/bin/python3
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            #QApplication.quit()
        if event.key() == Qt.Key_Return and (event.modifiers() & Qt.ControlModifier):
            self.renderWidget.pasteClipboard()
            self.renderWidget.renderShader()

    def initState(self):
        self.autosaveInterval = 30e3 # every 30 sec

    def initUI(self):
        self.drumWidget = MayDrumatizer()
        self.renderWidget = MayRenderer()
        # ... moar widscheddddz!

        self.initLayouts()

    def initLayouts(self):
        self.mainSplit = QHBoxLayout()

        self.mainSplit.addWidget(self.drumWidget, 66)
        self.mainSplit.addWidget(self.renderWidget, 33)

        self.setLayout(self.mainSplit)

    def autosave(self):
        print('mock autosave...')

if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(App.exec_())