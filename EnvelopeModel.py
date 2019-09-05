from PyQt5.QtCore import QAbstractListModel, Qt
from copy import deepcopy


class Envelope:


    def __init__(self, name = None, points = None, parameters = None):
        self.name = name or 'Matzes Liebling'
        self.points = points or []
        self.parameters = parameters or {} #TODO: include 'Try Exp. Fit' (with scipy.optimize) here

    def __repr__(self):
        return self.name

    def adjust(self, name = None, points = None, parameters = None, pointNumber = None):
        if name is not None:
            self.name = name

        if points is not None:
            self.points = points
        else:
            if pointNumber is not None and pointNumber > 0:
                if pointNumber < len(self.points):
                    pass
                elif pointNumber > len(self.points):
                    pass

        if parameters is not None:
            self.parameters = parameters

    def setPoints(self, points):
        self.points = points

    def addPoint(self, point):
        self.points.append(point)

    def randomize(self):
        print("U DO NO SUCH THING! (for now)")

# TODO: at '...', choose which parameters may be randomized


class EnvelopePoint:

    def __init__(self, time = 0, value = 0, fixedTime = False, fixedValue = False, name = None):
        self.time = time
        self.value = value
        self.fixedTime = fixedTime or (time < 1e-3)
        self.fixedValue = fixedValue
        self.name = name

    def dragTo(self, time = None, value = None):
        if time and not self.fixedTime:
            self.time = time
        if value and not self.fixedValue:
            self.value = value

    def values(self):
        return self.time, self.value

    def __repr__(self):
        return str(self.name) + '(' + ('FIX ' if self.fixedTime else '') + str(self.time) + ', ' + ('FIX ' if self.fixedValue else '') + str(self.value) + ')'


class EnvelopeModel(QAbstractListModel):

    def __init__(self, *args, envelopes = None, **kwargs):
        super(EnvelopeModel, self).__init__(*args, **kwargs)
        self.envelopes = envelopes or []
        self.lastInserted = len(self.envelopes) - 1

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.envelopes[index.row()].name

    def rowCount(self, index):
        return len(self.envelopes)

    def insertNew(self, envelope, position = None):
        newEnvelope = deepcopy(envelope)
        if position:
            self.envelopes.insert(position, newEnvelope)
            self.lastInserted = position
        else:
            self.envelopes.append(newEnvelope)
            self.lastInserted = len(self.envelopes) - 1

    def lastInsertedEnvelope(self):
        try:
            return self.envelopes[self.lastInserted]
        except:
            return None


defaultAmpEnvelope = Envelope(
    name = '(default)',
    points = [
        EnvelopePoint(0.00, 0.0, fixedTime = True, fixedValue = True),
        EnvelopePoint(0.05, 1.0, name = 'attack', fixedValue = True),
        EnvelopePoint(0.50, 0.5, name = 'decay'),
        EnvelopePoint(1.50, 0.0, name = 'sustain')
    ])

defaultFreqEnvelope = Envelope(
    name = '(default)',
    points = [
        EnvelopePoint(0.00, 6000, name = 'freq0', fixedTime = True),
        EnvelopePoint(0.15, 1000, name = 'freq1'),
        EnvelopePoint(0.40,  200, name = 'freq2')
    ])

defaultDistEnvelope = Envelope(
    name = '(default)',
    points = [
        EnvelopePoint(0.00, 1.0, name = 'distAmt0', fixedTime = True),
        EnvelopePoint(0.20, 1.5, name = 'distAmt1'),
        EnvelopePoint(0.80, 0.5, name = 'distAmt2'),
        EnvelopePoint(1.50, 0.2, name = 'distAmt3')
    ])
