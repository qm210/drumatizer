from PyQt5.QtCore import QAbstractListModel, Qt
from random import choice
import json

from EnvelopeModel import EnvelopeEncoder

layerTypes = ['SIN', 'SAW', 'SQU', 'TRI', 'WHTNS', 'PRLNS']
distTypes = ['Overdrive', 'Waveshape', 'Lo-Fi']


class Layer:

    unitVolume = 1e-2
    unitDetune = 1e-3
    unitStereoDelay = 1e-5

    def __init__(self, amplEnv = None, freqEnv = None, distEnv = None, name = None, _hash = None, amplEnvHash = None, freqEnvHash = None, distEnvHash = None):
        self.name = name or self.talkSomeTeam210Shit()
        self.type = layerTypes[0]
        self.amplEnvHash = amplEnv._hash if amplEnv is not None else amplEnvHash
        self.freqEnvHash = freqEnv._hash if freqEnv is not None else freqEnvHash
        self.distEnvHash = distEnv._hash if distEnv is not None else distEnvHash
        self.distType = 'Overdrive'
        self.distParam = 2
        self.distOff = True
        self.phasemodSrcHash = None
        self.phasemodAmt = 0
        self.phasemodOff = True
        self.volume = 100
        self.mute = False
        self.detune = 0
        self.stereodelay = 0
        self._hash = _hash or hash(self)

    def __str__(self):
        volumeRepr = '{}%'.format(self.volume) if not self.mute else 'MUTED'
        return f'{self.name} ({volumeRepr})'

    def adjust(self, **args):
        if 'name' in args:
            self.name = args['name']
        if 'type' in args:
            self.type = args['type']
        if 'amplEnv' in args:
            self.amplEnvHash = args['amplEnv']._hash
        if 'freqEnv' in args:
            self.freqEnvHash = args['freqEnv']._hash
        if 'distEnv' in args:
            self.distEnvHash = args['distEnv']._hash
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
        if 'phasemodOff' in args:
            self.phasemodOff = args['phasemodOff']
        if 'phasemodAmt' in args:
            self.phasemodAmt = args['phasemodAmt']
        if 'phasemodSrcHash' in args:
            self.phasemodSrcHash = args['phasemodSrcHash']


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
            'They are smoking beer inside',
            'Style is not a crime'
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
            return self.layers[index.row()].__str__()

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

    def hashList(self):
        return [layer._hash for layer in self.layers]

    def indexOfHash(self, _hash):
        try:
            return self.hashList().index(_hash)
        except ValueError:
            return None

    def layerOfHash(self, _hash):
        index = self.indexOfHash(_hash)
        return self.layers[index] if index else None

class LayerEncoder(json.JSONEncoder):

    # pylint: disable=method-hidden
    def default(self, obj):
        if isinstance(obj, Layer):
            layerObj = {
                '__drumatizeLayer__': obj._hash,
                'name': obj.name,
                'type': obj.type,
                'amplEnvHash': obj.amplEnvHash,
                'freqEnvHash': obj.freqEnvHash,
                'distEnvHash': obj.distEnvHash,
                'distType': obj.distType,
                'distParam': obj.distParam,
                'distOff': obj.distOff,
                'volume': obj.volume,
                'mute': obj.mute,
                'detune': obj.detune,
                'stereodelay': obj.stereodelay,
                'phasemodOff': obj.phasemodOff,
                'phasemodAmt': obj.phasemodAmt,
                'phasemodSrcHash': obj.phasemodSrcHash
            }
            return layerObj
        else:
            return super().default(obj)

    @classmethod
    def decode(self, dict):
        if '__drumatizeLayer__' in dict:
            layer = Layer(
                name = dict['name'],
                amplEnvHash = dict['amplEnvHash'],
                freqEnvHash = dict['freqEnvHash'],
                distEnvHash = dict['distEnvHash'],
                _hash = dict['__drumatizeLayer__']
            )
            layer.type = dict['type']
            layer.distType = dict['distType']
            layer.distParam = dict['distParam']
            layer.distOff = dict['distOff']
            layer.volume = dict['volume']
            layer.mute = dict['mute']
            layer.detune = dict['detune']
            layer.stereodelay = dict['stereodelay']
            layer.phasemodOff = dict['phasemodOff']
            layer.phasemodAmt = dict['phasemodAmt']
            layer.phasemodSrcHash = dict['phasemodSrcHash']
            return layer
        return dict
