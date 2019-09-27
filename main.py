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

    autosaveFile = 'auto.drumset'

    def __init__(self):
        super().__init__()
        self.setWindowTitle('QMs Drumatizer')
        self.setGeometry(300,0,1600,1000)
        self.initState()
        self.initUI()
        self.show()
        self.drumWidget.setFocus()

        self.timerAutosave = QTimer(self)
        self.timerAutosave.timeout.connect(self.autosave)
        self.timerAutosave.start(self.autosaveInterval)

        # TODO: organize command line arguments
        if '-init' in sys.argv:
            self.drumWidget.initData()
        else:
            self.autoload()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

        elif event.key() == Qt.Key_F1:
            self.drumWidget.debugOutput()


        if event.modifiers() & Qt.ControlModifier:

            if event.key() == Qt.Key_Return:
                self.renderWidget.pasteClipboard()
                self.renderWidget.renderShaderAndPlay()

            if event.key() == Qt.Key_B:
                currentDrum = self.drumWidget.currentDrum()
                print("called", currentDrum)
                if currentDrum:
                    self.renderWidget.renderShaderAndPlay(file = f'{currentDrum.name}.wav')

            if event.key() == Qt.Key_A:
                print(f"Saving to {self.autosaveFile}...")
                self.autosave()

            if event.key() == Qt.Key_S:
                self.drumWidget.purgeUnusedEnvelopes()
                # self.drumWidget.drumExport(useCurrentDrumName = True)
                self.autosaveFile = self.drumWidget.lastExportedDrumset or self.autosaveFile
                self.drumWidget.drumExport(name = self.autosaveFile)

            if event.key() == Qt.Key_L:
                print(f"Loading from {self.autosaveFile}...") # TODO: this doesn't make much sense, I guess, if autosaveInterval is small
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
        self.drumWidget.shaderCreated.connect(self.sendShaderToRenderer)
        self.drumWidget.synDrumCreated.connect(self.sendDrumatizeDetailsToRenderer)
        self.drumWidget.selectDrum.connect(self.sendSynDumpParametersToRenderer)

        self.renderWidget = MayRenderer(self)
        self.renderWidget.shouldSave.connect(self.autosave)

        self.initLayouts()
        self.setStyleSheet(mayStyle)

    def initLayouts(self):
        self.mainSplit = QHBoxLayout()
        self.mainSplit.addWidget(self.drumWidget, 68)
        self.mainSplit.addWidget(self.renderWidget, 32)
        self.setLayout(self.mainSplit)

    def autoload(self):
        try:
            self.drumWidget.drumImport(name = self.autosaveFile)
        except FileNotFoundError:
            self.drumWidget.initData()

    def autosave(self):
        try:
            self.drumWidget.setSynDumpParameters(self.renderWidget.useSynDump, self.renderWidget.synFileName, self.renderWidget.synDrumName)
            self.drumWidget.drumExport(name = self.autosaveFile)
        except Exception as ex:
            print('Autosave failed...', ex)

    def sendShaderToRenderer(self, shaderSource):
        self.renderWidget.paste(shaderSource)
        self.renderWidget.renderShaderAndPlay()

    def sendDrumatizeDetailsToRenderer(self, dL, dR, envCode, releaseTime):
        self.renderWidget.dumpInSynFile(dL, dR, envCode, releaseTime)

    def sendSynDumpParametersToRenderer(self):
        self.renderWidget.setSynDumpParameters(*(self.drumWidget.getSynDumpParameters()))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    returnCode = app.exec_()
    # print('\n'.join(repr(w) for w in app.allWidgets()))
    sys.exit(returnCode)
