from PyQt5.QtCore import QAbstractListModel


class DrumatizerModel(QAbstractListModel):

    def __init__(self, *args, content = None, **kwargs):
        super(DrumatizerModel, self).__init__(*args, **kwargs)
        self.content = content or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            status, text = self.content[index.row()]
            return text

    def rowCount(self, index):
        return len(self.content)