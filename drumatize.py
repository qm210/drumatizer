from DrumModel import *
from LayerModel import *
from EnvelopeModel import *

import numpy as np
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
        self.separateFunctionCount = 0
        self.separateFunctionCode = ''

    def drumatize(self):

        groupedResultsWithoutAmplEnv_L = {}
        groupedResultsWithoutAmplEnv_R = {}

        amplEnvSet = set(layer.amplEnv for layer in self.layers)
        glslAmplEnvs = {}
        for amplEnv in amplEnvSet:
            if 'tryExpFit' in amplEnv.parameters and amplEnv.parameters['tryExpFit']:
                glslAmplEnvs[amplEnv] = self.expDecayFit(amplEnv)
            else:
                glslAmplEnvs[amplEnv] = self.linearEnvelope(amplEnv)

            groupedResultsWithoutAmplEnv_L[amplEnv] = []
            groupedResultsWithoutAmplEnv_R[amplEnv] = []

        layerCleanDict = {}
        for layer in self.layers:
            freqEnv = layer.freqEnv
            freqPointNumber = freqEnv.pointNumber()

            if freqPointNumber == 1:
                glslPhase = '{}*_PROGTIME'.format(GLfloat(freqEnv.points[0].value))
            elif freqPointNumber == 2:
                args = (freqEnv.points[1].time, freqEnv.points[0].value, freqEnv.points[1].value)
                glslPhase = 'drop_phase(_PROGTIME,{},{},{})'.format(*(GLfloat(arg) for arg in args))
            elif freqPointNumber == 3:
                args = (freqEnv.points[1].time, freqEnv.points[2].time, freqEnv.points[0].value, freqEnv.points[1].value, freqEnv.points[2].value)
                glslPhase = 'drop2_phase(_PROGTIME,{},{},{},{},{})'.format(*(GLfloat(arg) for arg in args))
                #glslPhase = self.phaseThirdOrder(freqEnv.points)
                print(glslPhase)
            else:
                print('frequency envelope {} is invalid. Exiting...'.format(freqEnv.name))
                raise ValueError

            glslPhaseMod = GLfloat(0)
            #glslDetuneFactor = GLfloat(1. - layer.detune * layer.unitDetune)
            glslDetuneFactor = GLfloat(1)
            layerClean = self.oscFunction(layer.type, glslPhase, glslPhaseMod, glslDetuneFactor, GLfloat(freqEnv.points[0].value))
            layerCleanDict.update({layer._hash: layerClean})

        for layer in self.layers:
            if layer.mute:
                continue

            if not layer.phasemodOff:
                print(layerCleanDict, '\n')
                glslPhaseMod = f'{GLfloat(layer.phasemodAmt)}*{glslAmplEnvs[layer.amplEnv]}*{layerCleanDict[layer.phasemodSrcHash]}'
                glslDetuneFactor = GLfloat(1. - layer.detune * layer.unitDetune)
                layerResult = self.oscFunction(layer.type, glslPhase, glslPhaseMod, glslDetuneFactor, GLfloat(layer.freqEnv.points[0].value))
                print("HELP", layer.phasemodAmt, glslAmplEnvs[layer.amplEnv], '\n', glslPhaseMod, '\n', layerCleanDict[layer._hash], '\n', layerResult)
            else:
                layerResult = layerCleanDict[layer._hash]

            if not layer.distOff:
                glslDistEnv = self.linearEnvelope(layer.distEnv)
                layerResult = self.applyDistortion(layerResult, layer.distType, layer.distParam, glslDistEnv)

            stereodelay = GLfloat(round(layer.stereodelay * layer.unitStereoDelay, 5))
            _PROGTIME_R = f'(_t-{stereodelay})' if layer.stereodelay != 0 else '_t'
            layerResult_L = layerResult.replace('_PROGTIME', '_t')
            layerResult_R = layerResult.replace('_PROGTIME', _PROGTIME_R)

            glslVolume = GLfloat(layer.volume * layer.unitVolume)
            groupedResultsWithoutAmplEnv_L[layer.amplEnv].append(f'{glslVolume}*{layerResult_L}')
            groupedResultsWithoutAmplEnv_R[layer.amplEnv].append(f'{glslVolume}*{layerResult_R}')

        groupResults_L = []
        groupResults_R = []
        for amplEnv in amplEnvSet:
            grouped_L = groupedResultsWithoutAmplEnv_L[layer.amplEnv]
            grouped_R = groupedResultsWithoutAmplEnv_R[layer.amplEnv]
            groupResults_L.append('{}*({})'.format(glslAmplEnvs[amplEnv], '+'.join(grouped_L)) if grouped_L else '0.')
            groupResults_R.append('{}*({})'.format(glslAmplEnvs[amplEnv], '+'.join(grouped_R)) if grouped_R else '0.')

        resultL = '+'.join(groupResults_L).replace('_ENVTIME', '_t')
        resultR = '+'.join(groupResults_R).replace('_ENVTIME', '_t')
        envFuncCode = self.separateFunctionCode.replace('_ENVTIME', 't')

        return resultL, resultR, envFuncCode

    def oscFunction(self, indicator, phase, PhaseMod, detuneFactor, freqForNoise):
        noPhaseMod = (PhaseMod == GLfloat(0))
        noDetune = (detuneFactor == GLfloat(1))

        if indicator == 'SIN':
            if noPhaseMod:
                phaseArgs = phase
                func = '_sin'
            else:
                phaseArgs = f'{phase},{PhaseMod}'
                func = '_sin_'

            if noDetune:
                return f'{func}({phaseArgs})'
            else:
                return f'(.5*{func}({phaseArgs})+.5*{func}({detuneFactor}*{phaseArgs}))'

        elif indicator == 'PRLNS':
            # how could I implement a change in freqForNoise - TODO: think.
            if noDetune:
                return f'lpnoise(_PROGTIME,{freqForNoise})'
            else:
                return f'(.5*lpnoise(_PROGTIME,{freqForNoise})+.5*lpnoise(_PROGTIME,{detuneFactor}*{freqForNoise}))'

        else:
            if indicator == 'SAW':
                func = '_saw'
            elif indicator == 'SQU':
                func = '_sq'
            elif indicator == 'TRI':
                func = '_tri'
            elif indicator == 'WHTNS':
                func = 'pseudorandom'
                phase = f'{freqForNoise}*_PROGTIME'
            else:
                print(f'oscFunction({indicator},...) is not defined. Exiting...')
                raise ValueError

            phaseArgs = phase if noPhaseMod else f'{phase}+{PhaseMod}'

            if noDetune:
                return f'{func}({phaseArgs})'
            else:
                return f'(.5*{func}({phaseArgs})+.5*{func}({detuneFactor}*{phaseArgs}))'

    def applyDistortion(self, layerClean, distType, distParam, distEnv):
        if distType == 'Overdrive':
            return f'clamp({distEnv}*{layerClean},-1.,1.)'
        elif distType == 'Waveshape':
            return f'sinshape({layerClean}, {distEnv}, {GLfloat(distParam)})'
        elif distType == 'Lo-Fi':
            distEnv = f'({GLfloat(distParam)}*{distEnv})'
            return layerClean.replace('_PROGTIME',f'lofi(_PROGTIME,{distEnv})')
        elif distType == 'FM':
            print('FM (phase mod) is not implemented yet... should be treated differently, anyway!')
            return layerClean
        else:
            print(f'Distortion of type \'{distType}\' does not exist!')
            return layerClean

    def linearEnvelope(self, env):
        if len(env.points) == 0:
            return '0'
        elif len(env.points) == 1:
            return env.points[0].value

        separateFunction = f'env{self.separateFunctionCount}'
        self.separateFunctionCount += 1

        term = ''
        for point, next in zip(env.points, env.points[1:]):
            term += '_ENVTIME <= {}? linmix(_ENVTIME,{},{},{},{}):'.format(GLfloat(next.time), *self.linCoefficients(point.time, next.time), GLfloat(point.value), GLfloat(next.value))

        term += GLfloat(env.points[-1].value)

        self.separateFunctionCode += f'float {separateFunction}(float _ENVTIME){{return {term};}}\n'
        return separateFunction + '(_ENVTIME)'

    def linCoefficients(self, x0, x1):
        return GLfloat(round(1/(x1-x0), 4)), GLfloat(round(-x0/(x1-x0), 4))

    def expDecayFit(self, env):
        def expfunc(x, kappa):
            return np.exp(-kappa*x)

        attack = round(env.points[1].time, 4)
        t_data = np.array([p.time - attack for p in env.points[1:]])
        v_data = np.array([p.value for p in env.points[1:]])
        print("times:", t_data, "values:", v_data)

        try:
            opt, cov = curve_fit(expfunc, t_data, v_data)
            print(opt, cov)
            kappa = round(opt[0], 4)
        except RuntimeError as error:
            print("RuntimeError:", error.args[0])
            print("fit to exponential decay didn't work. use linear model...")
            return self.linearEnvelope(env)

        term = f'(_ENVTIME <= {attack}? smoothstep(0., {attack}, _ENVTIME): exp(-{kappa}*(_ENVTIME-{attack})) )'
        return term

    def phaseThirdOrder(self, freqPoints):
        # conditions: three points are given and tangent through last one is flat
        t1, t2 = freqPoints[1].time, freqPoints[2].time
        f0, f1, f2 = freqPoints[0].value, freqPoints[1].value, freqPoints[2].value
        A = np.array([[ t1*t1*t1, t1*t1, t1 ],
                      [ t2*t2*t2, t2*t2, t2 ],
                      [  3*t2*t2,  2*t2,  1 ]])
        b = np.array([f1-f0, f2-f0, 0])
        alpha, beta, gamma = np.linalg.solve(A, b)

        funcThirdOrder = f'({round(alpha/4, 3)}*_PROGTIME*_PROGTIME*_PROGTIME*_PROGTIME+{round(beta/3, 3)}*_PROGTIME*_PROGTIME*_PROGTIME+{round(gamma/2, 3)}*_PROGTIME*_PROGTIME+{f0}*_PROGTIME)'

        phaseAtPoint2 = GLfloat(round(alpha/4*t2*t2*t2*t2 + beta/3*t2*t2*t2 + gamma/2*t2*t2 + f0*t2, 3))
        freqAtPoint2 = GLfloat(freqPoints[2].value)
        timeAtPoint2 = GLfloat(freqPoints[2].time)
        phaseAfterPoint2 = f'{freqAtPoint2}*(_PROGTIME-{timeAtPoint2})+{phaseAtPoint2}'
        return f'(ENV_TIME <= {timeAtPoint2}? {funcThirdOrder}: {phaseAfterPoint2})'