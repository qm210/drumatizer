from PyQt5.QtCore import QAbstractListModel, Qt


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

    def __repr__(self):
        return self.name # '{} -- {}'.format(self.type.upper(), self.name)

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
            return self.drums[index.row()].__repr__()

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