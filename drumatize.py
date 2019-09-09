from DrumModel import *
from LayerModel import *
from EnvelopeModel import *

from scipy.optimize import curve_fit


GLfloat = lambda f: str(int(f)) + '.' if f==int(f) else str(f)[0 if f>=1 or f<0 or abs(f)<1e-4 else 1:].replace('-0.','-.')

def GLstr(s):
    try:
        f = float(s)
    except ValueError:
        return s
    else:
        return GLfloat(f)

class Drumatize:

    def __init__(self, layers):
        self.layers = layers

    def drumatize(self):

        groupedResults = {}

        amplEnvSet = set(layer.amplEnv for layer in self.layers)
        glslAmplEnvs = {}
        for amplEnv in amplEnvSet:
            glslAmplEnv = self.linearEnvelope(amplEnv)
            glslAmplEnvs[amplEnv] = glslAmplEnv
            groupedResults[amplEnv] = []

        for layer in self.layers:

            freqEnv = layer.freqEnv
            freqPointNumber = freqEnv.pointNumber()

            if freqPointNumber == 1:
                glslFreq = GLfloat(freqEnv.points[0].value)
            elif freqPointNumber == 2:
                args = (freqEnv.points[1].time, freqEnv.points[0].value, freqEnv.points[1].value)
                glslFreq = 'drop_phase(_PROGTIME,{},{},{})'.format(*(GLfloat(arg) for arg in args))
            elif freqPointNumber == 3:
                args = (freqEnv.points[1].time, freqEnv.points[2].time, freqEnv.points[0].value, freqEnv.points[1].value, freqEnv.points[2].value)
                glslFreq = 'drop2_phase(_PROGTIME,{},{},{},{},{})'.format(*(GLfloat(arg) for arg in args))
            else:
                print('frequency envelope {} is invalid. Exiting...'.format(freqEnv.name))
                raise ValueError

            glslPhase = '0'
            # glslDistEnv = self.layer.distEnv

            glslVolume = GLfloat(layer.volume * layer.unitVolume)

            layerResult = '{}*{}'.format(glslVolume, self.freqFunction(layer.type, glslFreq, glslPhase))
            groupedResults[layer.amplEnv].append(layerResult)

        groupResults = []
        for amplEnv in amplEnvSet:
            groupResults.append('{}*({})'.format(glslAmplEnvs[amplEnv], '+'.join(groupedResults[amplEnv])))

        return '+'.join(groupResults)

        # freqFunction = self.freqFunction(self.layer.type, freq, 0)
        # TODO: add option to add another envelope as phase.. heheh... hehehehe... --> nice reverb emulation and FM

    def freqFunction(self, indicator, freq, phase):
        phaseAdd = '' if phase == '0' else ('+' + phase)
        phaseArgs = '({}*_PROGTIME{})'.format(freq, phaseAdd)

        if indicator == 'SIN':
            if phase == '0':
                return '_sin({})'.format(freq)
            else:
                return '_sin_({},{})'.format(freq, phase)

        elif indicator == 'SAW':
            return '_saw' + phaseArgs

        elif indicator == 'SQU':
            return '_sq' + phaseArgs

        elif indicator == 'TRI':
            return '_tri' + phaseArgs

        elif indicator == 'WHTNS':
            return 'pseudorandom' + phaseArgs

        elif indicator == 'PRLNS':
            return 'lpnoise' + phaseArgs

        else:
            print('freqFunction({},{},{}) is not defined. Exiting...'.format(indicator,freq,phase))
            raise ValueError


    def linearEnvelope(self, env):
        if not env.points:
            return '0'

        term = ''
        for point, next in zip(env.points, env.points[1:]):
            term += '_ENVTIME <= {}? linmix(_ENVTIME,{},{},{},{}):'.format(GLfloat(point.time), *self.fractCoefficients(point.time, next.time), GLfloat(point.value), GLfloat(next.value))

        term += GLfloat(env.points[-1].value)
        return '(' + term + ')'

    def fractCoefficients(self, x0, x1):
        return GLfloat(round(1/(x1-x0), 4)), GLfloat(round(-x0/(x1-x0), 4))

    def expDecayFit(self, env):
        pass