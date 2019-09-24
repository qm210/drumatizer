#########################################################################
## Drumatize Section of Drumatizer (development started at 2019/09/03)
## -- Renderer Section was written some days before... ;)
##
## by QM / Team210
#########################################################################

from PyQt5.QtWidgets import * # pylint: disable=unused-import
from PyQt5.QtCore import Qt, pyqtSignal, QItemSelectionModel, QFile, QTextStream
from copy import deepcopy
from functools import partial
from os import path
import json

from DrumModel import *
from LayerModel import *
from EnvelopeModel import *
from EnvelopeWidget import EnvelopeWidget
from SettingsDialog import SettingsDialog
from RenameReplaceDialog import RenameReplaceDialog
from DoubleInputDialog import DoubleInputDialog
from Drumatizer import Drumatizer

class MayDrumatizer(QWidget):

    shaderCreated = pyqtSignal(str)
    synDrumCreated = pyqtSignal(str, str, str)
    selectDrum = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.renderTemplate = 'template.drumatize'

        self.initLayouts()
        self.initSignals()
        self.initModelView()
        self.initDefaultDrum()

    def initLayouts(self):
        # drum widget
        self.drumList = QComboBox()
        self.drumBtnAdd = QPushButton('+')
        self.drumBtnClone = QPushButton('C')
        self.drumBtnDel = QPushButton('–')
        self.drumBtnEdit = QPushButton('...')
        self.drumBtnExport = QPushButton('↗')
        self.drumBtnImport = QPushButton('↘')
        self.drumBtnRender = QPushButton('Render >>')

        self.drumLayout = QHBoxLayout()
        self.drumLayout.addWidget(QLabel('Drum:'))
        self.drumLayout.addWidget(self.drumList, 4)
        self.drumLayout.addWidget(self.drumBtnAdd)
        self.drumLayout.addWidget(self.drumBtnClone)
        self.drumLayout.addWidget(self.drumBtnDel)
        self.drumLayout.addWidget(self.drumBtnEdit)
        self.drumLayout.addWidget(self.drumBtnExport)
        self.drumLayout.addWidget(self.drumBtnImport)
        self.drumLayout.addWidget(self.drumBtnRender)

        self.drumGroup = QGroupBox()
        self.drumGroup.setLayout(self.drumLayout)

        # layer widget
        self.layerMainLayout = QHBoxLayout()
        self.layerListLayout = QVBoxLayout()
        self.layerList = QListView()
        self.layerList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.layerListLayout.addWidget(QLabel('Drum Layers'))
        self.layerListLayout.addWidget(self.layerList)

        self.layerEditor = QGroupBox()
        self.layerEditorLayout = QGridLayout()
        self.layerEditor.setLayout(self.layerEditorLayout)

        self.layerEditorName = QLineEdit()
        self.layerEditorType = QComboBox()
        self.layerEditorType.addItems(layerTypes)
        self.layerChooseAmplEnvList = QComboBox()
        self.layerChooseFreqEnvList = QComboBox()
        self.layerChooseDistEnvList = QComboBox()
        self.layerChooseDistOff = QCheckBox('no pls')
        self.layerEditorVolumeSlider = QSlider(Qt.Horizontal)
        self.layerEditorVolumeSlider.setValue(100)
        self.layerEditorVolumeSlider.setRange(0, 200)
        self.layerEditorVolumeLabel = QLabel('100%')
        self.layerEditorDetuneSlider = QSlider(Qt.Horizontal)
        self.layerEditorDetuneSlider.setRange(0, 1000)
        self.layerEditorDetuneSlider.setValue(0)
        self.layerEditorDetuneLabel = QLabel('0‰')
        self.layerEditorStereoDelaySlider = QSlider(Qt.Horizontal)
        self.layerEditorStereoDelaySlider.setRange(0, 200)
        self.layerEditorStereoDelaySlider.setValue(0)
        self.layerEditorStereoDelayLabel = QLabel('0 ppm')

        self.layerEditorLayout.addWidget(QLabel('Layer:'), 0, 0)
        self.layerEditorLayout.addWidget(self.layerEditorName, 0, 1)
        self.layerEditorLayout.addWidget(self.layerEditorType, 0, 2)
        self.layerEditorLayout.addWidget(QLabel('Amplitude Env.:'), 1, 0)
        self.layerEditorLayout.addWidget(self.layerChooseAmplEnvList, 1, 1)
        self.layerEditorLayout.addWidget(QLabel('Frequency Env.:'), 2, 0)
        self.layerEditorLayout.addWidget(self.layerChooseFreqEnvList, 2, 1)
        self.layerEditorLayout.addWidget(QLabel('Distortion Env.:'), 3, 0)
        self.layerEditorLayout.addWidget(self.layerChooseDistEnvList, 3, 1)
        self.layerEditorLayout.addWidget(self.layerChooseDistOff, 3, 2)
        self.layerEditorLayout.addWidget(QLabel('Volume:'), 4, 0)
        self.layerEditorLayout.addWidget(self.layerEditorVolumeSlider, 4, 1)
        self.layerEditorLayout.addWidget(self.layerEditorVolumeLabel, 4, 2)
        self.layerEditorLayout.addWidget(QLabel('Detune:'), 5, 0)
        self.layerEditorLayout.addWidget(self.layerEditorDetuneSlider, 5, 1)
        self.layerEditorLayout.addWidget(self.layerEditorDetuneLabel, 5, 2)
        self.layerEditorLayout.addWidget(QLabel('Stereo Delay:'), 6, 0)
        self.layerEditorLayout.addWidget(self.layerEditorStereoDelaySlider, 6, 1)
        self.layerEditorLayout.addWidget(self.layerEditorStereoDelayLabel, 6, 2)
        self.layerEditorLayout.setVerticalSpacing(7)
        # TODO: additional "phase mod by Layer" function, but THERE IS NO SPACE..!

        self.layerMenu = QVBoxLayout()
        self.layerMenu.addStretch()
        self.layerMenuBtnAdd = QPushButton('+')
        self.layerMenuBtnClone = QPushButton('C')
        self.layerMenuBtnDel = QPushButton('–')
        self.layerMenuBtnSwap = QPushButton('⇵')
        self.layerMenuMuteBox = QCheckBox('Mute')
        self.layerMenuBtnRenderSolo = QPushButton('Solo >>')
        self.layerMenuBtnRnd = QPushButton('???')
        self.layerMenu.addWidget(self.layerMenuBtnAdd)
        self.layerMenu.addWidget(self.layerMenuBtnDel)
        self.layerMenu.addWidget(self.layerMenuBtnSwap)
        self.layerMenu.addWidget(self.layerMenuBtnRnd)
        self.layerMenu.addWidget(self.layerMenuMuteBox)
        self.layerMenu.addWidget(self.layerMenuBtnRenderSolo)

        self.layerMainLayout.addLayout(self.layerListLayout, 50)
        self.layerMainLayout.addLayout(self.layerMenu, 1)
        self.layerMainLayout.addWidget(self.layerEditor, 49)

        self.layerGroup = QGroupBox()
        self.layerGroup.setLayout(self.layerMainLayout)

        # amp envelope widget - todo: do something smart to combine layers
        self.amplEnvList = QListView()
        self.amplEnvList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.amplEnvMenu = QVBoxLayout()
        self.amplEnvWidget = EnvelopeWidget(self)

        self.amplEnvMenuBtnAdd = QPushButton('+')
        self.amplEnvMenuBtnDel = QPushButton('–')
        self.amplEnvMenuBtnRnd = QPushButton('???')
        self.amplEnvMenuBtnEdit = QPushButton('...')

        self.amplEnvMenu.addStretch()
        self.amplEnvMenu.addWidget(self.amplEnvMenuBtnAdd)
        self.amplEnvMenu.addWidget(self.amplEnvMenuBtnDel)
        self.amplEnvMenu.addWidget(self.amplEnvMenuBtnEdit)
        self.amplEnvMenu.addWidget(self.amplEnvMenuBtnRnd)

        self.amplEnvLayout = QHBoxLayout()
        self.amplEnvLayout.addWidget(self.amplEnvList, 20)
        self.amplEnvLayout.addLayout(self.amplEnvMenu, 1)
        self.amplEnvLayout.addWidget(self.amplEnvWidget, 80)

        self.amplEnvMainLayout = QVBoxLayout()
        self.amplMenuLayout = QHBoxLayout()
        self.amplMenuLayout.addWidget(QLabel('Amplitude Envelopes'))
        self.amplMenuLayout.addStretch()
        self.amplEnvMenu_TryExpFitChkBox = QCheckBox('Try ExpDecay Fit')
        self.amplMenuLayout.addWidget(self.amplEnvMenu_TryExpFitChkBox)

        self.amplEnvMainLayout.addLayout(self.amplMenuLayout, 10)
        self.amplEnvMainLayout.addLayout(self.amplEnvLayout, 90)

        self.amplEnvGroup = QGroupBox()
        self.amplEnvGroup.setLayout(self.amplEnvMainLayout)

        # freq envelope widget
        self.freqEnvList = QListView()
        self.freqEnvList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.freqEnvMenu = QVBoxLayout()
        self.freqEnvWidget = EnvelopeWidget(self)

        self.freqEnvMenuBtnAdd = QPushButton('+')
        self.freqEnvMenuBtnDel = QPushButton('–')
        self.freqEnvMenuBtnRnd = QPushButton('???')
        self.freqEnvMenuBtnEdit = QPushButton('...')

        self.freqEnvMenu.addStretch()
        self.freqEnvMenu.addWidget(self.freqEnvMenuBtnAdd)
        self.freqEnvMenu.addWidget(self.freqEnvMenuBtnDel)
        self.freqEnvMenu.addWidget(self.freqEnvMenuBtnEdit)
        self.freqEnvMenu.addWidget(self.freqEnvMenuBtnRnd)

        self.freqEnvLayout = QHBoxLayout()
        self.freqEnvLayout.addWidget(self.freqEnvList, 20)
        self.freqEnvLayout.addLayout(self.freqEnvMenu, 1)
        self.freqEnvLayout.addWidget(self.freqEnvWidget, 80)

        self.freqEnvMainLayout = QVBoxLayout()
        self.freqMenuLayout = QHBoxLayout()
        self.freqMenuLayout.addWidget(QLabel('Frequency Envelopes'))
        self.freqMenuLayout.addStretch()
        self.freqEnvMenu_UsePolynomialChkBox = QCheckBox('Use Polynomial')
        self.freqMenuLayout.addWidget(self.freqEnvMenu_UsePolynomialChkBox)

        self.freqEnvMainLayout.addLayout(self.freqMenuLayout, 10)
        self.freqEnvMainLayout.addLayout(self.freqEnvLayout, 90)

        self.freqEnvGroup = QGroupBox()
        self.freqEnvGroup.setLayout(self.freqEnvMainLayout)

        # dist (fx) envelope widget
        self.distEnvList = QListView()
        self.distEnvList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.distEnvMenu = QVBoxLayout()
        self.distEnvWidget = EnvelopeWidget(self)
        # todo: at '...', choose how many points there should be (for dist and amp arbitrarily, for freq: 2 at most!)

        self.distEnvMenuBtnAdd = QPushButton('+')
        self.distEnvMenuBtnDel = QPushButton('–')
        self.distEnvMenuBtnRnd = QPushButton('???')
        self.distEnvMenuBtnEdit = QPushButton('...')

        self.distEnvMenu.addStretch()
        self.distEnvMenu.addWidget(self.distEnvMenuBtnAdd)
        self.distEnvMenu.addWidget(self.distEnvMenuBtnDel)
        self.distEnvMenu.addWidget(self.distEnvMenuBtnEdit)
        self.distEnvMenu.addWidget(self.distEnvMenuBtnRnd)

        self.distLayout = QHBoxLayout()
        self.distLayout.addWidget(self.distEnvList, 20)
        self.distLayout.addLayout(self.distEnvMenu, 1)
        self.distLayout.addWidget(self.distEnvWidget, 80)

        self.distMenuType = QComboBox()
        self.distMenuEdit_OverdriveMaximum = QDoubleSpinBox()
        self.distMenuEdit_OverdriveMaximum.setRange(0.1, 99.9)
        self.distMenuEdit_OverdriveMaximum.setValue(2.10)
        self.distMenuEdit_OverdriveMaximum.setSingleStep(0.1)
        self.distMenuEdit_OverdriveMaximum.setPrefix('max. ')
        self.distMenuEdit_WaveshapeParts = QSpinBox()
        self.distMenuEdit_WaveshapeParts.setMinimum(1)
        self.distMenuEdit_WaveshapeParts.setValue(3)
        self.distMenuEdit_WaveshapeParts.setMaximum(99)
        self.distMenuEdit_WaveshapeParts.setSuffix(' parts')
        self.distMenuEdit_LofiBits = QSpinBox()
        self.distMenuEdit_LofiBits.setRange(1, 2**16)
        self.distMenuEdit_LofiBits.setValue(2**13)
        self.distMenuEdit_LofiBits.setSingleStep(64)
        self.distMenuEdit_LofiBits.setSuffix(' bits')
        self.distMenuEdit_SaturationFactor = QDoubleSpinBox()
        self.distMenuEdit_SaturationFactor.setRange(0.1, 99.9)
        self.distMenuEdit_SaturationFactor.setValue(2.10)
        self.distMenuEdit_SaturationFactor.setSingleStep(0.1)
        self.distMenuEdit_SaturationFactor.setPrefix('x ')
        self.distMenuEdit_NA = QLineEdit()
        self.distMenuEdit_NA.setText('N/A')
        self.distMenuEdit_NA.setEnabled(False)
        self.distMenuType.addItems(distTypes)

        self.distMenuEdit = QStackedLayout()
        self.distMenuEdit.addWidget(self.distMenuEdit_OverdriveMaximum)
        self.distMenuEdit.addWidget(self.distMenuEdit_WaveshapeParts)
        self.distMenuEdit.addWidget(self.distMenuEdit_LofiBits)
        self.distMenuEdit.addWidget(self.distMenuEdit_SaturationFactor)
        self.distMenuEdit.addWidget(self.distMenuEdit_NA)

        self.distMenuEdit_PhaseModOff = QCheckBox('PhaseMod:')
        self.distMenuEdit_PhaseModAmt = QDoubleSpinBox()
        self.distMenuEdit_PhaseModAmt.setSuffix(' x')
        self.distMenuEdit_PhaseModAmt.setRange(-9.99, 9.99)
        self.distMenuEdit_PhaseModAmt.setSingleStep(0.1)
        self.distMenuEdit_PhaseModSource = QComboBox()
        self.distMenuEdit_PhaseModSource.addItem('<src>')
        self.distMenuEdit_PhaseModSource.setMaximumWidth(220)
        self.distMenuEdit_PhaseModSource.setMinimumWidth(220)

        self.distMenuLayout = QHBoxLayout()
        self.distMenuLayout.addWidget(QLabel('Distortion Envelopes'), 5)
        self.distMenuLayout.addWidget(self.distMenuType, 1)
        self.distMenuLayout.addLayout(self.distMenuEdit, 1)
        self.distMenuLayout.addStretch(2)
        self.distMenuLayout.addWidget(self.distMenuEdit_PhaseModOff, .1)
        self.distMenuLayout.addWidget(self.distMenuEdit_PhaseModAmt, .1)
        self.distMenuLayout.addWidget(self.distMenuEdit_PhaseModSource, 2)

        self.distEnvMainLayout = QVBoxLayout()
        self.distEnvMainLayout.addLayout(self.distMenuLayout)
        self.distEnvMainLayout.addLayout(self.distLayout)

        self.distEnvGroup = QGroupBox()
        self.distEnvGroup.setLayout(self.distEnvMainLayout)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.drumGroup, .5)
        self.mainLayout.addWidget(self.layerGroup, 1.5)
        self.mainLayout.addWidget(self.amplEnvGroup, 1)
        self.mainLayout.addWidget(self.freqEnvGroup, 1)
        self.mainLayout.addWidget(self.distEnvGroup, 1)

        self.setLayout(self.mainLayout)

        self.initWidgetDimensions()


    def initWidgetDimensions(self, maxTime = None, maxValue = None):
        self.maxTime = {'amplitude': 1.2, 'frequency': 1.2, 'distortion': 1.2}
        self.minValue = {'amplitude': 0, 'frequency':    20, 'distortion': 0}
        self.maxValue = {'amplitude': 1, 'frequency': 12000, 'distortion': 2}

        if maxTime is not None:
            self.maxTime['amplitude'] = maxTime
            self.maxTime['frequency'] = maxTime
            self.maxTime['distortion'] = maxTime

        if maxValue is not None:
            self.maxValue['amplitude'] = maxValue
            self.maxValue['frequency'] = maxValue
            self.maxValue['distortion'] = maxValue

        self.amplEnvWidget.setDimensions(maxTime = self.maxTime['amplitude'], minValue = self.minValue['amplitude'], maxValue = self.maxValue['amplitude'])
        self.freqEnvWidget.setDimensions(maxTime = self.maxTime['frequency'], minValue = self.minValue['frequency'], maxValue = self.maxValue['frequency'], logValue = True)
        self.distEnvWidget.setDimensions(maxTime = self.maxTime['distortion'], minValue = self.minValue['distortion'], maxValue = self.maxValue['distortion'])


    def initSignals(self):
        self.drumBtnAdd.pressed.connect(self.drumAdd)
        self.drumBtnClone.pressed.connect(self.drumClone)
        self.drumBtnDel.pressed.connect(self.drumDelete)
        self.drumBtnEdit.pressed.connect(self.drumEdit)
        self.drumBtnExport.pressed.connect(self.drumExport)
        self.drumBtnImport.pressed.connect(self.drumImport)
        self.drumBtnRender.pressed.connect(self.drumRender)

        self.layerMenuBtnAdd.pressed.connect(self.layerAdd)
        self.layerMenuBtnDel.pressed.connect(self.layerDelete)
        self.layerMenuBtnSwap.pressed.connect(self.layerSwap)
        self.layerMenuBtnRnd.pressed.connect(self.layerRandomize)
        self.layerMenuBtnRenderSolo.pressed.connect(self.layerRenderSolo)
        self.layerEditorName.textChanged.connect(self.layerSetName)
        self.layerEditorName.editingFinished.connect(self.layerRenameFresh)
        self.layerEditorType.currentTextChanged.connect(self.layerSetType)
        self.layerChooseAmplEnvList.currentIndexChanged.connect(self.amplEnvSelectIndex)
        self.layerChooseFreqEnvList.currentIndexChanged.connect(self.freqEnvSelectIndex)
        self.layerChooseDistEnvList.currentIndexChanged.connect(self.distEnvSelectIndex)
        self.layerChooseDistOff.stateChanged.connect(self.layerSetDistOff)
        self.layerEditorVolumeSlider.valueChanged.connect(self.layerSetVolume)
        self.layerEditorDetuneSlider.valueChanged.connect(self.layerSetDetune)
        self.layerEditorStereoDelaySlider.valueChanged.connect(self.layerSetStereoDelay)
        self.layerMenuMuteBox.stateChanged.connect(self.layerSetMute)

        self.amplEnvMenuBtnAdd.pressed.connect(self.amplEnvAdd)
        self.amplEnvMenuBtnDel.pressed.connect(self.amplEnvDelete)
        self.amplEnvMenuBtnRnd.pressed.connect(self.amplEnvRandomize)
        self.amplEnvMenuBtnEdit.pressed.connect(self.amplEnvEditSettings)
        self.amplEnvMenu_TryExpFitChkBox.stateChanged.connect(self.amplEnvSetTryExpFit)

        self.freqEnvMenuBtnAdd.pressed.connect(self.freqEnvAdd)
        self.freqEnvMenuBtnDel.pressed.connect(self.freqEnvDelete)
        self.freqEnvMenuBtnRnd.pressed.connect(self.freqEnvRandomize)
        self.freqEnvMenuBtnEdit.pressed.connect(self.freqEnvEditSettings)
        self.freqEnvMenu_UsePolynomialChkBox.stateChanged.connect(self.freqEnvSetUsePolynomial)

        self.distEnvMenuBtnAdd.pressed.connect(self.distEnvAdd)
        self.distEnvMenuBtnDel.pressed.connect(self.distEnvDelete)
        self.distEnvMenuBtnRnd.pressed.connect(self.distEnvRandomize)
        self.distEnvMenuBtnEdit.pressed.connect(self.distEnvEditSettings)
        self.distMenuEdit_OverdriveMaximum.valueChanged.connect(self.adjustDistEnvWidgetMaximum)
        self.distMenuEdit_WaveshapeParts.valueChanged.connect(partial(self.updateDistParams, choice=None))
        self.distMenuEdit_LofiBits.valueChanged.connect(partial(self.updateDistParams, choice=None))
        self.distMenuEdit_SaturationFactor.valueChanged.connect(partial(self.updateDistParams, choice=None))
        self.distMenuEdit_PhaseModOff.stateChanged.connect(self.layerSetPhaseMod)
        self.distMenuEdit_PhaseModAmt.valueChanged.connect(self.layerSetPhaseModAmt)
        self.distMenuEdit_PhaseModSource.currentIndexChanged.connect(self.layerSetPhaseModSrc)
        self.distMenuType.currentTextChanged.connect(self.updateDistParams)

        self.amplEnvWidget.pointsChanged.connect(self.amplEnvUpdateCurrent)
        self.freqEnvWidget.pointsChanged.connect(self.freqEnvUpdateCurrent)
        self.distEnvWidget.pointsChanged.connect(self.distEnvUpdateCurrent)


    def initModelView(self):
        self.drumModel = DrumModel()
        self.drumList.setModel(self.drumModel)
        self.drumList.currentIndexChanged.connect(self.drumLoad)
        # change should trigger (autosave and) reload

        self.layerModel = LayerModel()
        self.layerList.setModel(self.layerModel)
        self.layerList.selectionModel().currentChanged.connect(self.layerLoad)

        self.amplEnvModel = EnvelopeModel()
        self.amplEnvList.setModel(self.amplEnvModel)
        self.amplEnvList.selectionModel().currentChanged.connect(self.amplEnvLoad)
        self.amplEnvModel.layoutChanged.connect(self.amplEnvUpdateWidget) # TODO: check one day: do we need these?
        self.amplEnvModel.dataChanged.connect(self.updateDrumAmplEnvs)

        self.freqEnvModel = EnvelopeModel()
        self.freqEnvList.setModel(self.freqEnvModel)
        self.freqEnvList.selectionModel().currentChanged.connect(self.freqEnvLoad)
        self.freqEnvModel.layoutChanged.connect(self.freqEnvUpdateWidget)
        self.freqEnvModel.dataChanged.connect(self.updateDrumFreqEnvs)

        self.distEnvModel = EnvelopeModel()
        self.distEnvList.setModel(self.distEnvModel)
        self.distEnvList.selectionModel().currentChanged.connect(self.distEnvLoad)
        self.distEnvModel.layoutChanged.connect(self.distEnvUpdateWidget)
        self.distEnvModel.dataChanged.connect(self.updateDrumDistEnvs)

        self.layerChooseAmplEnvList.setModel(self.amplEnvModel)
        self.layerChooseFreqEnvList.setModel(self.freqEnvModel)
        self.layerChooseDistEnvList.setModel(self.distEnvModel)

        self.distMenuEdit_PhaseModSource.setModel(self.layerModel)


    def initDefaultDrum(self):
        self.defaultDrum = Drum()
        self.defaultDrum.addAmplEnv(defaultAmplEnvelope)
        self.defaultDrum.addFreqEnv(defaultFreqEnvelope)
        self.defaultDrum.addDistEnv(defaultDistEnvelope)
        self.defaultDrum.addLayer(Layer(amplEnv = defaultAmplEnvelope, freqEnv = defaultFreqEnvelope, distEnv = defaultDistEnvelope))

    def initData(self):
        # here one could load'em all!
        self.drumInsertAndSelect(self.defaultDrum)
        self.drumLoad(0)


    def changeWidgetDimensions(self, timeZoom = None, valueZoom = None):
        if timeZoom is None and valueZoom is None:
            inputDialog = DoubleInputDialog(self.parent, replaceTitle = 'Resize Views', replaceTimeLabel = 'Max. Time in sec.: (0 = default)', replaceValueLabel = 'Max. Value: (0 = default)',
                                            time = 0, value = 0, maxValue = 20000)
            if inputDialog.exec_():
                maxTime = round(inputDialog.timeBox.value(), inputDialog.precision)
                if maxTime < 1e-3:
                    maxTime = None
                maxValue = round(inputDialog.valueBox.value(), inputDialog.precision)
                if maxValue < 1e-3:
                    maxValue = None
                self.initWidgetDimensions(maxTime = maxTime, maxValue = maxValue)
        else:
            if timeZoom is not None:
                self.maxTime['amplitude'] *= timeZoom
                self.maxTime['frequency'] *= timeZoom
                self.maxTime['distortion'] *= timeZoom
            if valueZoom is not None:
                self.maxValue['amplitude'] *= valueZoom
                self.maxValue['frequency'] *= valueZoom
                self.maxValue['distortion'] *= valueZoom
            self.amplEnvWidget.setDimensions(maxTime = self.maxTime['amplitude'], minValue = self.minValue['amplitude'], maxValue = self.maxValue['amplitude'])
            self.freqEnvWidget.setDimensions(maxTime = self.maxTime['frequency'], minValue = self.minValue['frequency'], maxValue = self.maxValue['frequency'], logValue = True)
            self.distEnvWidget.setDimensions(maxTime = self.maxTime['distortion'], minValue = self.minValue['distortion'], maxValue = self.maxValue['distortion'])


