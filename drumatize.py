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

            glslPhase = GLfloat(0)
            # glslDistEnv = self.layer.distEnv
            glslVolume = GLfloat(layer.volume * layer.unitVolume)
            glslDetuneFactor = GLfloat(1. - layer.detune * layer.unitDetune)

            layerResult = f'{glslVolume}*{self.freqFunction(layer.type, glslFreq, glslPhase, glslDetuneFactor)}'
            groupedResults[layer.amplEnv].append(layerResult)

        groupResults = []
        for amplEnv in amplEnvSet:
            groupResults.append('{}*({})'.format(glslAmplEnvs[amplEnv], '+'.join(groupedResults[amplEnv])))

        result = '+'.join(groupResults)

        stereodelay = GLfloat(layer.stereodelay * layer.unitStereoDelay)
        print("STEREODELAY IS", stereodelay)

        _PROGTIME_R = f'(_t-{stereodelay})' if layer.stereodelay != 0 else '_t'
        resultL = result.replace('_ENVTIME', '_t').replace('_PROGTIME', '_t')
        resultR = result.replace('_ENVTIME', '_t').replace('_PROGTIME', _PROGTIME_R)

        return resultL, resultR

        # freqFunction = self.freqFunction(self.layer.type, freq, 0)
        # TODO: add option to add another envelope as phase.. heheh... hehehehe... --> nice reverb emulation and FM

    def freqFunction(self, indicator, freq, phase, detuneFactor):
        noPhase = (phase == GLfloat(0))
        noDetune = (detuneFactor == GLfloat(1))

        if indicator == 'SIN':
            if noPhase:
                phaseArgs = f'{freq}*_PROGTIME'
                func = '_sin'
            else:
                phaseArgs = f'{freq}*_PROGTIME,{phase}'
                func = '_sin_'

            if noDetune:
                return f'_sin({phaseArgs})'
            else:
                return f'(.5*_sin({phaseArgs})+.5*_sin({detuneFactor}*{phaseArgs}))'

        elif indicator == 'PRLNS':
            if noDetune:
                return f'lpnoise(_PROGTIME,{freq})'
            else:
                return f'(.5*lpnoise(_PROGTIME,{freq})+.5*lpnoise(_PROGTIME,{detuneFactor}*{freq}))'

        else:
            phaseArgs = f'{freq}*_PROGTIME' + ('' if noPhase else f'+{phase}')

            if indicator == 'SAW':
                func = '_saw'
            elif indicator == 'SQU':
                func = '_sq'
            elif indicator == 'TRI':
                func = '_tri'
            elif indicator == 'WHTNS':
                func = 'pseudorandom'
            else:
                print(f'freqFunction({indicator},...) is not defined. Exiting...')
                raise ValueError

            if noDetune:
                return f'{func}({phaseArgs})'
            else:
                return f'(.5*{func}({phaseArgs})+.5*{func}({detuneFactor}*{phaseArgs}))'


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