from PyQt5.QtCore import QAbstractListModel, Qt
import json

from LayerModel import LayerEncoder
from EnvelopeModel import EnvelopeEncoder

class Drum:

    def __init__(self, name = None, type = None):
        self.name = name or 'are you DRUMATIZED yet?'
        # idea: preset list will be grouped by type
        self.type = type or 'Asskick'
        self.iLike = 0
        # each drum holds an arbitrary amount of layers and envelopes of each kind
        self.layers = []
        self.amplEnvs = []
        self.freqEnvs = []
        self.distEnvs = []
        # '...' menu: enter name, type, option to purge unused envelopes, also the 'drum awesomeness', for the ranking ;)

    def __str__(self):
        return self.name # '{} -- {}'.format(self.type.upper(), self.name)

    def adjust(self, **args):
        if 'name' in args:
            self.name = args['name']
        if 'type' in args:
            self.type = args['type']
        if 'iLike' in args:
            self.iLike = args['iLike']
        if 'layers' in args:
            self.layers = args['layers']
        if 'amplEnvs' in args:
            self.amplEnvs = args['amplEnvs']
        if 'freqEnvs' in args:
            self.freqEnvs = args['freqEnvs']
        if 'distEnvs' in args:
            self.distEnvs = args['distEnvs']

    def addLayer(self, layer):
        self.layers.append(layer)

    def addAmplEnv(self, env):
        self.amplEnvs.append(env)

    def addFreqEnv(self, env):
        self.freqEnvs.append(env)

    def addDistEnv(self, env):
        self.distEnvs.append(env)

class DrumModel(QAbstractListModel):

    def __init__(self, *args, drums = None, **kwargs):
        super(DrumModel, self).__init__(*args, **kwargs)
        self.drums = drums or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.drums[index.row()].__str__()

    def rowCount(self, index = None):
        return len(self.drums)

    def indexOf(self, drum):
        try:
            numericalIndex = self.drums.index(drum)
            modelIndex = self.createIndex(numericalIndex, 0)
            if modelIndex.isValid():
                return modelIndex
        except ValueError:
            return None

    def emitAllChanged(self):
        self.dataChanged.emit(self.createIndex(0,0), self.createIndex(self.rowCount(),0))

    def clear(self):
        self.drums = []
        self.emitAllChanged()

    def clearAndRefill(self, drums):
        self.drums = drums
        self.emitAllChanged()

    def insertNew(self, drum, position = None):
        if position is not None:
            self.drums.insert(position, drum)
            self.newestIndex = position
        else:
            self.drums.append(drum)
            self.newestIndex = len(self.drums) - 1

    def newestDrum(self):
        try:
            return self.drums[self.newestIndex]
        except:
            return None

    def lastDrum(self):
        if self.drums:
            return self.drums[-1]
        else:
            return None

    def adjust(self, numericalIndex, **args):
        if self.drums:
            self.drums[numericalIndex].adjust(**args)

    def adjustNewest(self, **args):
        self.adjust(self.newestIndex, **args)

    def nameExists(self, name):
        return name in self.nameList()

    def nameList(self):
        return [drum.name for drum in self.drums]

    def removeFirstDrumOfName(self, name):
        if self.nameExists(name):
            firstFound = [drum for drum in self.drums if drum.name == name][0]
            self.drums.remove(firstFound)
            self.layoutChanged.emit()


class DrumEncoder(json.JSONEncoder):

    # pylint: disable=method-hidden
    def default(self, obj):
        if isinstance(obj, Drum):
            return {
                '__drumatizeDrum__': hash(obj),
                'name': obj.name,
                'type': obj.type,
                'iLike': obj.iLike,
                'layers': json.dumps(obj.layers, cls = LayerEncoder),
                'amplEnvs': json.dumps(obj.amplEnvs, cls = EnvelopeEncoder),
                'freqEnvs': json.dumps(obj.freqEnvs, cls = EnvelopeEncoder),
                'distEnvs': json.dumps(obj.distEnvs, cls = EnvelopeEncoder),
            }
        else:
            return super().default(obj)

    @classmethod
    def decode(self, dict):
        if '__drumatizeDrum__' in dict:
            drum = Drum(name = dict['name'], type = dict['type'])
            drum.iLike = dict['iLike']
            drum.amplEnvs = json.loads(dict['amplEnvs'], object_hook = EnvelopeEncoder.decode)
            drum.freqEnvs = json.loads(dict['freqEnvs'], object_hook = EnvelopeEncoder.decode)
            drum.distEnvs = json.loads(dict['distEnvs'], object_hook = EnvelopeEncoder.decode)
            drum.layers = json.loads(dict['layers'], object_hook=LayerEncoder.decode)
            return drum
        return dict