################################ MODEL FUNCTIONALITY ################################
#####################################################################################

    def loadSourceTemplate(self):
        sourceTemplateFile = QFile(self.renderTemplate)
        if not sourceTemplateFile.open(QFile.ReadOnly | QFile.Text):
            QMessageBox.warning('Could not read template file {}'.format(self.renderTemplate))
            return
        sourceTemplateStream = QTextStream(sourceTemplateFile)
        sourceTemplateStream.setCodec('utf-8')
        return sourceTemplateStream.readAll()

    def hashAllUsedEnvelopes(self):
        hashsInUse = []
        for layer in self.layerModel.layers:
            hashsInUse += [layer.amplEnvHash, layer.freqEnvHash, layer.distEnvHash]
        return set(hashsInUse)

    def purgeUnusedEnvelopes(self):
        print('Purge unused envelopes...')
        hashsInUse = self.hashAllUsedEnvelopes()

        for model in [self.amplEnvModel, self.freqEnvModel, self.distEnvModel]:
            reducedEnvs = [env for env in model.envelopes if env._hash in hashsInUse]
            model.clearAndRefill(reducedEnvs)

    def debugOutput(self):
        print("=== AMPLITUDE ENVELOPES ===")
        for env in self.amplEnvModel.envelopes:
            print('\t', env.name, env._hash)
        print("=== FREQUENCY ENVELOPES ===")
        for env in self.freqEnvModel.envelopes:
            print('\t', env.name, env._hash)
        print("=== DISTORTION ENVELOPES ===")
        for env in self.distEnvModel.envelopes:
            print('\t', env.name, env._hash)
        print("=== AND NOW ALL HASHS OF ENVELOPES CURRENTLY USED IN LAYERS: ===")
        print('\n'.join(self.hashAllUsedEnvelopes()))


    def drumatizeLayers(self, layers, dumpSyn = False):
        drumatizer = Drumatizer(layers, self.amplEnvModel.envelopes, self.freqEnvModel.envelopes, self.distEnvModel.envelopes, self.currentDrum().postprocPrefix, self.currentDrum().postprocSuffix)
        drumatizeL, drumatizeR, envFunc = drumatizer.drumatize()
        sourceShader = self.loadSourceTemplate().replace('AMAYDRUMATIZE_L', drumatizeL).replace('AMAYDRUMATIZE_R', drumatizeR).replace('//ENVFUNCTIONCODE', envFunc)
        self.shaderCreated.emit(sourceShader)
        if dumpSyn:
            self.synDrumCreated.emit(drumatizeL, drumatizeR, envFunc)


