from PyQt5.QtCore import QAbstractListModel, Qt

class EnvelopeModelItem:

    def __init__(self):
        self.name = 'Matzes Liebling'
        self.points = []
        self.parameters = {}

    def __repr__(self):
        return self.name

# TODO: at '...', choose which parameters may be randomized

class EnvelopeModel(QAbstractListModel):

    def __init__(self, *args, items = None, **kwargs):
        super(EnvelopeModel, self).__init__(*args, **kwargs)
        self.items = items or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.items[index.row()].name

    def rowCount(self, index):
        return len(self.items)