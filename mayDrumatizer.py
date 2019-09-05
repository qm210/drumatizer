from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QItemSelectionModel

from DrumModel import *
from LayerModel import *
from EnvelopeModel import *
from EnvelopeWidget import *
from SettingsDialog import *

class MayDrumatizer(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.initLayouts()

        self.initModelView()

        self.initData()


    def initLayouts(self):
        # preset widget
        self.presetList = QComboBox()
        self.presetList.addItem('<no preset stored>')
        self.preset_BtnAdd = QPushButton('+')
        self.preset_BtnClone = QPushButton('C')
        self.preset_BtnDel = QPushButton('–')
        self.preset_BtnEdit = QPushButton('...')
        self.preset_BtnExport = QPushButton('↗')
        self.preset_BtnImport = QPushButton('↘')
        self.preset_BtnRender = QPushButton('Render >>')

        self.presetLayout = QHBoxLayout()
        self.presetLayout.addWidget(QLabel('Preset:'))
        self.presetLayout.addWidget(self.presetList, 4)
        self.presetLayout.addWidget(self.preset_BtnAdd)
        self.presetLayout.addWidget(self.preset_BtnClone)
        self.presetLayout.addWidget(self.preset_BtnDel)
        self.presetLayout.addWidget(self.preset_BtnEdit)
        self.presetLayout.addWidget(self.preset_BtnExport)
        self.presetLayout.addWidget(self.preset_BtnImport)
        self.presetLayout.addWidget(self.preset_BtnRender)

        self.presetGroup = QGroupBox()
        self.presetGroup.setLayout(self.presetLayout)

        # layer widget
        self.layerMainLayout = QHBoxLayout()
        self.layerListLayout = QVBoxLayout()
        self.layerList = QListView()
        self.layerListLayout.addWidget(QLabel('Drum Layers'))
        self.layerListLayout.addWidget(self.layerList)

        self.layerEditor = QGroupBox()
        self.layerEditorLayout = QFormLayout()
        self.layerEditor.setLayout(self.layerEditorLayout)

        self.layerEditorName = QLineEdit()
        self.layerEditorType = QComboBox()
        self.layerEditorType.addItems(layerTypes)

        self.layerChooseAmpEnvList = QComboBox()
        self.layerChooseFreqEnvList = QComboBox()
        self.layerChooseDistEnvList = QComboBox()

        self.layerEditorLayout.addRow('Layer Name:', self.layerEditorName)
        self.layerEditorLayout.addRow('Layer Type:', self.layerEditorType)
        self.layerEditorLayout.addRow('Amplitude Env.:', self.layerChooseAmpEnvList)
        self.layerEditorLayout.addRow('Frequency Env.:', self.layerChooseFreqEnvList)
        self.layerEditorLayout.addRow('Distortion Env.:', self.layerChooseDistEnvList)
        self.layerEditorLayout.addRow('Volume:', QSlider(Qt.Horizontal))
        self.layerEditorLayout.setVerticalSpacing(10)

        self.layerMenu = QVBoxLayout()
        self.layerMenu.addStretch()
        self.layerMenu_BtnAdd = QPushButton('+')
        self.layerMenu_BtnClone = QPushButton('C')
        self.layerMenu_BtnEdit = QPushButton('...')
        self.layerMenu_ChkBoxMute = QCheckBox('Mute')
        self.layerMenu_BtnRenderSolo = QPushButton('Solo >>')
        self.layerMenu_BtnRnd = QPushButton('???')
        self.layerMenu.addWidget(self.layerMenu_BtnAdd)
        self.layerMenu.addWidget(self.layerMenu_BtnClone)
        self.layerMenu.addWidget(self.layerMenu_BtnEdit)
        self.layerMenu.addWidget(self.layerMenu_BtnRnd)
        self.layerMenu.addWidget(self.layerMenu_ChkBoxMute)
        self.layerMenu.addWidget(self.layerMenu_BtnRenderSolo)

        self.layerMainLayout.addLayout(self.layerListLayout, 50)
        self.layerMainLayout.addLayout(self.layerMenu, 1)
        self.layerMainLayout.addWidget(self.layerEditor, 50)

        self.layerGroup = QGroupBox()
        self.layerGroup.setLayout(self.layerMainLayout)

        # amp envelope widget - todo: do something smart to combine layers
        self.ampEnvList = QListView()

        self.ampEnvMenu = QVBoxLayout()
        self.ampEnvWidget = EnvelopeWidget(self)
        self.ampEnvWidget.setDimensions(2, 1)

        self.ampEnvMenu_BtnAdd = QPushButton('+')
        self.ampEnvMenu_BtnAdd.pressed.connect(self.ampEnvAdd)
        self.ampEnvMenu_BtnDel = QPushButton('–')
        self.ampEnvMenu_BtnDel.pressed.connect(self.ampEnvDelete)
        self.ampEnvMenu_BtnRnd = QPushButton('???')
        self.ampEnvMenu_BtnRnd.pressed.connect(self.ampEnvRandomize)
        self.ampEnvMenu_BtnEdit = QPushButton('...')
        self.ampEnvMenu_BtnEdit.pressed.connect(self.ampEnvOpenSettings)

        self.ampEnvMenu.addStretch()
        self.ampEnvMenu.addWidget(self.ampEnvMenu_BtnAdd)
        self.ampEnvMenu.addWidget(self.ampEnvMenu_BtnDel)
        self.ampEnvMenu.addWidget(self.ampEnvMenu_BtnEdit)
        self.ampEnvMenu.addWidget(self.ampEnvMenu_BtnRnd)

        self.ampEnvLayout = QHBoxLayout()
        self.ampEnvLayout.addWidget(self.ampEnvList, 20)
        self.ampEnvLayout.addLayout(self.ampEnvMenu, 1)
        self.ampEnvLayout.addWidget(self.ampEnvWidget, 80)

        self.ampEnvMainLayout = QVBoxLayout()
        self.ampMenuLayout = QHBoxLayout()
        self.ampMenuLayout.addWidget(QLabel('Amplitude Envelopes'))
        self.ampMenuLayout.addStretch()
        self.ampEnvMenu_TryExpFitChkBox = QCheckBox('Try ExpDecay Fit')
        self.ampMenuLayout.addWidget(self.ampEnvMenu_TryExpFitChkBox)

        self.ampEnvMainLayout.addLayout(self.ampMenuLayout, 10)
        self.ampEnvMainLayout.addLayout(self.ampEnvLayout, 90)

        self.ampEnvGroup = QGroupBox()
        self.ampEnvGroup.setLayout(self.ampEnvMainLayout)

        # freq envelope widget
        self.freqEnvList = QListView()
        self.freqEnvMenu = QVBoxLayout()
        self.freqEnvWidget = EnvelopeWidget(self)
        self.freqEnvWidget.setDimensions(maxTime = 2, minValue = 20, maxValue = 12000, logValue = True)

        self.freqEnvMenu_BtnAdd = QPushButton('+')
        self.freqEnvMenu_BtnDel = QPushButton('–')
        self.freqEnvMenu_BtnRnd = QPushButton('???')
        self.freqEnvMenu_BtnEdit = QPushButton('...')
        self.freqEnvMenu.addStretch()
        self.freqEnvMenu.addWidget(self.freqEnvMenu_BtnAdd)
        self.freqEnvMenu.addWidget(self.freqEnvMenu_BtnDel)
        self.freqEnvMenu.addWidget(self.freqEnvMenu_BtnEdit)
        self.freqEnvMenu.addWidget(self.freqEnvMenu_BtnRnd)

        self.freqEnvLayout = QHBoxLayout()
        self.freqEnvLayout.addWidget(self.freqEnvList, 20)
        self.freqEnvLayout.addLayout(self.freqEnvMenu, 1)
        self.freqEnvLayout.addWidget(self.freqEnvWidget, 80)

        self.freqEnvMainLayout = QVBoxLayout()
        self.freqEnvMainLayout.addWidget(QLabel('Frequency Envelopes'), 10)
        self.freqEnvMainLayout.addLayout(self.freqEnvLayout, 90)

        self.freqEnvGroup = QGroupBox()
        self.freqEnvGroup.setLayout(self.freqEnvMainLayout)

        # dist (fx) envelope widget
        self.distEnvList = QListView()
        self.distEnvMenu = QVBoxLayout()
        self.distEnvWidget = EnvelopeWidget(self)
        self.distEnvWidget.setDimensions(maxTime = 2, maxValue = 2)
        # todo: at '...', choose how many points there should be (for dist and amp arbitrarily, for freq: 2 at most!)

        self.distEnvMenu_BtnAdd = QPushButton('+')
        self.distEnvMenu_BtnDel = QPushButton('–')
        self.distEnvMenu_BtnRnd = QPushButton('???')
        self.distEnvMenu_BtnEdit = QPushButton('...')
        self.distEnvMenu.addStretch()
        self.distEnvMenu.addWidget(self.distEnvMenu_BtnAdd)
        self.distEnvMenu.addWidget(self.distEnvMenu_BtnDel)
        self.distEnvMenu.addWidget(self.distEnvMenu_BtnEdit)
        self.distEnvMenu.addWidget(self.distEnvMenu_BtnRnd)

        self.distLayout = QHBoxLayout()
        self.distLayout.addWidget(self.distEnvList, 20)
        self.distLayout.addLayout(self.distEnvMenu, 1)
        self.distLayout.addWidget(self.distEnvWidget, 80)

        self.distMenuType = QComboBox()
        self.distMenuEdit_OverdriveMaximum = QDoubleSpinBox()
        self.distMenuEdit_OverdriveMaximum.setRange(0.1, 99.9)
        self.distMenuEdit_OverdriveMaximum.setValue(self.distEnvWidget.maxValue)
        self.distMenuEdit_OverdriveMaximum.setSingleStep(0.1)
        self.distMenuEdit_OverdriveMaximum.setPrefix('max. ')
        self.distMenuEdit_OverdriveMaximum.valueChanged.connect(self.adjustDistEnvWidgetMaximum)
        self.distMenuEdit_WaveshapeParts = QSpinBox()
        self.distMenuEdit_WaveshapeParts.setMinimum(1)
        self.distMenuEdit_WaveshapeParts.setValue(3)
        self.distMenuEdit_WaveshapeParts.setMaximum(99)
        self.distMenuEdit_WaveshapeParts.setSuffix(' parts')
        self.distMenuEdit_FMSource = QComboBox()
        self.distMenuEdit_FMSource.addItem('<src>')
        self.distMenuEdit_LofiBits = QSpinBox()
        self.distMenuEdit_LofiBits.setRange(1, 2**16)
        self.distMenuEdit_LofiBits.setValue(2**13)
        self.distMenuEdit_LofiBits.setSingleStep(64)
        self.distMenuEdit_LofiBits.setSuffix(' bits')
        self.distMenuEdit_NA = QLineEdit()
        self.distMenuEdit_NA.setText('N/A')
        self.distMenuEdit_NA.setEnabled(False)
        self.distMenuType.addItems(distTypes)
        self.distMenuType.currentTextChanged.connect(self.adjustDistMenuEdit)

        self.distMenuEdit = QStackedLayout()
        self.distMenuEdit.addWidget(self.distMenuEdit_OverdriveMaximum)
        self.distMenuEdit.addWidget(self.distMenuEdit_WaveshapeParts)
        self.distMenuEdit.addWidget(self.distMenuEdit_FMSource)
        self.distMenuEdit.addWidget(self.distMenuEdit_LofiBits)
        self.distMenuEdit.addWidget(self.distMenuEdit_NA)
        #todo: change THIS parameter over time, each, esp. FM and LoFi!

        self.distMenuLayout = QHBoxLayout()
        self.distMenuLayout.addWidget(QLabel('Distortion Envelopes'), 5)
        self.distMenuLayout.addWidget(self.distMenuType, 1)
        self.distMenuLayout.addLayout(self.distMenuEdit, 1)

        self.distEnvMainLayout = QVBoxLayout()
        self.distEnvMainLayout.addLayout(self.distMenuLayout)
        self.distEnvMainLayout.addLayout(self.distLayout)

        self.distEnvGroup = QGroupBox()
        self.distEnvGroup.setLayout(self.distEnvMainLayout)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.presetGroup, .5)
        self.mainLayout.addWidget(self.layerGroup, 1.5)
        self.mainLayout.addWidget(self.ampEnvGroup, 1)
        self.mainLayout.addWidget(self.freqEnvGroup, 1)
        self.mainLayout.addWidget(self.distEnvGroup, 1)

        self.setLayout(self.mainLayout)


    def initModelView(self):
        self.presetModel = DrumModel()
        self.presetList.setModel(self.presetModel)
        # change should trigger (autosave and) reload

        self.layerModel = LayerModel()
        self.layerList.setModel(self.layerModel)
        #self.layerList.selectionModel().currentChanged.connect(self.layerSelect)

        self.ampEnvModel = EnvelopeModel()
        self.ampEnvList.setModel(self.ampEnvModel)
        self.ampEnvList.selectionModel().currentChanged.connect(self.ampEnvSelected)
        self.ampEnvModel.layoutChanged.connect(self.ampEnvUpdate)

        self.freqEnvModel = EnvelopeModel()
        self.freqEnvList.setModel(self.freqEnvModel)
        self.freqEnvList.selectionModel().currentChanged.connect(self.freqEnvSelect)
        self.freqEnvModel.layoutChanged.connect(self.freqEnvUpdate)

        self.distEnvModel = EnvelopeModel()
        self.distEnvList.setModel(self.distEnvModel)
        self.distEnvList.selectionModel().currentChanged.connect(self.distEnvSelect)
        self.distEnvModel.layoutChanged.connect(self.distEnvUpdate)

        self.layerChooseAmpEnvList.setModel(self.ampEnvModel)
        self.layerChooseFreqEnvList.setModel(self.freqEnvModel)
        self.layerChooseDistEnvList.setModel(self.distEnvModel)

        self.distMenuEdit_FMSource.setModel(self.layerModel)


    def initData(self):
        self.ampEnvModel.insertNew(defaultAmpEnvelope)
        self.ampEnvList.selectionModel().setCurrentIndex(self.ampEnvModel.index(0), QItemSelectionModel.SelectCurrent)

        self.freqEnvModel.insertNew(defaultFreqEnvelope)
        self.freqEnvList.selectionModel().setCurrentIndex(self.freqEnvModel.index(0), QItemSelectionModel.SelectCurrent)

        self.distEnvModel.insertNew(defaultDistEnvelope)
        self.distEnvList.selectionModel().setCurrentIndex(self.distEnvModel.index(0), QItemSelectionModel.SelectCurrent)


    def adjustDistMenuEdit(self, choice):
        if choice == 'Overdrive':
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_OverdriveMaximum)
            self.adjustDistEnvWidgetMaximum(self.distMenuEdit_OverdriveMaximum.value())
        elif choice == 'Waveshape':
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_WaveshapeParts)
            self.adjustDistEnvWidgetMaximum(2)
        elif choice == 'FM':
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_FMSource)
            self.adjustDistEnvWidgetMaximum(2)
        elif choice == 'Lo-Fi':
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_LofiBits)
            self.adjustDistEnvWidgetMaximum(2)
        else:
            self.distMenuEdit.setCurrentWidget(self.distMenuEdit_NA)

    def adjustDistEnvWidgetMaximum(self, value):
        self.distEnvWidget.setDimensions(maxValue = value)