#################################### DRUMS ##########################################

    def anyDrums(self, moreThan = 0):
        return self.drumModel.rowCount() > moreThan

    def currentDrum(self):
        try:
            return self.drumModel.drums[self.drumList.currentIndex()]
        except IndexError:
            return None

    def drumLoad(self, index = None):
        self.selectDrum.emit()
        if index is not None:
            self.drumList.setCurrentIndex(index)
            drum = self.drumModel.drums[index]
        else:
            drum = self.currentDrum()
        self.amplEnvModel.clearAndRefill(drum.amplEnvs)
        self.freqEnvModel.clearAndRefill(drum.freqEnvs)
        self.distEnvModel.clearAndRefill(drum.distEnvs)
        self.layerModel.clearAndRefill(drum.layers)
        self.layerSelect(0)
        self.layerLoad()

    def drumInsertAndSelect(self, drum, position = None):
        self.drumModel.insertNew(drum, position)
        self.drumModel.layoutChanged.emit()
        index = self.drumModel.indexOf(drum)
        if index.isValid():
            self.drumList.setCurrentIndex(index.row())

    def drumAdd(self, clone = False):
        title = 'New Drum' if not clone else 'Clone Drum'
        name, ok = QInputDialog.getText(self, title, 'Enter {} Name:'.format(title), QLineEdit.Normal, '')
        if ok and name != '':
            oldDrum = self.defaultDrum if not clone else self.currentDrum()
            newDrum = deepcopy(oldDrum)
            newDrum.adjust(name = name, layers = deepcopy(oldDrum.layers))
            self.drumInsertAndSelect(newDrum, self.drumList.currentIndex() + 1)

    def drumClone(self):
        self.drumAdd(clone = True)

    def drumDelete(self):
        if self.anyDrums(moreThan = 1):
            self.drumModel.drums.remove(self.currentDrum())
            self.drumModel.layoutChanged.emit()

    def drumEdit(self):
        currentParameters = f'{self.currentDrum().name}; {self.currentDrum().type}; {self.currentDrum().iLike}'
        dialog = QInputDialog(self.parent)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setWindowTitle('Edit Drum')
        dialog.setLabelText('Enter [name; type; awesomeness]')
        dialog.setTextValue(currentParameters)
        dialog.resize(400,200)
        ok = dialog.exec_()
        if not ok:
            return
        pars = dialog.textValue().split(';')
        if len(pars) > 0:
            self.currentDrum().adjust(name = pars[0].strip())
        if len(pars) > 1:
            self.currentDrum().adjust(type = pars[1].strip())
        if len(pars) > 2:
            self.currentDrum().adjust(iLike = int(pars[2].strip()))

        currentPostProc = f'{self.currentDrum().postprocPrefix}...{self.currentDrum().postprocSuffix}'
        dialog = QInputDialog(self.parent)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setWindowTitle('Post Processing')
        dialog.setLabelText('Enter [Prefix...Suffix] (with these ...!)')
        dialog.setTextValue(currentPostProc)
        dialog.resize(400,200)
        ok = dialog.exec_()
        if not ok:
            return
        pars = dialog.textValue().split('...')
        if len(pars) != 2:
            print(dialog.textValue(), 'is not a valid post processing Prefix...Suffix form.')
            return
        self.currentDrum().adjust(postprocPrefix = pars[0].strip())
        self.currentDrum().adjust(postprocSuffix = pars[1].strip())

    def drumExport(self, name = None, useCurrentDrumName = False):
        if name is None:
            if useCurrentDrumName:
                name = self.currentDrum().name + '.drum'
                print(f'Export to {name}')
            else:
                nameSuggestion = self.currentDrum().name.replace(' ', '_').replace('?', '')
                name, _ = QFileDialog.getSaveFileName(self.parent, 'Export', nameSuggestion, 'Single *.drum or whole *.drumset files(*.drum *.drumset)')
                if name == '':
                    return
        name = path.basename(name)
        extension = name.split('.')[-1]
        actualName = '.'.join(name.split('.')[0:-1])
        fn = open(name, 'w')
        if extension == 'drum':
            json.dump(self.currentDrum(), fn, cls = DrumEncoder)
            if actualName != self.currentDrum().name:
                print("Renaming drum to", actualName)
                self.currentDrum().adjust(name = actualName) # TODO: think about whether we want this
        elif extension == 'drumset':
            json.dump(self.drumModel.drums, fn, cls = DrumEncoder)
        else:
            print('File extension is neither .drum nor .drumset, I do not quit but refuse to do shit!')
        fn.close()

    def drumImport(self, name = None):
        if name is None:
            name, _  = QFileDialog.getOpenFileName(self.parent, 'Import', '', 'Single *.drum or whole *.drumset files(*.drum *.drumset)')
            if name == '':
                return
        name = path.basename(name)
        extension = name.split('.')[-1]
        actualName = '.'.join(name.split('.')[0:-1])
        fn = open(name, 'r')
        # TOOD: check whether names exist --> opt to rename or overwrite
        if extension == 'drum':
            newDrum = json.load(fn, object_hook = DrumEncoder.decode)
            newDrum.adjust(name = actualName)
            while newDrum.name in self.drumModel.nameList():
                dialog = RenameReplaceDialog(self, name = newDrum.name)
                if dialog.exec_():
                    if dialog.mode == RenameReplaceDialog.RENAME:
                        newDrum.adjust(name = dialog.getName())
                    elif dialog.mode == RenameReplaceDialog.REPLACE:
                        self.drumModel.removeFirstDrumOfName(newDrum.name)
                    else:
                        print("RenameReplaceDialog returned unknown value for mode")
                        raise ValueError
                else:
                    break
            self.drumInsertAndSelect(newDrum)
        elif extension == 'drumset':
            self.drumModel.clearAndRefill(json.load(fn, object_hook = DrumEncoder.decode))
            self.drumLoad(0)
        else:
            print('File extension is neither .drum nor .drumset, I do not quit but refuse to do shit!')
        fn.close()


    def drumRender(self):
        self.drumatizeLayers(self.currentDrum().layers, dumpSyn = True)


    def updateDrumAmplEnvs(self):
        self.currentDrum().adjust(amplEnvs = self.amplEnvModel.envelopes)

    def updateDrumFreqEnvs(self):
        self.currentDrum().adjust(freqEnvs = self.freqEnvModel.envelopes)

    def updateDrumDistEnvs(self):
        self.currentDrum().adjust(distEnvs = self.distEnvModel.envelopes)

    def setSynDumpParameters(self, useSynDump, synFileName, synDrumName):
        self.currentDrum().adjust(useSynDump = useSynDump, synFileName = synFileName, synDrumName = synDrumName)

    def getSynDumpParameters(self):
        return self.currentDrum().useSynDump, self.currentDrum().synFileName, self.currentDrum().synDrumName

