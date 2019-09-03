from PyQt5.QtWidgets import *

from envelopewidget import EnvelopeWidget

class MayDrumatizer(QWidget):

    def __init__(self):
        super().__init__()
        self.initLayouts()

    def initLayouts(self):
        self.mainLayout = QVBoxLayout()

        self.layerWidget = QGroupBox('Drum Layers')
        self.ampEnvWidget = QGroupBox('Amplitude Envelopes')
        self.freqEnvWidget = QGroupBox('Frequency Envelopes')
        self.distEnvWidget = QGroupBox('Distortion Envelopes')

        # layer widget
        # amp envelope widget - todo: do something smart to combine layers
        ampEnvWidget = EnvelopeWidget()
        ampLayout = QHBoxLayout()
        ampLayout.addWidget(ampEnvWidget)
        self.ampEnvWidget.setLayout(ampLayout)
        ampEnvWidget.setMaxDimensions(2, 1)
        ampEnvWidget.addPoint(0, 0, fixedTime = True, fixedValue = True)
        ampEnvWidget.addPoint(0.05, 1, fixedValue = True, name = 'attack')
        ampEnvWidget.addPoint(0.5, .5, name = 'decay')
        ampEnvWidget.addPoint(2, 0, fixedValue = True, name = 'release')

        # freq envelope widget
        freqEnvWidget = EnvelopeWidget()
        freqLayout = QHBoxLayout()
        freqLayout.addWidget(freqEnvWidget)
        self.freqEnvWidget.setLayout(freqLayout)

        # dist (fx) envelope widget
        distEnvWidget = EnvelopeWidget()
        distLayout = QHBoxLayout()
        distLayout.addWidget(distEnvWidget)
        self.distEnvWidget.setLayout(distLayout)

        self.mainLayout.addWidget(self.layerWidget, 2)
        self.mainLayout.addWidget(self.ampEnvWidget, 1)
        self.mainLayout.addWidget(self.freqEnvWidget, 1)
        self.mainLayout.addWidget(self.distEnvWidget, 1)

        self.setLayout(self.mainLayout)


# deadline: hard cyber

# vortex: nordic horror industrial (BLACKHNO)

# UNC: die grüne demo

# revision: tunguska / tschernobyl
# game: johann lafers helilandeplatz