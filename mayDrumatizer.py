#########################################################################
## Drumatize Section of Drumatizer (development started at 2019/09/03)
## -- Renderer Section was written some days before... ;)
##
## by QM / Team210
#########################################################################

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

        self.maxTime = 2
        self.minValue = {'amplitude': 0, 'frequency':    20, 'distortion': 0}
        self.maxValue = {'amplitude': 1, 'frequency': 12000, 'distortion': 2}

        self.initLayouts()
        self.initSignals()
        self.initModelView()
        self.initData()

    def initLayouts(self):
        # drum widget
        self.drumList = QComboBox()
        self.drum_BtnAdd = QPushButton('+')
        self.drum_BtnClone = QPushButton('C')
        self.drum_BtnDel = QPushButton('–')
        self.drum_BtnEdit = QPushButton('...')
        self.drum_BtnExport = QPushButton('↗')
        self.drum_BtnImport = QPushButton('↘')
        self.drum_BtnRender = QPushButton('Render >>')

        self.drumLayout = QHBoxLayout()
        self.drumLayout.addWidget(QLabel('Drum:'))
        self.drumLayout.addWidget(self.drumList, 4)
        self.drumLayout.addWidget(self.drum_BtnAdd)
        self.drumLayout.addWidget(self.drum_BtnClone)
        self.drumLayout.addWidget(self.drum_BtnDel)
        self.drumLayout.addWidget(self.drum_BtnEdit)
        self.drumLayout.addWidget(self.drum_BtnExport)
        self.drumLayout.addWidget(self.drum_BtnImport)
        self.drumLayout.addWidget(self.drum_BtnRender)

        self.drumGroup = QGroupBox()
        self.drumGroup.setLayout(self.drumLayout)

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
        self.layerEditorType.setMinimumWidth(200)
        self.layerChooseAmplEnvList = QComboBox()
        self.layerChooseAmplEnvList.setMinimumWidth(200)
        self.layerChooseFreqEnvList = QComboBox()
        self.layerChooseFreqEnvList.setMinimumWidth(200)
        self.layerChooseDistEnvList = QComboBox()
        self.layerChooseDistEnvList.setMinimumWidth(200)
        self.layerChooseDistOff = QCheckBox('no pls')
        self.layerChooseDistEnvListLayout = QHBoxLayout()
        self.layerChooseDistEnvListLayout.addWidget(self.layerChooseDistEnvList)
        self.layerChooseDistEnvListLayout.addStretch()
        self.layerChooseDistEnvListLayout.addWidget(self.layerChooseDistOff)
        self.layerEditorVolumeSlider = QSlider(Qt.Horizontal)
        self.layerEditorVolumeSlider.setValue(100)
        self.layerEditorVolumeSlider.setRange(0, 200)
        self.layerEditorVolumeSpacer = QLabel('  ')
        self.layerEditorVolumeLabel = QLabel('100%')
        self.layerEditorVolumeLayout = QHBoxLayout()
        self.layerEditorVolumeLayout.addWidget(self.layerEditorVolumeSlider)
        self.layerEditorVolumeLayout.addWidget(self.layerEditorVolumeSpacer)
        self.layerEditorVolumeLayout.addWidget(self.layerEditorVolumeLabel)

        self.layerEditorLayout.addRow('Layer Name:', self.layerEditorName)
        self.layerEditorLayout.addRow('Layer Type:', self.layerEditorType)
        self.layerEditorLayout.addRow('Amplitude Env.:', self.layerChooseAmplEnvList)
        self.layerEditorLayout.addRow('Frequency Env.:', self.layerChooseFreqEnvList)
        self.layerEditorLayout.addRow('Distortion Env.:', self.layerChooseDistEnvListLayout)
        self.layerEditorLayout.addRow('Volume:', self.layerEditorVolumeLayout)
        self.layerEditorLayout.setVerticalSpacing(10)

        self.layerMenu = QVBoxLayout()
        self.layerMenu.addStretch()
        self.layerMenuBtnAdd = QPushButton('+')
        self.layerMenuBtnClone = QPushButton('C')
        self.layerMenuBtnEdit = QPushButton('...')
        self.layerMenuMuteBox = QCheckBox('Mute')
        self.layerMenuBtnRenderSolo = QPushButton('Solo >>')
        self.layerMenuBtnRnd = QPushButton('???')
        self.layerMenu.addWidget(self.layerMenuBtnAdd)
        self.layerMenu.addWidget(self.layerMenuBtnClone)
        self.layerMenu.addWidget(self.layerMenuBtnEdit)
        self.layerMenu.addWidget(self.layerMenuBtnRnd)
        self.layerMenu.addWidget(self.layerMenuMuteBox)
        self.layerMenu.addWidget(self.layerMenuBtnRenderSolo)

        self.layerMainLayout.addLayout(self.layerListLayout, 54)
        self.layerMainLayout.addLayout(self.layerMenu, 1)
        self.layerMainLayout.addWidget(self.layerEditor, 45)

        self.layerGroup = QGroupBox()
        self.layerGroup.setLayout(self.layerMainLayout)

        # amp envelope widget - todo: do something smart to combine layers
        self.amplEnvList = QListView()
        self.amplEnvMenu = QVBoxLayout()
        self.amplEnvWidget = EnvelopeWidget(self)
        self.amplEnvWidget.setDimensions(maxTime = self.maxTime, minValue = self.minValue['amplitude'], maxValue = self.maxValue['amplitude'])

        self.amplEnvMenu_BtnAdd = QPushButton('+')
        self.amplEnvMenu_BtnDel = QPushButton('–')
        self.amplEnvMenu_BtnRnd = QPushButton('???')
        self.amplEnvMenu_BtnEdit = QPushButton('...')

        self.amplEnvMenu.addStretch()
        self.amplEnvMenu.addWidget(self.amplEnvMenu_BtnAdd)
        self.amplEnvMenu.addWidget(self.amplEnvMenu_BtnDel)
        self.amplEnvMenu.addWidget(self.amplEnvMenu_BtnEdit)
        self.amplEnvMenu.addWidget(self.amplEnvMenu_BtnRnd)

        self.amplEnvLayout = QHBoxLayout()
        self.amplEnvLayout.addWidget(self.amplEnvList, 20)
        self.amplEnvLayout.addLayout(self.amplEnvMenu, 1)
        self.amplEnvLayout.addWidget(self.amplEnvWidget, 80)

        self.amplEnvMainLayout = QVBoxLayout()
        self.ampMenuLayout = QHBoxLayout()
        self.ampMenuLayout.addWidget(QLabel('Amplitude Envelopes'))
        self.ampMenuLayout.addStretch()
        self.amplEnvMenu_TryExpFitChkBox = QCheckBox('Try ExpDecay Fit')
        self.ampMenuLayout.addWidget(self.amplEnvMenu_TryExpFitChkBox)

        self.amplEnvMainLayout.addLayout(self.ampMenuLayout, 10)
        self.amplEnvMainLayout.addLayout(self.amplEnvLayout, 90)

        self.amplEnvGroup = QGroupBox()
        self.amplEnvGroup.setLayout(self.amplEnvMainLayout)

        # freq envelope widget
        self.freqEnvList = QListView()
        self.freqEnvMenu = QVBoxLayout()
        self.freqEnvWidget = EnvelopeWidget(self)
        self.freqEnvWidget.setDimensions(maxTime = self.maxTime, minValue = self.minValue['frequency'], maxValue = self.maxValue['frequency'], logValue = True)

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
        self.distEnvWidget.setDimensions(maxTime = self.maxTime, minValue = self.minValue['distortion'], maxValue = self.maxValue['distortion'])
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
        self.mainLayout.addWidget(self.drumGroup, .5)
        self.mainLayout.addWidget(self.layerGroup, 1.5)
        self.mainLayout.addWidget(self.amplEnvGroup, 1)
        self.mainLayout.addWidget(self.freqEnvGroup, 1)
        self.mainLayout.addWidget(self.distEnvGroup, 1)

        self.setLayout(self.mainLayout)


    def initSignals(self):
        self.layerChooseAmplEnvList.currentIndexChanged.connect(self.amplEnvSelectIndex)
        self.layerChooseFreqEnvList.currentIndexChanged.connect(self.freqEnvSelectIndex)
        self.layerChooseDistEnvList.currentIndexChanged.connect(self.distEnvSelectIndex)
        self.layerChooseDistOff.stateChanged.connect(lambda state: self.layerChooseDistEnvList.setEnabled(not state))
        self.layerEditorVolumeSlider.valueChanged.connect(lambda value: self.layerEditorVolumeLabel.setText('{}%'.format(value)))
        self.amplEnvMenu_BtnAdd.pressed.connect(self.amplEnvAdd)
        self.amplEnvMenu_BtnDel.pressed.connect(self.amplEnvDelete)
        self.amplEnvMenu_BtnRnd.pressed.connect(self.amplEnvRandomize)
        self.amplEnvMenu_BtnEdit.pressed.connect(self.amplEnvEditSettings)
        self.freqEnvMenu_BtnAdd.pressed.connect(self.freqEnvAdd)
        self.freqEnvMenu_BtnDel.pressed.connect(self.freqEnvDelete)
        self.freqEnvMenu_BtnRnd.pressed.connect(self.freqEnvRandomize)
        self.freqEnvMenu_BtnEdit.pressed.connect(self.freqEnvEditSettings)
        self.distEnvMenu_BtnAdd.pressed.connect(self.distEnvAdd)
        self.distEnvMenu_BtnDel.pressed.connect(self.distEnvDelete)
        self.distEnvMenu_BtnRnd.pressed.connect(self.distEnvRandomize)
        self.distEnvMenu_BtnEdit.pressed.connect(self.distEnvEditSettings)
        self.distMenuEdit_OverdriveMaximum.valueChanged.connect(self.adjustDistEnvWidgetMaximum)
        self.distMenuType.currentTextChanged.connect(self.adjustDistMenuEdit)


    def initModelView(self):
        self.drumModel = DrumModel()
        self.drumList.setModel(self.drumModel)
        # change should trigger (autosave and) reload

        self.layerModel = LayerModel()
        self.layerList.setModel(self.layerModel)
        self.layerList.selectionModel().currentChanged.connect(self.layerOnSelection)

        self.amplEnvModel = EnvelopeModel()
        self.amplEnvList.setModel(self.amplEnvModel)
        self.amplEnvList.selectionModel().currentChanged.connect(self.amplEnvOnSelection)
        self.amplEnvModel.layoutChanged.connect(self.amplEnvUpdate) # TODO: check one day: do we need these?

        self.freqEnvModel = EnvelopeModel()
        self.freqEnvList.setModel(self.freqEnvModel)
        self.freqEnvList.selectionModel().currentChanged.connect(self.freqEnvOnSelection)
        self.freqEnvModel.layoutChanged.connect(self.freqEnvUpdate)

        self.distEnvModel = EnvelopeModel()
        self.distEnvList.setModel(self.distEnvModel)
        self.distEnvList.selectionModel().currentChanged.connect(self.distEnvOnSelection)
        self.distEnvModel.layoutChanged.connect(self.distEnvUpdate)

        self.layerChooseAmplEnvList.setModel(self.amplEnvModel)
        #SHIT self.layerChooseAmplEnvList.currentIndexChanged.connect()
        self.layerChooseFreqEnvList.setModel(self.freqEnvModel)
        self.layerChooseDistEnvList.setModel(self.distEnvModel)

        self.distMenuEdit_FMSource.setModel(self.layerModel)


    def initData(self):
        defaultDrum = Drum()
        defaultLayer = Layer(amplEnv = defaultAmplEnvelope, freqEnv = defaultFreqEnvelope, distEnv = defaultDistEnvelope)

        defaultDrum.addLayer(defaultLayer)
        defaultDrum.addAmplEnv(defaultAmplEnvelope)
        defaultDrum.addFreqEnv(defaultFreqEnvelope)
        defaultDrum.addDistEnv(defaultDistEnvelope)

        for env in defaultDrum.amplEnvs:
            self.amplEnvInsertAndSelect(env)

        for env in defaultDrum.freqEnvs:
            self.freqEnvInsertAndSelect(env)

        for env in defaultDrum.distEnvs:
            self.distEnvInsertAndSelect(env)

        for layer in defaultDrum.layers:
            print(layer.name)
            self.layerInsertAndSelect(layer)

        # here one could load'em all!
        self.drumInsertAndSelect(defaultDrum)

        #self.layerChooseAmplEnvList.setCurrentIndex(self.amplEnvList.currentIndex().row())
        #    self.layerChooseFreqEnvList.setCurrentIndex(self.freqEnvList.currentIndex().row())
        #    self.layerChooseDistEnvList.setCurrentIndex(self.distEnvList.currentIndex().row())

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
        self.maxValue['distortion'] = value
        self.distEnvWidget.setDimensions(maxValue = value)


