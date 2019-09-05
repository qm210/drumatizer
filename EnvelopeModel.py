from PyQt5.QtCore import QAbstractListModel, Qt
from copy import deepcopy
from math import pi
from random import uniform


class Envelope:

    def __init__(self, name = None, type = None, points = None, parameters = None):
        self.name = name or 'Matzes Liebling'
        self.type = type
        self.points = points or []
        self.parameters = parameters or {} # TODO: include 'Try Exp. Fit' (with scipy.optimize) here

    def __repr__(self):
        return self.name

    def adjust(self, name = None, points = None, pointNumber = None, parameters = None):
        if name is not None:
            self.name = name
        if points is not None:
            self.points = points
        else:
            oldNumber = len(self.points)
            print(pointNumber, oldNumber, "ey")
            if pointNumber is not None and pointNumber > 1:
                if pointNumber < oldNumber:
                    self.points = self.points[0:pointNumber-1] + [self.points[-1]]
                elif pointNumber > oldNumber:
                    if oldNumber == 1:
                        self.points.append(EnvelopePoint(time = pi/2, value = self.points[0].value))
                        oldNumber += 1
                    # my super-awesome golden ratio algorithm C=
                    for p in range(pointNumber - oldNumber):
                        goldenTime = .382 * self.points[-2].time + .618 * self.points[-1].time
                        goldenValue = .382 * self.points[-2].value + .618 * self.points[-1].value
                        print(p, goldenTime, goldenValue)
                        self.points.insert(-1, EnvelopePoint(time = goldenTime, value = goldenValue))

        if parameters is not None:
            self.parameters = parameters


    def setPoints(self, points):
        self.points = points

    def addPoint(self, point):
        self.points.append(point)

    def pointNumber(self):
        return len(self.points)

    def randomize(self, maxTime, minValue, maxValue, minTime = 0):
        for p, point in enumerate(self.points):
            if not point.fixedTime and p > 0:
                point.time = round(uniform(self.points[p-1].time, self.points[p+1].time if p < len(self.points)-1 else maxTime), 2)
            if not point.fixedValue:
                point.value = round(uniform(minValue, maxValue), 2)

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
        self.newestIndex = len(self.envelopes) - 1

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.envelopes[index.row()].name

    def rowCount(self, index):
        return len(self.envelopes)

    def indexOf(self, envelope):
        try:
            numericalIndex = self.envelopes.index(envelope)
            modelIndex = self.createIndex(numericalIndex, 0)
            if modelIndex.isValid():
                return modelIndex
        except ValueError:
            return None

    def insertNew(self, envelope, position = None):
        newEnvelope = deepcopy(envelope)
        if position:
            self.envelopes.insert(position, newEnvelope)
            self.newestIndex = position
        else:
            self.envelopes.append(newEnvelope)
            self.newestIndex = len(self.envelopes) - 1

    def newestEnvelope(self):
        try:
            return self.envelopes[self.newestIndex]
        except:
            return None

    def adjust(self, numericalIndex, name = None, points = None, parameters = None, pointNumber = None):
        if self.envelopes:
            self.envelopes[numericalIndex].adjust(name, points, pointNumber, parameters)

    def adjustNewest(self, **args):
        self.adjust(self.newestIndex, **args)


defaultAmpEnvelope = Envelope(
    name = '(default)',
    type = 'amplitude',
    points = [
        EnvelopePoint(0.00, 0.0, fixedTime = True, fixedValue = True),
        EnvelopePoint(0.05, 1.0, name = 'attack', fixedValue = True),
        EnvelopePoint(0.50, 0.5, name = 'decay'),
        EnvelopePoint(1.50, 0.0, name = 'sustain')
    ])

defaultFreqEnvelope = Envelope(
    name = '(default)',
    type = 'frequency',
    points = [
        EnvelopePoint(0.00, 6000, name = 'freq0', fixedTime = True),
        EnvelopePoint(0.15, 1000, name = 'freq1'),
        EnvelopePoint(0.40,  200, name = 'freq2')
    ])

defaultDistEnvelope = Envelope(
    name = '(default)',
    type = 'distortion',
    points = [
        EnvelopePoint(0.00, 1.0, name = 'distAmt0', fixedTime = True),
        EnvelopePoint(0.20, 1.5, name = 'distAmt1'),
        EnvelopePoint(0.80, 0.5, name = 'distAmt2'),
        EnvelopePoint(1.50, 0.2, name = 'distAmt3')
    ])
