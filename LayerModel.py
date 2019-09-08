from PyQt5.QtCore import QAbstractListModel, Qt
from random import choice

layerTypes = ['SIN', 'SAW', 'SQU', 'TRI', 'WHTNS', 'PRLNS']
distTypes = ['Overdrive', 'Waveshape', 'FM', 'Lo-Fi']


class Layer:

    unitVolume = 1e-2
    unitDetune = 1e-3
    unitStereoDelay = 1e-6

    def __init__(self, amplEnv = None, freqEnv = None, distEnv = None):
        self.name = self.talkSomeTeam210Shit()
        self.type = layerTypes[0]
        self.amplEnv = amplEnv
        self.freqEnv = freqEnv
        self.distEnv = distEnv
        self.distType = 'Overdrive'
        self.distParam = 2
        self.distOff = True
        self.volume = 100
        self.mute = False
        self.detune = 0
        self.stereodelay = 0
        # TODO: change stereo-delay per sample -- extend the synth in order to assemble L and R separately?
        # for now, can just apply chorus in .may language separately

    def __repr__(self):
        volumeRepr = '{}%'.format(self.volume) if not self.mute else 'MUTED'
        return '{} ({} × {} × {})'.format(self.name, volumeRepr, self.type, self.amplEnv.name)

    def adjust(self, **args):
        if 'name' in args:
            self.name = args['name']
        if 'type' in args:
            self.type = args['type']
        if 'amplEnv' in args:
            self.amplEnv = args['amplEnv']
        if 'freqEnv' in args:
            self.freqEnv = args['freqEnv']
        if 'distEnv' in args:
            self.distEnv = args['distEnv']
        if 'distType' in args:
            self.distType = args['distType']
        if 'distParam' in args:
            self.distParam = args['distParam']
        if 'distOff' in args:
            self.distOff = args['distOff']
        if 'volume' in args:
            self.volume = args['volume']
        if 'mute' in args:
            self.mute = args['mute']
        if 'detune' in args:
            self.detune = args['detune']
        if 'stereodelay' in args:
            self.stereodelay = args['stereodelay']


    def talkSomeTeam210Shit(self, skip = []):
        '''
        putting the FUN in FUNction!
        '''
        allSentences = [
            'Are you ready for QoodMusic?',
            'Is this already layer NR4?',
            'Is this French Cheese!?',
            'Once you offend, you cannot stop',
            'Something with 150 kcal',
            'Just. A. Psychological. Effect!',
            'Sucht euch mal besser einen Musiker',
            'Aber irgendwas\'jaimmer',
            'Ah, der Bus mit den Leuten!',
            'Vote for Team210, these are cool guys',
            'More Currrrrrrrrrrrrry',
            'From the guys that brought to you: \'Für Elite\'',
            'I hope these Germans are here on friendly terms',
            'QM might have lost his t-shirt in your sauna..?',
            'PFEFFERSPRAY',
            'HEY BROSKI; WHAT\'S UP, BROSKI??',
            'you have to be in the lake to be the lake',
            'They are smoking beer inside'
        ]
        sentences = [s for s in allSentences if s not in skip]
        if sentences:
            return choice(sentences)
        else:
            suffix = '!'
            while True:
                sentence = 'Now you\'re just lazy' + suffix
                if sentence not in skip:
                    return sentence
                suffix = '...' + suffix


class LayerModel(QAbstractListModel):

    def __init__(self, *args, layers = None, **kwargs):
        super(LayerModel, self).__init__(*args, **kwargs)
        self.layers = layers or []
        self.newestIndex = len(self.layers) - 1

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.layers[index.row()].__repr__()

    def rowCount(self, index = None):
        return len(self.layers)

    def indexOf(self, layer):
        try:
            numericalIndex = self.layers.index(layer)
            modelIndex = self.createIndex(numericalIndex, 0)
            if modelIndex.isValid():
                return modelIndex
        except ValueError:
            return None

    def emitAllChanged(self):
        self.dataChanged.emit(self.createIndex(0,0), self.createIndex(self.rowCount(),0))

    def clear(self):
        self.layers = []
        self.emitAllChanged()

    def clearAndRefill(self, layers):
        self.layers = layers
        self.emitAllChanged()

    def insertNew(self, layer, position = None):
        if position is not None:
            self.layers.insert(position, layer)
            self.newestIndex = position
        else:
            self.layers.append(layer)
            self.newestIndex = len(self.layers) - 1

    def newestLayer(self):
        try:
            return self.layers[self.newestIndex]
        except:
            return None

    def lastLayer(self):
        if self.layers:
            return self.layers[-1]
        else:
            return None

    def adjust(self, numericalIndex, **args):
        if self.layers:
            self.layers[numericalIndex].adjust(**args)

    def adjustNewest(self, **args):
        self.adjust(self.newestIndex, **args)

    def nameExists(self, name):
        return name in self.nameList()

    def nameList(self):
        return [layer.name for layer in self.layers]

    def swapLayers(self, numericalIndex, numericalNextIndex):
        if numericalIndex != numericalNextIndex:
            self.layers[numericalIndex], self.layers[numericalNextIndex] = self.layers[numericalNextIndex], self.layers[numericalIndex]
            self.emitAllChanged()