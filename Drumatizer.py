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

class Drumatizer:

    def __init__(self, layers, amplEnvs, freqEnvs, distEnvs):
        self.layers = layers
        self.amplEnvs = amplEnvs
        self.freqEnvs = freqEnvs
        self.distEnvs = distEnvs

        self.separateFunctionCount = 0
        self.separateFunctionCode = ''

    def drumatize(self):

        groupedResultsWithoutAmplEnv_L = {}
        groupedResultsWithoutAmplEnv_R = {}

        glslAmplEnvs = {}
        for amplEnv in self.amplEnvs:
            if amplEnv._hash in glslAmplEnvs:
                continue

            tryExpFit = ('tryExpFit' in amplEnv.parameters and amplEnv.parameters['tryExpFit'])
            if tryExpFit:
                glslAmplEnvs[amplEnv._hash] = self.expDecayFit(amplEnv)
            else:
                glslAmplEnvs[amplEnv._hash] = self.linearEnvelope(amplEnv)

            groupedResultsWithoutAmplEnv_L[amplEnv._hash] = []
            groupedResultsWithoutAmplEnv_R[amplEnv._hash] = []

        layerCleanDict = {}
        glslPhase = {}
        glslFreqForNoise = {}
        glslDetuneFactor = {}
        for layer in self.layers:
            freqEnv = next(env for env in self.freqEnvs if env._hash == layer.freqEnvHash)
            freqPointNumber = freqEnv.pointNumber()
            glslFreqForNoise[layer._hash] = self.linearEnvelope(freqEnv)
            glslDetuneFactor[layer._hash] = GLfloat(round(1. - layer.detune * layer.unitDetune, 5))
            usePolynomial = ('usePolynomial' in freqEnv.parameters and freqEnv.parameters['usePolynomial'])

            if usePolynomial:
                glslPhase[layer._hash] = self.polynomialPhase(freqEnv.points)
            else:
                if freqPointNumber == 1:
                    glslPhase[layer._hash] = '{}*_PROGTIME'.format(GLfloat(freqEnv.points[0].value))
                elif freqPointNumber == 2:
                    args = (freqEnv.points[1].time, freqEnv.points[0].value, freqEnv.points[1].value)
                    glslPhase[layer._hash] = 'drop_phase(_PROGTIME,{},{},{})'.format(*(GLfloat(arg) for arg in args))
                elif freqPointNumber == 3:
                    args = (freqEnv.points[1].time, freqEnv.points[2].time, freqEnv.points[0].value, freqEnv.points[1].value, freqEnv.points[2].value)
                    glslPhase[layer._hash] = 'drop2_phase(_PROGTIME,{},{},{},{},{})'.format(*(GLfloat(arg) for arg in args))
                else:
                    print('frequency envelope {} is invalid. Exiting...'.format(freqEnv.name))
                    raise ValueError

            layerClean = self.oscFunction(layer.type, glslPhase[layer._hash], GLfloat(0), glslDetuneFactor[layer._hash], glslFreqForNoise[layer._hash])
            layerCleanDict.update({layer._hash: layerClean})

        for layer in self.layers:
            if layer.mute:
                continue

            if not layer.phasemodOff:
                glslPhaseMod = f'{GLfloat(layer.phasemodAmt)}*{glslAmplEnvs[layer.amplEnvHash]}*{layerCleanDict[layer.phasemodSrcHash]}'
                layerResult = self.oscFunction(layer.type, glslPhase[layer._hash], glslPhaseMod, glslDetuneFactor[layer._hash], glslFreqForNoise[layer._hash])
            else:
                layerResult = layerCleanDict[layer._hash]

            if not layer.distOff:
                distEnv = next(env for env in self.distEnvs if env._hash == layer.distEnvHash)
                glslDistEnv = self.linearEnvelope(distEnv)
                layerResult = self.applyDistortion(layerResult, layer.distType, layer.distParam, glslDistEnv)

            stereodelay = GLfloat(round(layer.stereodelay * layer.unitStereoDelay, 5))
            _PROGTIME_R = f'(_t-{stereodelay})' if layer.stereodelay != 0 else '_t'
            layerResult_L = layerResult.replace('_PROGTIME', '_t')
            layerResult_R = layerResult.replace('_PROGTIME', _PROGTIME_R)

            glslVolume = GLfloat(round(layer.volume * layer.unitVolume, 3))
            groupedResultsWithoutAmplEnv_L[layer.amplEnvHash].append(f'{glslVolume}*{layerResult_L}')
            groupedResultsWithoutAmplEnv_R[layer.amplEnvHash].append(f'{glslVolume}*{layerResult_R}')

        groupResults_L = []
        groupResults_R = []
        for amplEnvHash in glslAmplEnvs:
            grouped_L = groupedResultsWithoutAmplEnv_L[amplEnvHash]
            grouped_R = groupedResultsWithoutAmplEnv_R[amplEnvHash]
            groupResults_L.append('vel*{}*({})'.format(glslAmplEnvs[amplEnvHash], '+'.join(grouped_L)) if grouped_L else '0.')
            groupResults_R.append('vel*{}*({})'.format(glslAmplEnvs[amplEnvHash], '+'.join(grouped_R)) if grouped_R else '0.')

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
            return f'clip({distEnv}*{layerClean})'
        elif distType == 'Waveshape':
            return f'sinshape({layerClean}, {distEnv}, {GLfloat(distParam)})'
        elif distType == 'Lo-Fi':
            distEnv = f'({GLfloat(distParam)}*{distEnv})'
            return layerClean.replace('_PROGTIME',f'lofi(_PROGTIME,{distEnv})')
        elif distType == 'Saturation':
            return f's_atan({GLfloat(distParam)}*{distEnv}*{layerClean})'
        else:
            print(f'Distortion of type \'{distType}\' does not exist!')
            return layerClean

    def linearEnvelope(self, env):
        if len(env.points) == 0:
            return '0'
        elif len(env.points) == 1:
            return env.points[0].value

        separateFunction = f'__ENV{self.separateFunctionCount}'
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

    def polynomialPhase(self, freqPoints):
        numberPoints = len(freqPoints)
        if numberPoints == 1:
            return f'{freqPoints[0].value}*_PROGTIME'
        elif numberPoints == 2:
            t1 = freqPoints[1].time
            f0, f1 = freqPoints[0].value, freqPoints[1].value
            alpha = (f0-f1)/(t1*t1)
            beta = -2 * (f0-f1)/t1
            polyPhaseTerm = f'{round(alpha/3, 3)}*_PROGTIME*_PROGTIME*_PROGTIME+{round(beta/2, 3)}*_PROGTIME*_PROGTIME+{round(f0, 3)}*_PROGTIME'
            phaseAtLastPoint = GLfloat(round(alpha/3*t1*t1*t1 + beta/2*t1*t1 + f0*t1, 3))

        elif numberPoints == 3:
            # conditions: three points are given and tangent through last one is flat
            t1, t2 = freqPoints[1].time, freqPoints[2].time
            f0, f1, f2 = freqPoints[0].value, freqPoints[1].value, freqPoints[2].value
            A = np.array([[ t1*t1*t1, t1*t1, t1 ],
                        [ t2*t2*t2, t2*t2, t2 ],
                        [  3*t2*t2,  2*t2,  1 ]])
            b = np.array([f1-f0, f2-f0, 0])
            alpha, beta, gamma = np.linalg.solve(A, b)
            polyPhaseTerm = f'({round(alpha/4, 3)}*_PROGTIME*_PROGTIME*_PROGTIME*_PROGTIME+{round(beta/3, 3)}*_PROGTIME*_PROGTIME*_PROGTIME+{round(gamma/2, 3)}*_PROGTIME*_PROGTIME+{f0}*_PROGTIME)'
            phaseAtLastPoint = GLfloat(round(alpha/4*t2*t2*t2*t2 + beta/3*t2*t2*t2 + gamma/2*t2*t2 + f0*t2, 3))

        else:
            print("polynomialPhase() is not implemented for more than 3 points..! sorray!")
            raise ValueError

        freqAtLastPoint = GLfloat(freqPoints[-1].value)
        timeAtLastPoint = GLfloat(freqPoints[-1].time)
        phaseAfterLastPoint = f'{freqAtLastPoint}*(_PROGTIME-{timeAtLastPoint})+{phaseAtLastPoint}'
        return f'(_ENVTIME <= {timeAtLastPoint}? {polyPhaseTerm}: {phaseAfterLastPoint})'