from PyQt5.QtCore import QAbstractListModel, Qt
from copy import deepcopy
from math import pi
from random import uniform
import json


class Envelope:

    def __init__(self, name = None, type = None, points = None, parameters = None, _hash = None):
        self.name = name or 'Matzes Liebling'
        self.type = type
        self.points = points or []
        self.parameters = parameters or {} # TODO: include 'Try Exp. Fit' (with scipy.optimize) here
        self._hash = _hash or hash(self)

    def __str__(self):
        return self.name

    def adjust(self, name = None, points = None, parameters = None, pointNumber = None, singlePointValue = None):
        if name is not None:
            self.name = name
        if points is not None:
            self.points = points
        else:
            oldNumber = len(self.points)
            if pointNumber is not None:
                if pointNumber == 1:
                    self.points = [EnvelopePoint(time = 0, value = singlePointValue or 0)]
                else:
                    if pointNumber < oldNumber:
                        if pointNumber == 2 and self.type == 'amplitude':
                            self.points = self.points[0:2]
                        else:
                            self.points = self.points[0:pointNumber-1] + [self.points[-1]]
                    elif pointNumber > oldNumber:
                        if oldNumber == 2 and self.type == 'amplitude':
                            self.points.append(EnvelopePoint(time = pi/4, value = 0))
                            oldNumber += 1
                        elif oldNumber == 1:
                            self.points.append(EnvelopePoint(time = pi/4, value = self.points[0].value))
                            oldNumber += 1
                        # my super-awesome golden ratio algorithm C=
                        for _ in range(pointNumber - oldNumber):
                            goldenTime = .382 * self.points[-2].time + .618 * self.points[-1].time
                            goldenValue = .382 * self.points[-2].value + .618 * self.points[-1].value
                            self.points.insert(-1, EnvelopePoint(time = goldenTime, value = goldenValue))

        if parameters is not None:
            self.parameters = parameters

    def adjustParameter(self, parName, parValue):
        self.parameters.update({parName: parValue})

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

    def __init__(self, time = 0, value = 0, fixedTime = False, fixedValue = False, name = None, decodePoint = None):
        self.time = time
        self.value = value
        self.fixedTime = fixedTime or (time < 1e-3)
        self.fixedValue = fixedValue
        self.name = name
        if decodePoint is not None:
            try:
                self.time = decodePoint['time']
                self.value = decodePoint['value']
                self.fixedTime = decodePoint['fixedTime']
                self.fixedvalue = decodePoint['fixedValue']
                self.name = decodePoint['name']
            except:
                print("EnvelopePoint(decodePoint = ...) was passed something incompatible..!")
                raise

    def dragTo(self, time = None, value = None):
        if time is not None and not self.fixedTime:
            self.time = time
        if value is not None and not self.fixedValue:
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
            return self.envelopes[index.row()].__str__()

    def rowCount(self, index = None):
        return len(self.envelopes)

    def indexOf(self, envelope):
        try:
            numericalIndex = self.envelopes.index(envelope)
            modelIndex = self.createIndex(numericalIndex, 0)
            if modelIndex.isValid():
                return modelIndex
        except ValueError:
            return None

    def emitAllChanged(self):
        self.dataChanged.emit(self.createIndex(0,0), self.createIndex(self.rowCount(),0))

    def clear(self):
        self.envelopes = []
        self.emitAllChanged()

    def clearAndRefill(self, envelopes):
        self.envelopes = [deepcopy(env) for env in envelopes]
        self.emitAllChanged()

    def insertNew(self, envelope, position = None):
        newEnvelope = deepcopy(envelope)
        if position is not None:
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

    def lastEnvelope(self):
        if self.envelopes:
            return self.envelopes[-1]
        else:
            return None

    def adjust(self, numericalIndex, name = None, points = None, parameters = None, pointNumber = None):
        if self.envelopes:
            self.envelopes[numericalIndex].adjust(name, points, pointNumber, parameters)

    def adjustNewest(self, **args):
        self.adjust(self.newestIndex, **args)

    def nameExists(self, name):
        return name in self.nameList()

    def nameList(self):
        return [envelope.name for envelope in self.envelopes]


defaultAmplEnvelope = Envelope(
    name = '(default)',
    type = 'amplitude',
    points = [
        EnvelopePoint(0.00, 0.0, fixedTime = True, fixedValue = True),
        EnvelopePoint(0.05, 1.0, name = 'attack', fixedValue = True),
        EnvelopePoint(0.50, 0.5, name = 'decay'),
        EnvelopePoint(1.2, 0.0, name = 'sustain')
    ],
    parameters = {'tryExpFit': False})

defaultFreqEnvelope = Envelope(
    name = '(default)',
    type = 'frequency',
    points = [
        EnvelopePoint(0.00, 6000, name = 'freq0', fixedTime = True),
        EnvelopePoint(0.15, 1000, name = 'freq1'),
        EnvelopePoint(0.40,  200, name = 'freq2')
    ],
    parameters = {'usePolynomial': False})

defaultDistEnvelope = Envelope(
    name = '(default)',
    type = 'distortion',
    points = [
        EnvelopePoint(0.00, 1.0, name = 'distAmt0', fixedTime = True),
        EnvelopePoint(0.20, 1.15, name = 'distAmt1'),
        EnvelopePoint(0.80, 0.5, name = 'distAmt2'),
        EnvelopePoint(1.20, 0.2, name = 'distAmt3')
    ])


class EnvelopeEncoder(json.JSONEncoder):

    # pylint: disable=method-hidden
    def default(self, obj):
        if isinstance(obj, Envelope):
            return {
                '__drumatizeEnvelope__': obj._hash,
                'name': obj.name,
                'type': obj.type,
                'points': json.dumps(obj.points, default = (lambda point: point.__dict__)),
                'parameters': obj.parameters
            }
        else:
            return super().default(obj)

    @classmethod
    def decode(self, dict):
        if '__drumatizeEnvelope__' in dict:
            points = [EnvelopePoint(decodePoint = p) for p in json.loads(dict['points'])]
            parameters = self.ensureParameterCompatibility(dict['parameters'], dict['type'])
            return Envelope(
                name = dict['name'],
                type = dict['type'],
                points = points,
                parameters = parameters,
                _hash = dict['__drumatizeEnvelope__'],
            )
        else:
            return dict

    @classmethod
    def decodeList(self, list):
        print('decodeList', list)
        return [self.decode(env) for env in list if '__drumatizeEnvelope__' in env]

    @classmethod
    def ensureParameterCompatibility(self, parameters, type):
        if type == 'amplitude':
            for defaultPar in defaultAmplEnvelope.parameters:
                if defaultPar not in parameters:
                    parameters.update({defaultPar: defaultAmplEnvelope.parameters[defaultPar]})
        if type == 'frequency':
            for defaultPar in defaultFreqEnvelope.parameters:
                if defaultPar not in parameters:
                    parameters.update({defaultPar: defaultFreqEnvelope.parameters[defaultPar]})
        if type == 'distortion':
            for defaultPar in defaultDistEnvelope.parameters:
                if defaultPar not in parameters:
                    parameters.update({defaultPar: defaultDistEnvelope.parameters[defaultPar]})
        return parameters