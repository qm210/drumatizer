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
from mayStyle import mayStyle

class MainWindow(QWidget):

    autosave_file = 'auto.drumset'

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

            if event.key() == Qt.Key_B:
                currentDrum = self.drumWidget.currentDrum()
                print("called", currentDrum)
                if currentDrum:
                    self.renderWidget.renderShaderAndPlay(file = f'{currentDrum.name}.wav')

            if event.key() == Qt.Key_S:
                print(f"Saving to {self.autosave_file}...")
                self.autosave()

            if event.key() == Qt.Key_L:
                print(f"Loading from {self.autosave_file}...")
                self.autoload()

            if event.key() == Qt.Key_P:
                self.drumWidget.purgeUnusedEnvelopes()

            if event.key() == Qt.Key_T:
                self.drumWidget.changeWidgetDimensions()

        # no CTRL pressed
        else:
            if event.key() == Qt.Key_Return:
                self.renderWidget.stopShader()

            if event.key() == Qt.Key_I:
                self.drumWidget.changeWidgetDimensions(valueZoom = 0.91)
            if event.key() == Qt.Key_K:
                self.drumWidget.changeWidgetDimensions(valueZoom = 1.10)
            if event.key() == Qt.Key_J:
                self.drumWidget.changeWidgetDimensions(timeZoom = 1.10)
            if event.key() == Qt.Key_L:
                self.drumWidget.changeWidgetDimensions(timeZoom = 0.91)


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
            self.drumWidget.drumImport(name = self.autosave_file)
        except FileNotFoundError:
            self.drumWidget.initData()

    def autosave(self):
        try:
            self.drumWidget.drumExport(name = self.autosave_file)
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
