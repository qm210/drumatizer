from PyQt5.QtWidgets import * # pylint: disable=unused-import
from PyQt5.QtCore import Qt, QFile, QFileInfo, QIODevice, QByteArray, QBuffer, QTextStream, pyqtSignal
from PyQt5.QtMultimedia import QAudioOutput, QAudioFormat, QAudioDeviceInfo, QAudio
from datetime import datetime
from random import randint

from SFXGLWidget import SFXGLWidget

class MayRenderer(QWidget):

    shouldsave = pyqtSignal()

    texsize = 512
    samplerate = 44100

    shaderHeader = '#version 130\n uniform float iTexSize;\n uniform float iBlockOffset;\n uniform float iSampleRate;\n\n'

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.blocksize = (self.texsize*self.texsize)/self.samplerate

        self.initState()
        self.initUI()
        self.initAudio()

    def initState(self):
        self.playing = False
        self.initVolume = 0.3

        self.useWatchFile = False
        self.watchFileName = ''
        self.storeCodeIfNotWatching = ''

    def initUI(self):
        self.mainLayout = QVBoxLayout()
        self.codeLayout = QVBoxLayout()
        self.codeButtonBar = QHBoxLayout()
        self.codeWatchFileBar = QHBoxLayout()
        self.renderBar = QHBoxLayout()
        self.playbackBar = QHBoxLayout()
        self.renderGroup = QGroupBox()
        self.renderGroupLayout = QVBoxLayout()
        self.renderGroupLayout.addLayout(self.renderBar)
        self.renderGroupLayout.addLayout(self.playbackBar)
        self.renderGroup.setLayout(self.renderGroupLayout)
        self.renderGroup.setObjectName("renderGroup")

        self.codeGroup = QGroupBox()
        self.buttonCopy = QPushButton('↬ Clipboard', self)
        self.buttonCopy.clicked.connect(self.copyToClipboard)
        self.buttonPaste = QPushButton('Paste ↴', self)
        self.buttonPaste.clicked.connect(self.pasteClipboard)
        self.buttonClear = QPushButton('×', self)
        self.buttonClear.clicked.connect(self.clearEditor)
        self.codeEditor = QPlainTextEdit(self)
        self.codeEditor.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        #self.codeEditor.setCenterOnScroll(True)
        #self.codeEditor.textChanged.formatEditor()) # this gives a recursion problem, but how to filter e.g. tabs?
        self.codeEditor.cursorPositionChanged.connect(self.updatePosLabel)
        self.codeEditor.setTabStopWidth(14)
        self.watchFileCheckBox = QCheckBox('watch file:', self)
        self.watchFileCheckBox.stateChanged.connect(self.toggleWatchFile)
        self.watchFileNameBox = QLineEdit(self)
        self.watchFileNameBox.setPlaceholderText('use GLSL code file instead of the above editor...')
        self.watchFileNameBox.textChanged.connect(self.setWatchFileName)
        self.buttonWatchFile = QPushButton('...', self)
        self.buttonWatchFile.clicked.connect(self.chooseWatchFile)

        self.renderButton = QPushButton(self)
        self.renderButton.clicked.connect(self.pressRenderShader)
        self.renderLengthBox = QDoubleSpinBox(self)
        self.renderLengthBox.setMinimum(0)
        self.renderLengthBox.setValue(4*self.blocksize - .01)
        self.renderLengthBox.setSingleStep(self.blocksize)
        self.renderLengthBox.setSuffix(' sec')
        self.renderLengthBox.setToolTip('render length')
        self.renderBpmBox = QSpinBox(self)
        self.renderBpmBox.setRange(1, 999)
        self.renderBpmBox.setValue(160)
        self.renderBpmBox.setPrefix('BPM ')
        self.renderBpmBox.setToolTip('--> determines SPB')
        self.playbackVolumeSlider = QSlider(Qt.Horizontal)
        self.playbackVolumeSlider.setMaximum(100)
        self.playbackVolumeSlider.setValue(self.initVolume * 100)
        self.playbackVolumeSlider.setToolTip('volume')
        self.playbackVolumeSlider.sliderMoved.connect(self.setVolume)
        self.renderBar.addWidget(self.renderButton, 60)
        self.renderBar.addWidget(self.renderBpmBox, 20)
        self.renderBar.addWidget(self.renderLengthBox, 20)

        self.progressBar = QProgressBar(self)
        self.progressBar.setEnabled(False)
        self.pauseButton = QPushButton(self)
        self.pauseButton.setEnabled(False)
        self.pauseButton.clicked.connect(self.pressPauseButton)
        self.playbackBar.addWidget(self.progressBar, 60)
        self.playbackBar.addWidget(self.playbackVolumeSlider, 20)
        self.playbackBar.addWidget(self.pauseButton, 20)

        self.codeButtonBar.addWidget(self.buttonCopy)
        self.codeButtonBar.addWidget(self.buttonPaste)
        self.codeButtonBar.addWidget(self.buttonClear)
        self.codeWatchFileBar.addWidget(self.watchFileCheckBox)
        self.codeWatchFileBar.addWidget(self.watchFileNameBox)
        self.codeWatchFileBar.addWidget(self.buttonWatchFile)
        self.codeHeader = QHBoxLayout()
        self.codePosLabel = QLabel('(0,0)')
        self.codeHeader.addWidget(QLabel('GLSL code'))
        self.codeHeader.addStretch()
        self.codeHeader.addWidget(self.codePosLabel)
        self.codeLayout.addLayout(self.codeHeader)
        self.codeLayout.addLayout(self.codeButtonBar)
        self.codeLayout.addWidget(self.codeEditor)
        self.codeLayout.addLayout(self.codeWatchFileBar)
        self.codeGroup.setLayout(self.codeLayout)

        self.mainLayout.addWidget(self.codeGroup)
        self.mainLayout.addWidget(self.renderGroup)

        self.updatePlayingUI()

        self.setLayout(self.mainLayout)

    def updatePlayingUI(self, keepActive = False):
        self.renderButton.setText('shut the fuck up' if self.playing else 'send to hell')
        if not self.playing and not keepActive:
            self.progressBar.setValue(0)
        self.progressBar.setEnabled(self.playing if not keepActive else True)
        self.pauseButton.setEnabled(self.playing if not keepActive else True)
        self.pauseButton.setText('||' if (self.playing and self.audiooutput.state() != QAudio.SuspendedState) else '▶')

    def initAudio(self):
        self.audioformat = QAudioFormat()
        self.audioformat.setSampleRate(self.samplerate)
        self.audioformat.setChannelCount(2)
        self.audioformat.setSampleSize(32)
        self.audioformat.setCodec('audio/pcm')
        self.audioformat.setByteOrder(QAudioFormat.LittleEndian)
        self.audioformat.setSampleType(QAudioFormat.Float)
        # self.audiodeviceinfo = QAudioDeviceInfo(QAudioDeviceInfo.defaultOutputDevice())

        self.audiooutput = QAudioOutput(self.audioformat)
        self.audiooutput.setVolume(self.initVolume)

    def paste(self, source):
        self.codeEditor.clear()
        source = source.replace('    ','\t').replace('   ', '\t')
        self.codeEditor.insertPlainText(source)
        self.codeEditor.setFocus()
        self.codeEditor.ensureCursorVisible()

    def pasteClipboard(self):
        self.paste(self.shaderHeader + QApplication.clipboard().text())

    def copyToClipboard(self):
        print("TODO: Implement copyToClipboard()")
        self.codeEditor.setFocus()

    def clearEditor(self):
        self.codeEditor.setPlainText('')
        self.codeEditor.setFocus()

    def updatePosLabel(self):
        cursor = self.codeEditor.textCursor()
        self.codePosLabel.setText(f'({cursor.blockNumber()},{cursor.positionInBlock()})')