##################################### LAYERS ########################################

    def anyLayers(self, moreThan = 0):
        return self.layerModel.rowCount() > moreThan

    def currentLayer(self):
        try:
            return self.layerModel.layers[self.layerList.currentIndex().row()]
        except IndexError:
            return None

    def layerAmplEnv(self, layer):
        if layer is None:
            return None
        else:
            return self.amplEnvModel.envOfHash(layer.amplEnvHash)

    def currentLayerAmplEnv(self):
        return self.layerAmplEnv(self.currentLayer())

    def layerFreqEnv(self, layer):
        if layer is None:
            return None
        else:
            return self.freqEnvModel.envOfHash(layer.freqEnvHash)

    def currentLayerFreqEnv(self):
        return self.layerFreqEnv(self.currentLayer())

    def layerDistEnv(self, layer):
        if layer is None:
            return None
        else:
            return self.distEnvModel.envOfHash(layer.distEnvHash)

    def currentLayerDistEnv(self):
        return self.layerDistEnv(self.currentLayer())

    def layerLoad(self, current = None, previous = None):
        if current is None:
            current = self.layerList.currentIndex()
        layer = self.layerModel.layers[current.row()]
        self.layerEditorName.setText(layer.name)
        self.layerEditorType.setCurrentText(layer.type)

        if self.layerAmplEnv(layer) is not None:
            self.layerChooseAmplEnvList.setCurrentText(self.layerAmplEnv(layer).name)
            self.amplEnvMenu_TryExpFitChkBox.setChecked(self.layerAmplEnv(layer).parameters['tryExpFit'])
        if self.layerFreqEnv(layer) is not None:
            self.freqEnvMenu_UsePolynomialChkBox.setChecked(self.layerFreqEnv(layer).parameters['usePolynomial'])
            self.layerChooseFreqEnvList.setCurrentText(self.layerFreqEnv(layer).name)
        if self.layerDistEnv(layer) is not None:
            self.layerChooseDistEnvList.setCurrentText(self.layerDistEnv(layer).name)

        self.layerChooseDistOff.setChecked(layer.distOff)
        self.layerEditorVolumeSlider.setValue(layer.volume)
        self.layerMenuMuteBox.setChecked(layer.mute)
        self.layerEditorDetuneSlider.setValue(layer.detune)
        self.layerEditorStereoDelaySlider.setValue(layer.stereodelay)

        self.distMenuType.setCurrentText(layer.distType)
        self.distMenuEdit_PhaseModOff.setChecked(not layer.phasemodOff)
        self.distMenuEdit_PhaseModAmt.setValue(layer.phasemodAmt)
        self.distMenuEdit_PhaseModSource.setCurrentIndex(self.layerModel.indexOfHash(layer.phasemodSrcHash) or 0)

    def layerUpdate(self):
        self.layerList.dataChanged(self.layerList.currentIndex(), self.layerList.currentIndex())

    def layerSelect(self, numericalIndex):
        if self.layerModel.rowCount() > 0:
            index = self.layerModel.createIndex(numericalIndex,0)
            self.layerList.selectionModel().setCurrentIndex(index, QItemSelectionModel.SelectCurrent)

    def layerInsertAndSelect(self, layer, position = None):
        self.layerModel.insertNew(layer, position)
        index = self.layerModel.indexOf(layer)
        if index.isValid():
            self.layerList.clearSelection()
            print(self.currentAmplEnv()._hash, layer.amplEnvHash)
            self.layerList.selectionModel().setCurrentIndex(index, QItemSelectionModel.SelectCurrent)
            print(self.currentAmplEnv()._hash, layer.amplEnvHash)
            self.layerModel.emitAllChanged()
            self.layerList.scrollTo(index)

    def layerAdd(self):
        # TODO: add some 'Clone' function, but not now
        self.amplEnvInsertAndSelect(defaultAmplEnvelope)
        self.freqEnvInsertAndSelect(defaultFreqEnvelope)
        self.distEnvInsertAndSelect(defaultDistEnvelope)
        newLayer = Layer(amplEnv = self.currentAmplEnv(), freqEnv = self.currentFreqEnv(), distEnv = self.currentDistEnv())
        newLayer.adjust(name = newLayer.talkSomeTeam210Shit(skip = self.layerModel.nameList()), volume = 100, detune = 0, stereodelay = 0, distOff = True)
        self.layerInsertAndSelect(newLayer, self.layerList.currentIndex().row() + 1)
        self.layerLoad()
        self.layerModel.layoutChanged.emit()
        self.layerEditorName.selectAll()
        self.layerEditorName.setFocus()

    def layerDelete(self):
        if self.anyLayers(moreThan = 1):
            index = self.layerModel.indexOf(self.currentLayer()).row()
            self.layerModel.layers.remove(self.currentLayer())
            self.layerModel.layoutChanged.emit()
            if index == self.layerModel.rowCount():
                self.layerList.setCurrentIndex(self.layerModel.indexOf(self.layerModel.lastLayer()))

    def layerSwap(self):
        index = self.layerModel.indexOf(self.currentLayer()).row()
        nextIndex = (index + 1) % self.layerModel.rowCount()
        self.layerModel.swapLayers(index, nextIndex)
        self.layerSelect(nextIndex)

    def layerRandomize(self):
        print("HAVE YET TO IMPLEMENT LAYER RANDOMIZE..! (sry)")

    def layerRenderSolo(self):
        soloLayer = [self.currentLayer()]
        keepMute = soloLayer[0].mute
        soloLayer[0].mute = False

        # we might also need the phaseMod layer, if given - but make sure it's muted
        needPhasemodLayer = (not self.currentLayer().phasemodOff and self.currentLayer().phasemodSrcHash != self.currentLayer()._hash)
        if needPhasemodLayer:
            soloLayer.append(self.layerModel.layerOfHash(self.currentLayer().phasemodSrcHash))
            keepPhaseModSrcMute = soloLayer[-1].mute
            soloLayer[-1].mute = True

        self.drumatizeLayers(soloLayer)

        # restore mute settings
        soloLayer[0].mute = keepMute
        if needPhasemodLayer:
            soloLayer[-1].mute = keepPhaseModSrcMute

    def layerSetName(self, name):
        self.currentLayer().adjust(name = name)
        self.layerUpdate()

    def layerRenameFresh(self):
        name = self.layerEditorName.text()
        if self.layerModel.justAddedNew and name != '':
            self.currentLayerAmplEnv().adjust(name = name)
            self.currentLayerFreqEnv().adjust(name = name)
            self.currentLayerDistEnv().adjust(name = name)
        self.layerModel.justAddedNew = False

    def layerSetType(self, type):
        self.currentLayer().adjust(type = type)
        self.layerUpdate()

    def layerSetDistOff(self, state):
        self.currentLayer().adjust(distOff = state)
        self.layerChooseDistEnvList.setEnabled(not state)
        self.layerUpdate()

    def layerSetMute(self, state):
        self.currentLayer().adjust(mute = (state == Qt.Checked))
        self.layerUpdate()

    def layerSetVolume(self, value):
        self.currentLayer().adjust(volume = value)
        self.layerEditorVolumeLabel.setText(f'{value}%')
        self.layerUpdate()

    def layerSetDetune(self, value):
        self.currentLayer().adjust(detune = value)
        self.layerEditorDetuneLabel.setText(f'{value}‰')
        self.layerUpdate()

    def layerSetStereoDelay(self, value):
        self.currentLayer().adjust(stereodelay = value)
        self.layerEditorStereoDelayLabel.setText(f'{value}0 ppm' if value != 0 else '0 ppm')
        self.layerUpdate()

    def layerSetPhaseMod(self, state):
        self.currentLayer().adjust(phasemodOff = (state != Qt.Checked))
        self.layerUpdate()

    def layerSetPhaseModAmt(self, value):
        self.currentLayer().adjust(phasemodAmt = value)
        self.layerUpdate()

    def layerSetPhaseModSrc(self, index):
        self.currentLayer().adjust(phasemodSrcHash = self.layerModel.hashList()[index])
        self.layerUpdate()


    def loadDistParams(self):
        choice = self.currentLayer().distType
        self.distMenuType.setCurrentText(choice)
        distParam = self.currentLayer().distParam
        if choice == 'Overdrive':
            self.distMenuEdit_OverdriveMaximum.setValue(distParam)
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_OverdriveMaximum)
            self.adjustDistEnvWidgetMaximum(distParam)
        elif choice == 'Waveshape':
            self.distMenuEdit_WaveshapeParts(distParam)
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_WaveshapeParts)
            self.adjustDistEnvWidgetMaximum(2)
        elif choice == 'Lo-Fi':
            self.distMenuEdit_LofiBits.setValue(distParam)
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_LofiBits)
            self.adjustDistEnvWidgetMaximum(2)
        elif choice == 'Saturation':
            self.distMenuEdit_SaturationFactor.setValue(distParam)
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_SaturationFactor)
            self.adjustDistEnvWidgetMaximum(10)
        else:
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_NA)

    def updateDistParams(self, choice = None):
        if choice is None:
            choice = self.currentLayer().distType

        if choice == 'Overdrive':
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_OverdriveMaximum)
            self.adjustDistEnvWidgetMaximum(self.distMenuEdit_OverdriveMaximum.value())
            distParam = None
        elif choice == 'Waveshape':
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_WaveshapeParts)
            self.adjustDistEnvWidgetMaximum(2)
            distParam = self.distMenuEdit_WaveshapeParts.value()
        elif choice == 'Lo-Fi':
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_LofiBits)
            self.adjustDistEnvWidgetMaximum(2)
            distParam = self.distMenuEdit_LofiBits.value()
        elif choice == 'Saturation':
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_SaturationFactor)
            self.adjustDistEnvWidgetMaximum(10)
            distParam = self.distMenuEdit_SaturationFactor.value()
        else:
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_NA)
            distParam = None

        self.currentLayer().adjust(distType = choice, distParam = distParam)

    def adjustDistEnvWidgetMaximum(self, value):
        self.maxValue['distortion'] = value
        self.distEnvWidget.setDimensions(maxValue = value)