################################ MODEL FUNCTIONALITY ################################
#####################################################################################

################################## DRUM DRUMS #####################################
    def drumInsertAndSelect(self, drum, position = None):
        self.drumModel.insertNew(drum, position)
        index = self.drumModel.indexOf(drum)
        if index.isValid():
            self.drumList.setCurrentIndex(index.row())

##################################### LAYERS ########################################
    def layerOnSelection(self, current, previous = None):
        layer = self.layerModel.layers[current.row()]
        self.layerEditorName.setText(layer.name)
        self.layerEditorType.setCurrentText(layer.type)
        self.layerChooseAmplEnvList.setCurrentText(layer.amplEnv.name)
        self.layerChooseFreqEnvList.setCurrentText(layer.freqEnv.name)
        self.layerChooseDistEnvList.setCurrentText(layer.distEnv.name)
        self.layerChooseDistOff.setEnabled(layer.distOff)
        self.layerEditorVolumeSlider.setValue(layer.volume)
        self.layerMenuMuteBox.setEnabled(layer.mute)


    def layerInsertAndSelect(self, layer, position = None):
        self.layerModel.insertNew(layer, position)
        index = self.layerModel.indexOf(layer)
        if index.isValid():
            self.layerList.selectionModel().setCurrentIndex(index, QItemSelectionModel.SelectCurrent)