#    def formatEditor(self):
#        plainText = self.codeEditor.toPlainText().replace('\t', 4*' ')
#        self.codeEditor.setPlainText(plainText)

    def toggleWatchFile(self, state):
        if not self.useWatchFile and state == Qt.Checked:
            self.storeCodeIfNotWatching = self.codeEditor.toPlainText()

        self.useWatchFile = (state == Qt.Checked)
        self.codeEditor.setEnabled(not self.useWatchFile)

        if self.useWatchFile:
            self.showWatchFileInfo()
        else:
            self.codeEditor.setPlainText(self.storeCodeIfNotWatching)

    def chooseWatchFile(self):
        dialogResult = QFileDialog.getOpenFileName(self, 'Choose file with GLSL code', '', 'GLSL files (*.glsl);;All files (*)')
        print(dialogResult)
        self.watchFileNameBox.setText(dialogResult[0])
        self.watchFileCheckBox.setCheckState(Qt.Checked)

        self.shouldsave.emit()

    def setWatchFileName(self):
        self.watchFileName = self.watchFileNameBox.text()
        self.showWatchFileInfo()

    def showWatchFileInfo(self):
        if self.useWatchFile:
            fileInfo = QFileInfo(self.watchFileName)
            infoText = 'use code from file:\n' + self.watchFileName + '\n' + ('(exists)' if fileInfo.exists() else '(doesn\'t exist)')
            self.codeEditor.setPlainText(infoText)

    def pressRenderShader(self):
        self.playing = not self.playing
        if self.playing :
            self.renderShaderAndPlay()
        else :
            self.stopShader()

    def pressPauseButton(self):
        state = self.audiooutput.state()

        if state == QAudio.ActiveState:
            self.audiooutput.suspend()
        elif state == QAudio.SuspendedState:
            self.audiooutput.resume()

        self.updatePlayingUI(keepActive = True)

    def stopShader(self):
        self.audiooutput.stop()
        self.updatePlayingUI()

    def renderShaderAndPlay(self):
        self.playing = True
        self.updatePlayingUI()

        # this is the SUPER FUN BITCRUSHER for the test shader
        nr_bits = randint(128, 8192)

        shaderSource = self.shaderHeader + """
void main()
{
   float t = (iBlockOffset + gl_FragCoord.x + gl_FragCoord.y*iTexSize) / iSampleRate;
   t = floor(t*BITS.) / BITS.;
   vec2 s = .2 * vec2(sin(2.*3.14159*49.*t*(1.+t))); // let's make it fun and squeaky
   vec2 v  = floor((0.5+0.5*s)*65535.0);
   vec2 vl = mod(v,256.0)/255.0;
   vec2 vh = floor(v/256.0)/255.0;
   gl_FragColor = vec4(vl.x,vh.x,vl.y,vh.y);
}
"""
        shaderSource = shaderSource.replace('BITS', str(nr_bits))
        print(nr_bits, 'bits for the SUPER FUN BITCRUSHER in the test shader.')

        starttime = datetime.now()

        try:
            if self.useWatchFile:
                watchFile = QFile(self.watchFileName)
                if not watchFile.open(QFile.ReadOnly | QFile.Text):
                    QMessageBox.warning(self, "Öhm... blöd.", "File öffnen ging nicht. Is genügend Pfeffer drauf?")
                    self.playing = False
                    self.updatePlayingUI()
                    return
                textStream = QTextStream(watchFile)
                textStream.setCodec('utf-8')
                shaderSource = self.shaderHeader + textStream.readAll()

            else:
                code = self.codeEditor.toPlainText()
                if code:
                    shaderSource = code

        except:
            raise

        uniforms = {}

        SPB = 60 / float(self.renderBpmBox.value())
        uniforms.update({'SPB': SPB})

        print(shaderSource)
        print(self.renderLengthBox.value())

        try:
            duration = self.renderLengthBox.value()
        except:
            print('couldn\'t read duration field. take 10secs.')
            duration = 10

        glwidget = SFXGLWidget(self, self.audioformat.sampleRate(), duration, self.texsize, moreUniforms = uniforms)

        glwidget.show()
        self.log = glwidget.newShader(shaderSource)
        print(self.log)
        self.music = glwidget.music
        glwidget.hide()
        glwidget.destroy()

        if self.music == None :
            return

        self.renderLengthBox.setValue(round(glwidget.duration_real, 2) - .01)

        self.bytearray = QByteArray(self.music)

        self.audiobuffer = QBuffer(self.bytearray)
        self.audiobuffer.open(QIODevice.ReadOnly)

        endtime = datetime.now()
        el = endtime - starttime
        print("Compile time: {:.3f}s".format(el.total_seconds()))

        self.audiooutput.stop()
        self.audiooutput.start(self.audiobuffer)

        self.audiooutput.setNotifyInterval(100)
        self.audiooutput.stateChanged.connect(self.updatePlayingUI)

        self.progressBar.setMaximum(self.audiobuffer.size())
        self.audiooutput.notify.connect(self.proceedAudio)

    def proceedAudio(self):
        # print(self.audiobuffer.pos() / self.audioformat.sampleRate())
        self.progressBar.setValue(self.audiobuffer.pos())
        if self.audiobuffer.atEnd():
            self.audiooutput.stop()
            self.playing = False
        self.updatePlayingUI()

    def setVolume(self):
        self.audiooutput.setVolume(self.playbackVolumeSlider.value() * .01)