############################ AMPLITUDE ENVELOPES ####################################

    def anyAmplEnv(self, moreThan = 0):
        return self.amplEnvModel.rowCount() > moreThan

    def currentAmplEnv(self):
        try:
            return self.amplEnvModel.envelopes[self.amplEnvList.currentIndex().row()]
        except IndexError:
            return None

    def amplEnvUpdateCurrent(self):
        self.currentAmplEnv().adjust(points = self.amplEnvWidget.points)

    def amplEnvUpdateWidget(self):
        self.amplEnvWidget.loadEnvelope(self.currentAmplEnv())

    def amplEnvLoad(self, current, previous = None):
        self.amplEnvWidget.loadEnvelope(self.amplEnvModel.envelopes[current.row()])
        self.amplEnvMenu_TryExpFitChkBox.setChecked(self.amplEnvModel.envelopes[current.row()].parameters['tryExpFit'])

    def amplEnvSelect(self, envelope):
        index = self.amplEnvModel.indexOf(envelope)
        print(envelope.name, index)
        if index.isValid():
            self.amplEnvList.clearSelection()
            self.amplEnvList.selectionModel().setCurrentIndex(index, QItemSelectionModel.SelectCurrent)
            self.amplEnvModel.emitAllChanged()
            self.amplEnvList.scrollTo(index)

    def amplEnvSelectIndex(self, index):
        self.amplEnvList.selectionModel().setCurrentIndex(self.amplEnvModel.createIndex(index, 0), QItemSelectionModel.SelectCurrent)
        self.currentLayer().amplEnvHash = self.currentAmplEnv()._hash

    def amplEnvInsertAndSelect(self, envelope, position = None):
        self.amplEnvModel.insertNew(envelope, position)
        self.amplEnvSelect(self.amplEnvModel.newestEnvelope())

    def amplEnvAdd(self):
        self.handleAmplEnvSettingsDialog(SettingsDialog(self, defaultAmplEnvelope, mode = SettingsDialog.NEW))

    def amplEnvEditSettings(self):
        if self.anyAmplEnv():
            self.handleAmplEnvSettingsDialog(SettingsDialog(self, self.currentAmplEnv()))

    def handleAmplEnvSettingsDialog(self, dialog):
        if dialog.exec_():
            name = dialog.getName()
            pointNumber = dialog.getPointNumber()
            value = dialog.getSinglePointValue()
            assign = dialog.getWhetherToAssign()
            if dialog.mode == SettingsDialog.NEW:
                self.amplEnvInsertAndSelect(defaultAmplEnvelope, self.amplEnvList.currentIndex().row() + 1)
            elif dialog.mode == SettingsDialog.CLONE:
                self.amplEnvInsertAndSelect(self.currentAmplEnv(), self.amplEnvList.currentIndex().row() + 1)
            if not name:
                name = '({} env {})'.format(self.currentAmplEnv().type, self.amplEnvList.currentIndex().row() + 1)
            if self.amplEnvModel.nameExists(name) and dialog.mode != SettingsDialog.EDIT:
                name += '++'
            self.currentAmplEnv().adjust(name = name, pointNumber = pointNumber, singlePointValue = value)

            if assign:
                self.layerChooseAmplEnvList.setCurrentIndex(self.amplEnvList.currentIndex().row())

            self.amplEnvUpdateWidget()
            self.amplEnvModel.dataChanged.emit(self.amplEnvList.currentIndex(), self.amplEnvList.currentIndex())


    def amplEnvDelete(self):
        if self.currentAmplEnv()._hash in self.hashAllUsedEnvelopes():
            print("This Envelope is assigned somewhere; thus can not be deleted.")
            return
        confirm = QMessageBox.question(self, "Delete?", "Delete? Sure?")
        if confirm == QMessageBox.No:
            return
        if self.anyAmplEnv(moreThan = 1):
            index = self.amplEnvModel.indexOf(self.currentAmplEnv()).row()
            self.amplEnvModel.envelopes.remove(self.currentAmplEnv())
            self.amplEnvModel.layoutChanged.emit()
            if index == self.amplEnvModel.rowCount():
                self.amplEnvList.setCurrentIndex(self.amplEnvModel.indexOf(self.amplEnvModel.lastEnvelope()))

    def amplEnvRandomize(self):
        if self.anyAmplEnv():
            env = self.currentAmplEnv()
            env.randomize(self.maxTime[env.type], self.minValue[env.type], self.maxValue[env.type])
            self.amplEnvWidget.update()

    def amplEnvSetTryExpFit(self, state):
        self.currentAmplEnv().adjustParameter('tryExpFit', state == Qt.Checked)


