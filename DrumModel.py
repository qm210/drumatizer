from PyQt5.QtCore import QAbstractListModel, Qt

class DrumModelItem:

    def __init__(self):
        self.name = 'Matzes Liebling'
        # idea: preset list will be grouped by type
        self.type = 'Snare'
        self.iLike = 0
        # each drum holds an arbitrary amount of layers and envelopes of each kind
        self.layers = []
        self.ampEnvelopes = []
        self.freqEnvelopes = []
        self.distEnvelopes = []
        # '...' menu: enter name, type, option to purge unused envelopes, also the 'drum awesomeness', for the ranking ;)

    def __repr__(self):
        return '{} -- {}'.format(self.type.upper(), self.name)


class DrumModel(QAbstractListModel):

    def __init__(self, *args, items = None, **kwargs):
        super(DrumModel, self).__init__(*args, **kwargs)
        self.items = items or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.items[index.row()].name

    def rowCount(self, index):
        return len(self.items)