############################ AMPLITUDE ENVELOPES ####################################

    def anyAmplEnv(self, moreThan = 0):
        return len(self.amplEnvModel.envelopes) > moreThan

    def currentAmplEnv(self):
        try:
            return self.amplEnvModel.envelopes[self.amplEnvList.currentIndex().row()]
        except IndexError:
            return None

    def amplEnvUpdate(self):
        self.amplEnvWidget.loadEnvelope(self.currentAmplEnv())

    def amplEnvOnSelection(self, current, previous = None):
        self.amplEnvWidget.loadEnvelope(self.amplEnvModel.envelopes[current.row()])

    def amplEnvSelect(self, envelope):
        index = self.amplEnvModel.indexOf(envelope)
        if index is not None:
            self.amplEnvList.selectionModel().setCurrentIndex(index, QItemSelectionModel.SelectCurrent)

    def amplEnvSelectIndex(self, index):
        self.amplEnvList.selectionModel().setCurrentIndex(self.amplEnvModel.createIndex(index, 0), QItemSelectionModel.SelectCurrent)

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

            if pointNumber > 1:
                self.currentAmplEnv().adjust(name = name, pointNumber = pointNumber)
            else:
                self.currentAmplEnv().adjust(name = name, points = EnvelopePoint(time = 0, value = value))

            if assign:
                self.layerChooseAmplEnvList.setCurrentIndex(self.amplEnvList.currentIndex().row())

            self.amplEnvModel.dataChanged.emit(self.amplEnvList.currentIndex(), self.amplEnvList.currentIndex())


    def amplEnvDelete(self):
        if self.anyAmplEnv(moreThan = 1):
            index = self.amplEnvModel.indexOf(self.currentAmplEnv()).row()

            self.amplEnvModel.envelopes.remove(self.currentAmplEnv())
            self.amplEnvModel.layoutChanged.emit()

            if index == self.amplEnvModel.rowCount():
                self.amplEnvList.setCurrentIndex(self.amplEnvModel.indexOf(self.amplEnvModel.lastEnvelope()))

    def amplEnvRandomize(self):
        if self.anyAmplEnv():
            env = self.currentAmplEnv()
            env.randomize(self.maxTime, self.minValue[env.type], self.maxValue[env.type])
            self.amplEnvWidget.update()