############################ FREQUENCY ENVELOPES ####################################

    def anyFreqEnv(self, moreThan = 0):
        return self.freqEnvModel.rowCount() > moreThan

    def currentFreqEnv(self):
        try:
            return self.freqEnvModel.envelopes[self.freqEnvList.currentIndex().row()]
        except IndexError:
            return None

    def freqEnvUpdateCurrent(self):
        self.currentFreqEnv().adjust(points = self.freqEnvWidget.points)

    def freqEnvUpdateWidget(self):
        self.freqEnvWidget.loadEnvelope(self.currentFreqEnv())

    def freqEnvLoad(self, current, previous = None):
        self.freqEnvWidget.loadEnvelope(self.freqEnvModel.envelopes[current.row()])
        self.freqEnvMenu_UsePolynomialChkBox.setChecked(self.freqEnvModel.envelopes[current.row()].parameters['usePolynomial'])

    def freqEnvSelect(self, envelope):
        index = self.freqEnvModel.indexOf(envelope)
        if index.isValid():
            self.freqEnvList.clearSelection()
            self.freqEnvList.selectionModel().setCurrentIndex(index, QItemSelectionModel.SelectCurrent)
            self.freqEnvModel.emitAllChanged()
            self.freqEnvList.scrollTo(index)

    def freqEnvSelectIndex(self, index):
        self.freqEnvList.selectionModel().setCurrentIndex(self.freqEnvModel.createIndex(index, 0), QItemSelectionModel.SelectCurrent)
        self.currentLayer().freqEnvHash = self.currentFreqEnv()._hash

    def freqEnvInsertAndSelect(self, envelope, position = None):
        self.freqEnvModel.insertNew(envelope, position)
        self.freqEnvSelect(self.freqEnvModel.newestEnvelope())

    def freqEnvAdd(self):
        self.handleFreqEnvSettingsDialog(SettingsDialog(self, defaultFreqEnvelope, mode = SettingsDialog.NEW))

    def freqEnvEditSettings(self):
        if self.anyFreqEnv():
            self.handleFreqEnvSettingsDialog(SettingsDialog(self, self.currentFreqEnv()))

    def handleFreqEnvSettingsDialog(self, dialog):
        if dialog.exec_():
            name = dialog.getName()
            pointNumber = dialog.getPointNumber()
            value = dialog.getSinglePointValue()
            assign = dialog.getWhetherToAssign()
            if dialog.mode == SettingsDialog.NEW:
                self.freqEnvInsertAndSelect(defaultFreqEnvelope, self.freqEnvList.currentIndex().row() + 1)
            elif dialog.mode == SettingsDialog.CLONE:
                self.freqEnvInsertAndSelect(self.currentFreqEnv(), self.freqEnvList.currentIndex().row() + 1)
            if not name:
                name = '({} env {})'.format(self.currentFreqEnv().type, self.freqEnvList.currentIndex().row() + 1)
            if self.freqEnvModel.nameExists(name) and dialog.mode != SettingsDialog.EDIT:
                name += '++'
            self.currentFreqEnv().adjust(name = name, pointNumber = pointNumber, singlePointValue = value)

            if assign:
                self.layerChooseFreqEnvList.setCurrentIndex(self.freqEnvList.currentIndex().row())

            self.freqEnvUpdateWidget()
            self.freqEnvModel.dataChanged.emit(self.freqEnvList.currentIndex(), self.freqEnvList.currentIndex())


    def freqEnvDelete(self):
        if self.currentFreqEnv()._hash in self.hashAllUsedEnvelopes():
            print("This Envelope is assigned somewhere; thus can not be deleted.")
            return
        confirm = QMessageBox.question(self, "Delete?", "Delete? Sure?")
        if confirm == QMessageBox.No:
            return
        if self.anyFreqEnv(moreThan = 1):
            index = self.freqEnvModel.indexOf(self.currentFreqEnv()).row()
            self.freqEnvModel.envelopes.remove(self.currentFreqEnv())
            self.freqEnvModel.layoutChanged.emit()
            if index == self.freqEnvModel.rowCount():
                self.freqEnvList.setCurrentIndex(self.freqEnvModel.indexOf(self.freqEnvModel.lastEnvelope()))

    def freqEnvRandomize(self):
        if self.anyFreqEnv():
            env = self.currentFreqEnv()
            env.randomize(self.maxTime[env.type], self.minValue[env.type], self.maxValue[env.type])
            self.freqEnvWidget.update()

    def freqEnvSetUsePolynomial(self, state):
        self.currentFreqEnv().adjustParameter('usePolynomial', state == Qt.Checked)


