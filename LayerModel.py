from PyQt5.QtCore import QAbstractListModel, Qt
from random import choice

layerTypes = ['Sine Oscillator', 'Saw Oscillator', 'Square Oscillator', 'Triangle Osciallator', 'White Pseudonoise', 'Perlin Noise']
distTypes = ['Overdrive', 'Waveshape', 'FM', 'Lo-Fi']


class Layer:

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
        # TODO: change stereo-delay per sample -- extend the synth in order to assemble L and R separately?
        # for now, can just apply chorus in .may language separately

    def __repr__(self):
        if self.mute:
            return 'MUTE {} ({})'.format(self.name, self.type)
        else:
            return '{}% {} ({})'.format(self.volume, self.name, self.type)

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


    def talkSomeTeam210Shit(self):
        '''
        putting the FUN in FUNction!
        '''
        return choice([
            'Are you ready for QoodMusic?',
            'Is this already layer NR4?',
            'Is this French Cheese!?',
            'Once you offend, you cannot stop',
            'Something with 150 kcal',
            'Is this a psychological effect?',
            'Sucht euch mal besser einen Musiker',
            'Irgendwas is ja immir',
            'Ah, der Bus mit den Leuten!',
            'You love Team210, secretly',
            'More Curry',
            'From the guys that brought to you: \'Für Elite\'',
            'I hope these Germans are here on friendly purpose',
            'QM might have lost his t-shirt in your sauna..?',
            'PFEFFERSPRAY',
            'you have to be in the lake to be the lake'
        ])


class LayerModel(QAbstractListModel):

    def __init__(self, *args, layers = None, **kwargs):
        super(LayerModel, self).__init__(*args, **kwargs)
        self.layers = layers or []
        self.newestIndex = len(self.layers) - 1

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.layers[index.row()].name

    def rowCount(self, index):
        return len(self.layers)

    def indexOf(self, layer):
        try:
            numericalIndex = self.layers.index(layer)
            modelIndex = self.createIndex(numericalIndex, 0)
            if modelIndex.isValid():
                return modelIndex
        except ValueError:
            return None

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