############################ FREQUENCY ENVELOPES ####################################

    def anyFreqEnv(self, moreThan = 0):
        return len(self.freqEnvModel.envelopes) > moreThan

    def currentFreqEnv(self):
        try:
            return self.freqEnvModel.envelopes[self.freqEnvList.currentIndex().row()]
        except IndexError:
            return None

    def freqEnvUpdate(self):
        self.freqEnvWidget.loadEnvelope(self.currentFreqEnv())
        print(self.currentFreqEnv())

    def freqEnvOnSelection(self, current, previous = None):
        env = self.freqEnvModel.envelopes[current.row()]
        self.freqEnvWidget.loadEnvelope(env)

    def freqEnvSelect(self, envelope):
        index = self.freqEnvModel.indexOf(envelope)
        if index is not None:
            self.freqEnvList.selectionModel().setCurrentIndex(index, QItemSelectionModel.SelectCurrent)

    def freqEnvSelectIndex(self, index):
        self.freqEnvList.selectionModel().setCurrentIndex(self.freqEnvModel.createIndex(index, 0), QItemSelectionModel.SelectCurrent)

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

            if pointNumber > 1:
                self.currentFreqEnv().adjust(name = name, pointNumber = pointNumber)
            else:
                self.currentFreqEnv().adjust(name = name, points = EnvelopePoint(time = 0, value = value))

            if assign:
                self.layerChooseFreqEnvList.setCurrentIndex(self.freqEnvList.currentIndex().row())

            self.freqEnvModel.dataChanged.emit(self.freqEnvList.currentIndex(), self.freqEnvList.currentIndex())


    def freqEnvDelete(self):
        if self.anyFreqEnv(moreThan = 1):
            index = self.freqEnvModel.indexOf(self.currentFreqEnv()).row()

            self.freqEnvModel.envelopes.remove(self.currentFreqEnv())
            self.freqEnvModel.layoutChanged.emit()

            if index == self.freqEnvModel.rowCount():
                self.freqEnvList.setCurrentIndex(self.freqEnvModel.indexOf(self.freqEnvModel.lastEnvelope()))

    def freqEnvRandomize(self):
        if self.anyFreqEnv():
            env = self.currentFreqEnv()
            env.randomize(self.maxTime, self.minValue[env.type], self.maxValue[env.type])
            self.freqEnvWidget.update()


