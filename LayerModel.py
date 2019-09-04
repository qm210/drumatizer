from PyQt5.QtCore import QAbstractListModel, Qt

layerTypes = ['Sine Oscillator', 'Saw Oscillator', 'Square Oscillator', 'Triangle Osciallator', 'White Pseudonoise', 'Perlin Noise']
distTypes = ['Overdrive', 'Waveshape', 'FM', 'Lo-Fi']

class LayerModelItem:

    def __init__(self):
        self.name = 'QMs Liebling-slayer'
        self.type = layerTypes[0]
        self.ampEnvelope = None # if these are none, create one upon creation
        self.freqEnvelope = None
        self.distEnvelope = None
        self.distType = None
        self.distParam = None
        self.volume = 1
        self.mute = False
        # each layer holds an envelope of each kind

    def __repr__(self):
        if self.mute:
            return 'MUTE {} ({})'.format(self.name, self.type)
        else:
            return '{}% {} ({})'.format(100*self.volume, self.name, self.type)


class LayerModel(QAbstractListModel):

    def __init__(self, *args, items = None, **kwargs):
        super(LayerModel, self).__init__(*args, **kwargs)
        self.items = items or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.items[index.row()].name

    def rowCount(self, index):
        return len(self.items)