################################ MODEL FUNCTIONALITY ################################
#####################################################################################

############################ AMPLITUDE ENVELOPES ####################################

    def anyAmpEnv(self):
        return len(self.ampEnvModel.envelopes) > 0

    def currentAmpEnv(self):
        try:
            return self.ampEnvModel.envelopes[self.ampEnvList.currentIndex().row()]
        except IndexError:
            return None

    def ampEnvUpdate(self):
        self.ampEnvWidget.loadEnvelope(self.currentAmpEnv())

    def ampEnvSelected(self, current, previous = None):
        env = self.ampEnvModel.envelopes[current.row()]
        self.ampEnvWidget.loadEnvelope(env)

    def ampEnvAdd(self):
        # actually, open settings editor first
        self.ampEnvModel.insertNew(defaultAmpEnvelope)
        self.ampEnvModel.layoutChanged.emit()

    def ampEnvDelete(self):
        if self.anyAmpEnv():
            self.ampEnvModel.envelopes.remove(self.currentAmpEnv())
            self.ampEnvModel.layoutChanged.emit()

    def ampEnvRandomize(self):
        if self.anyAmpEnv():
            self.currentAmpEnv().randomize()

    def ampEnvOpenSettings(self):
        if self.anyAmpEnv():
            settingsDialog = SettingsDialog(self, type = 'amplitude', name = self.currentAmpEnv().name)
            if settingsDialog.exec_():
                name = settingsDialog.getName()
                pointNumber = settingsDialog.getPointNumber()
                value = settingsDialog.getSinglePointValue()
                assign = settingsDialog.getWhetherToAssign()

                if settingsDialog.clone:
                    pass
                    #ampEnvClone(self, name = name, pointNumber = pointNumber, value = value, assign = assign)
                else:
                    if pointNumber > 1:
                        self.currentAmpEnv().adjust(name = name, pointNumber = pointNumber)
                    else:
                        self.currentAmpEnv().adjust(name = name, points = EnvelopePoint(time = 0, value = value))

                    if assign:
                        self.layerChooseAmpEnvList.setCurrentIndex(self.ampEnvList.currentIndex().row())

                self.ampEnvModel.dataChanged.emit(self.ampEnvList.currentIndex(), self.ampEnvList.currentIndex())