############################ DISTORTION ENVELOPES ####################################

    def anyDistEnv(self, moreThan = 0):
        return len(self.distEnvModel.envelopes) > moreThan

    def currentDistEnv(self):
        try:
            return self.distEnvModel.envelopes[self.distEnvList.currentIndex().row()]
        except IndexError:
            return None

    def distEnvUpdate(self):
        self.distEnvWidget.loadEnvelope(self.currentDistEnv())

    def distEnvOnSelection(self, current, previous = None):
        env = self.distEnvModel.envelopes[current.row()]
        self.distEnvWidget.loadEnvelope(env)

    def distEnvSelect(self, envelope):
        index = self.distEnvModel.indexOf(envelope)
        if index is not None:
            self.distEnvList.selectionModel().setCurrentIndex(index, QItemSelectionModel.SelectCurrent)

    def distEnvSelectIndex(self, index):
        self.distEnvList.selectionModel().setCurrentIndex(self.distEnvModel.createIndex(index, 0), QItemSelectionModel.SelectCurrent)

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

            if pointNumber > 1:
                self.currentDistEnv().adjust(name = name, pointNumber = pointNumber)
            else:
                self.currentDistEnv().adjust(name = name, points = EnvelopePoint(time = 0, value = value))

            if assign:
                self.layerChooseDistEnvList.setCurrentIndex(self.distEnvList.currentIndex().row())

            self.distEnvModel.dataChanged.emit(self.distEnvList.currentIndex(), self.distEnvList.currentIndex())


    def distEnvDelete(self):
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