############################ DISTORTION ENVELOPES ####################################

    def anyDistEnv(self, moreThan = 0):
        return self.distEnvModel.rowCount() > moreThan

    def currentDistEnv(self):
        try:
            return self.distEnvModel.envelopes[self.distEnvList.currentIndex().row()]
        except IndexError:
            return None

    def distEnvUpdateCurrent(self):
        self.currentDistEnv().adjust(points = self.distEnvWidget.points)

    def distEnvUpdateWidget(self):
        self.distEnvWidget.loadEnvelope(self.currentDistEnv())

    def distEnvLoad(self, current, previous = None):
        self.distEnvWidget.loadEnvelope(self.distEnvModel.envelopes[current.row()])

    def distEnvSelect(self, envelope):
        index = self.distEnvModel.indexOf(envelope)
        if index.isValid():
            self.distEnvList.clearSelection()
            self.distEnvList.selectionModel().setCurrentIndex(index, QItemSelectionModel.SelectCurrent)
            self.distEnvModel.emitAllChanged()
            self.distEnvList.scrollTo(index)

    def distEnvSelectIndex(self, index):
        self.distEnvList.selectionModel().setCurrentIndex(self.distEnvModel.createIndex(index, 0), QItemSelectionModel.SelectCurrent)
        self.currentLayer().distEnvHash = self.currentDistEnv()._hash

    def distEnvInsertAndSelect(self, envelope, position = None):
        self.distEnvModel.insertNew(envelope, position)
        self.distEnvSelect(self.distEnvModel.newestEnvelope())

    def distEnvAdd(self):
        self.handleDistEnvSettingsDialog(SettingsDialog(self, defaultDistEnvelope, mode = SettingsDialog.NEW))

    def distEnvEditSettings(self):
        if self.anyDistEnv():
            self.handleDistEnvSettingsDialog(SettingsDialog(self, self.currentDistEnv()))

    def handleDistEnvSettingsDialog(self, dialog):
        if dialog.exec_():
            name = dialog.getName()
            pointNumber = dialog.getPointNumber()
            value = dialog.getSinglePointValue()
            assign = dialog.getWhetherToAssign()
            if dialog.mode == SettingsDialog.NEW:
                self.distEnvInsertAndSelect(defaultDistEnvelope, self.distEnvList.currentIndex().row() + 1)
            elif dialog.mode == SettingsDialog.CLONE:
                self.distEnvInsertAndSelect(self.currentDistEnv(), self.distEnvList.currentIndex().row() + 1)
            if not name:
                name = '({} env {})'.format(self.currentDistEnv().type, self.distEnvList.currentIndex().row() + 1)
            if self.distEnvModel.nameExists(name) and dialog.mode != SettingsDialog.EDIT:
                name += '++'
            self.currentDistEnv().adjust(name = name, pointNumber = pointNumber, singlePointValue = value)

            if assign:
                self.layerChooseDistEnvList.setCurrentIndex(self.distEnvList.currentIndex().row())

            self.distEnvUpdateWidget()
            self.distEnvModel.dataChanged.emit(self.distEnvList.currentIndex(), self.distEnvList.currentIndex())


    def distEnvDelete(self):
        if self.currentDistEnv()._hash in self.hashAllUsedEnvelopes():
            print("This Envelope is assigned somewhere; thus can not be deleted.")
            return
        confirm = QMessageBox.question(self, "Delete?", "Delete? Sure?")
        if confirm == QMessageBox.No:
            return
        if self.anyDistEnv(moreThan = 1):
            index = self.distEnvModel.indexOf(self.currentDistEnv()).row()
            self.distEnvModel.envelopes.remove(self.currentDistEnv())
            self.distEnvModel.layoutChanged.emit()
            if index == self.distEnvModel.rowCount():
                self.distEnvList.setCurrentIndex(self.distEnvModel.indexOf(self.distEnvModel.lastEnvelope()))

    def distEnvRandomize(self):
        if self.anyDistEnv():
            env = self.currentDistEnv()
            env.randomize(self.maxTime, self.minValue[env.type], self.maxValue[env.type])
            self.distEnvWidget.update()


# TODO: idea for layer effects: chorus / more precise stereo delay / .. ??


# deadline: hard cyber

# vortex: nordic horror industrial (BLACKHNO)

# UNC: die grüne demo

# revision: tunguska / tschernobyl
# game: johann lafers helilandeplatz