############################ FREQUENCY ENVELOPES ####################################

    def currentFreqEnv(self):
        try:
            return self.freqEnvModel.envelopes[self.freqEnvList.selectedIndexes()[-1].row()]
        except IndexError:
            return None

    def freqEnvUpdate(self):
        self.freqEnvWidget.loadEnvelope(self.currentFreqEnv())

    def freqEnvSelect(self, current, previous = None):
        self.freqEnvWidget.loadEnvelope(self.freqEnvModel.envelopes[current.row()])

    def freqEnvAdd(self):
        # actually, open settings editor first
        self.freqEnvModel.insertNew(defaultFreqEnvelope)
        self.freqEnvModel.layoutChanged.emit()

    def freqEnvDelete(self):
        try:
            index = self.freqEnvList.selectedIndexes()[-1]
            del self.freqEnvModel.envelopes[index.row()]
            self.freqEnvModel.layoutChanged.emit()
            self.freqEnvList.clearSelection()
        except:
            pass

    def freqEnvRandomize(self):
        try:
            index = self.freqEnvList.selectedIndexes()[-1]
            self.freqEnvModel.envelopes[index.row()].randomize()
        except:
            pass

    def freqEnvOpenSettings(self):
        name = 'Wolfgang Frequenzgang'
        try:
            index = self.freqEnvList.selectedIndexes()[-1]
            self.freqEnvModel.envelopes[index.row()].adjust(name = name)
            self.freqEnvModel.dataChanged.emit(index, index)
        except:
            raise


############################ DISTORTION ENVELOPES ####################################

    def currentDistEnv(self):
        try:
            return self.distEnvModel.envelopes[self.distEnvList.selectedIndexes()[-1].row()]
        except IndexError:
            return None

    def distEnvUpdate(self):
        self.distEnvWidget.loadEnvelope(self.currentDistEnv())

    def distEnvSelect(self, current, previous = None):
        self.distEnvWidget.loadEnvelope(self.distEnvModel.envelopes[current.row()])

    def distEnvAdd(self):
        # actually, open settings editor first
        self.distEnvModel.insertNew(defaultDistEnvelope)
        self.distEnvModel.layoutChanged.emit()

    def distEnvDelete(self):
        try:
            index = self.distEnvList.selectedIndexes()[-1]
            del self.distEnvModel.envelopes[index.row()]
            self.distEnvModel.layoutChanged.emit()
            self.distEnvList.clearSelection()
        except:
            pass

    def distEnvRandomize(self):
        try:
            index = self.distEnvList.selectedIndexes()[-1]
            self.distEnvModel.envelopes[index.row()].randomize()
        except:
            pass

    def distEnvOpenSettings(self):
        name = 'hannes am saufen'
        try:
            index = self.distEnvList.selectedIndexes()[-1]
            self.distEnvModel.envelopes[index.row()].adjust(name = name)
            self.distEnvModel.dataChanged.emit(index, index)
        except:
            raise


# TODO: idea for layer effects: chorus / more precise stereo delay / .. ??


# deadline: hard cyber

# vortex: nordic horror industrial (BLACKHNO)

# UNC: die grüne demo

# revision: tunguska / tschernobyl
# game: johann lafers helilandeplatz