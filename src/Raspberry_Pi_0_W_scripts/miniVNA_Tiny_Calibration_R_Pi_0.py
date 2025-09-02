import platform
import serial
import matplotlib.pyplot as plt
import numpy as np
import time
import math
from enum import Enum
import copy
import json
from datetime import datetime
import socket

# Import javaobj-py3 which has better Python 3 support
try:
    import javaobj
except ImportError:
    print("Error: javaobj not installed. Please install with: pip install javaobj-py3")
    exit(1)

class VNACalibrationPoint:
    def __init__(self):
        self.delta_e = 0 + 0j
        self.e11 = 0 + 0j
        self.e00 = 0 + 0j
        self.loss = 0.0
        self.phase = 0.0
        self.rss1 = 0
        self.rss2 = 0
        self.rss3 = 0
        self.edf = None
        self.esf = None
        self.erf = None
        self.frequency = 0.0

    def to_dict(self):
        return {
            'delta_e': str(self.delta_e),
            'e11': str(self.e11),
            'e00': str(self.e00),
            'loss': self.loss,
            'phase': self.phase,
            'rss1': self.rss1,
            'rss2': self.rss2,
            'rss3': self.rss3,
            'edf': self.edf,
            'esf': self.esf,
            'erf': self.erf,
            'frequency': self.frequency
        }

    def set_delta_e(self, value):
        self.delta_e = value

    def get_delta_e(self):
        return self.delta_e

    def set_e11(self, value):
        self.e11 = value

    def get_e11(self):
        return self.e11

    def set_e00(self, value):
        self.e00 = value

    def get_e00(self):
        return self.e00

    def set_frequency(self, freq):
        self.frequency = freq

    def get_frequency(self):
        return self.frequency

    def __repr__(self):
        return f"VNACalibrationPoint(delta_e={self.delta_e}, e11={self.e11}, e00={self.e00}, frequency={self.frequency})"


class VNASampleBlock:
    def __init__(self):
        self._ANALYSER_TYPE_UNKNOWN = None
        self._config = None
        self._analyserType = 20
        self._deviceSupply = 6.0
        self._deviceTemperature = None
        self._numberOfSteps = None
        self._numberOfOverscans = 0
        self._samples = None
        self._scanMode = "Reflection"
        self._startFrequency = None
        self._stopFrequency = None
        self._calibrationPoints = None

    def to_dict(self):
        return {
            '_ANALYSER_TYPE_UNKNOWN': self._ANALYSER_TYPE_UNKNOWN,
            '_config': self._config,
            '_analyserType': self._analyserType,
            '_deviceSupply': self._deviceSupply,
            '_deviceTemperature': self._deviceTemperature,
            '_numberOfSteps': self._numberOfSteps,
            '_numberOfOverscans': self._numberOfOverscans,
            '_samples': self._samples,
            '_scanMode': self._scanMode,
            '_startFrequency': self._startFrequency,
            '_stopFrequency': self._stopFrequency,
            '_calibrationPoints': self._calibrationPoints
        }

    def setDeviceTemperature(self, deviceTemperature):
        self._deviceTemperature = deviceTemperature

    def getDeviceTemperature(self):
        return self._deviceTemperature

    def setDeviceSupply(self, deviceSupply):
        self._deviceSupply = deviceSupply

    def getDeviceSupply(self):
        return self._deviceSupply

    def setSamples(self, samples):
        self._samples = samples

    def getSamples(self):
        return self._samples
        # def getCalibrationBlock(self):
        #     return self._samples

    def getCalibrationPoints(self):
        return self._calibrationPoints

    def getCalibrationPoints(self):
        return self._calibrationPoints

    def setScanMode(self, scanMode):
        self._scanMode = scanMode

    def setNumberOfSteps(self, numberOfSteps):
        self._numberOfSteps = numberOfSteps

    def setStartFrequency(self, startFrequency):
        self._startFrequency = startFrequency

    def setStopFrequency(self, stopFrequency):
        self._stopFrequency = stopFrequency

    def setAnalyserType(self, analyserType):
        self._analyserType = analyserType


class VNABaseSample:
    def __init__(self, obj_copy=None):
        # if obj_copy is not None:
        if isinstance(obj_copy, set):
            obj_copy_list = list(obj_copy)
            obj_copy_list[0].angle
            # Copy constructor: copy attributes from another VNABaseSample
            self.angle = obj_copy_list[0].angle
            self.loss = obj_copy_list[0].loss
            self.frequency = obj_copy_list[0].frequency
            self.rss1 = obj_copy_list[0].rss1
            self.rss2 = obj_copy_list[0].rss2
            self.rss3 = obj_copy_list[0].rss3
            self.hasPData = obj_copy_list[0].hasPData
            self.p1 = obj_copy_list[0].p1
            self.p2 = obj_copy_list[0].p2
            self.p3 = obj_copy_list[0].p3
            self.p4 = obj_copy_list[0].p4
            self.p1Ref = obj_copy_list[0].p1Ref
            self.p2Ref = obj_copy_list[0].p2Ref
            self.p3Ref = obj_copy_list[0].p3Ref
            self.p4Ref = obj_copy_list[0].p4Ref
        elif isinstance(obj_copy, dict):
            # Copy constructor: copy attributes from another VNABaseSample
            self.angle = obj_copy['angle']
            self.loss = obj_copy['loss']
            self.frequency = obj_copy['frequency']
            self.rss1 = obj_copy['rss1']
            self.rss2 = obj_copy['rss2']
            self.rss3 = obj_copy['rss3']
            self.hasPData = False
            self.p1 = obj_copy['p1']
            self.p2 = obj_copy['p2']
            self.p3 = obj_copy['p3']
            self.p4 = obj_copy['p4']
            self.p1Ref = obj_copy['p1Ref']
            self.p2Ref = obj_copy['p2Ref']
            self.p3Ref = obj_copy['p3Ref']
            self.p4Ref = obj_copy['p4Ref']
        else:
            self.angle = 0.0
            self.loss = 0.0
            self.frequency = 0
            self.rss1 = 0
            self.rss2 = 0
            self.rss3 = 0
            self.hasPData = False
            self.p1 = 0
            self.p2 = 0
            self.p3 = 0
            self.p4 = 0
            self.p1Ref = 0
            self.p2Ref = 0
            self.p3Ref = 0
            self.p4Ref = 0
            self._RHO = None
            self._mag = None
            self._reflection_loss = None
            self._reflection_phase = None
            self._SWR = None
            self._R = None
            self._X = None
            self._Z = None

    def getLoss(self):  # This is the real part not the loss
        return self.loss

    def setLoss(self, value):
        self.loss = value

    def getAngle(self):  # This is the imaginary part not the angle
        return self.angle

    def setAngle(self, value):
        self.angle = value

    def get_frequency(self):
        return self.frequency

    def set_frequency(self, value):
        self.frequency = value

    def set_rho(self, RHO):
        self._RHO = RHO

    def set_mag(self, mag):
        self._mag = mag

    def set_reflection_loss(self, reflection_loss):
        self._reflection_loss = reflection_loss

    def set_reflection_phase(self, reflection_phase):
        self._reflection_phase = reflection_phase

    def set_SWR(self, SWR):
        self._SWR = SWR

    def set_R(self, R):
        self._R = R

    def set_X(self, X):
        self._X = X

    def set_Z(self, Z):
        self._Z = Z

    def __repr__(self):
        return f"VNABaseSample(loss={self.loss}, angle={self.angle})"

    def as_complex(self):
        # Assuming loss is magnitude, angle is degrees
        magnitude = self.getLoss()
        # angle_rad = math.radians(self.getAngle())
        angle_rad = self.getAngle()
        # return complex(magnitude * math.cos(angle_rad), magnitude * math.sin(angle_rad))
        return complex(self.getLoss(), self.getAngle())


class VNACalibrationContextTiny:
    def __init__(self):
        self._dib = VNADeviceInfoBlock()

    def to_dict(self):
        return {
            '_dib': self._dib
        }

    def set_conversion_temperature(self, conversion_temperature):
        self._conversion_temperature = conversion_temperature

    def get_conversion_temperature(self):
        return self._conversion_temperature

    def set_dib(self, dib):
        self._dib = dib

    def get_dib(self):
        return self._dib

    def set_calibration_block(self, cal_block):
        self._calibration_block = cal_block

    def get_calibration_block(self):
        return self._calibration_block

    def set_scan_mode(self, scan_mode):
        self._scan_mode = scan_mode

    def get_scan_mode(self):
        return self._scan_mode

    def set_calibration_temperature(self, calibration_temperature):
        self._calibration_temperature = calibration_temperature

    def get_calibration_temperature(self):
        return self._calibration_temperature

    def set_sine_correction(self, value):
        self._sine_correction = value

    def get_sine_correction(self):
        return self._sine_correction

    def set_cosine_correction(self, value):
        self._cosine_correction = value

    def get_cosine_correction(self):
        return self._cosine_correction

    def set_gain_correction(self, value):
        self._gain_correction = value

    def get_gain_correction(self):
        return self._gain_correction

    def set_temp_correction(self, value):
        self._temp_correction = value

    def get_temp_correction(self):
        return self._temp_correction


class ReferenceResistance:
    def __init__(self, real):
        self._real = real

    def getReal(self):
        return self._real


class VNADeviceInfoBlock:
    def __init__(self):
        self._gain_correction = 1.0
        self._ifPhaseCorrection = 1.1
        self._phaseCorrection = 0.0
        self._sine_correction = 0.0
        self._cosine_correction = 1.0
        self._tempCorrection = 0.011
        self._conversion_temperature = 0.0
        self._calibration_temperature = None
        self._prescaler = 10
        self._scanCommandReflection = "7"
        self._scanCommandTransmission = "6"
        self._openTimeout = 5000
        self._readTimeout = 20000
        self._afterCommandDelay = 0
        self._bootloaderBaudrate = 230400
        self._baudrate = 921600
        self._ddsTicksPerMHz = 10000000
        self._filterMode = 0
        self._maxFrequency = 3000000000
        self._maxLoss = -120.0
        self._maxPhase = 180.0
        self._minFrequency = 1000000
        self._minLoss = 0.0
        self._minPhase = -180.0
        self._numberOfOverscans4Calibration = 1
        self._numberOfSamples4Calibration = 1000
        self._peakSuppression = True
        self._referenceChannel = False
        self._referenceResistance = {"imaginary": 0.0, "real": 50.0, "isNaN": False, "isInfinite": False}
        self._firmwareFileFilter = "*.hex"
        self._scanModeParameters = None
        self._longName = "mini radio solutions - miniVNA Tiny"
        self._shortName = "miniVNA Tiny"
        self._type = "20"
        self._calibration_block = None
        self._scan_mode = None
        self._reference_resistance = 50

    def to_dict(self):
        return {
            '_gain_correction': self._gain_correction,
            '_ifPhaseCorrection': self._ifPhaseCorrection,
            '_phaseCorrection': self._phaseCorrection,
            '_sine_correction': self._sine_correction,
            '_cosine_correction': self._cosine_correction,
            '_tempCorrection': self._tempCorrection,
            '_conversion_temperature': self._conversion_temperature,
            '_calibration_temperature': self._calibration_temperature,
            '_prescaler': self._prescaler,
            '_scanCommandReflection': self._scanCommandReflection,
            '_scanCommandTransmission': self._scanCommandTransmission,
            '_openTimeout': self._openTimeout,
            '_readTimeout': self._readTimeout,
            '_afterCommandDelay': self._afterCommandDelay,
            '_bootloaderBaudrate': self._bootloaderBaudrate,
            '_baudrate': self._baudrate,
            '_ddsTicksPerMHz': self._ddsTicksPerMHz,
            '_filterMode': self._filterMode,
            '_maxFrequency': self._maxFrequency,
            '_maxLoss': self._maxLoss,
            '_maxPhase': self._maxPhase,
            '_minFrequency': self._minFrequency,
            '_minLoss': self._minLoss,
            '_minPhase': self._minPhase,
            '_numberOfOverscans4Calibration': self._numberOfOverscans4Calibration,
            '_numberOfSamples4Calibration': self._numberOfSamples4Calibration,
            '_peakSuppression': self._peakSuppression,
            '_referenceChannel': self._referenceChannel,
            '_referenceResistance': self._referenceResistance,
            '_firmwareFileFilter': self._firmwareFileFilter,
            '_scanModeParameters': self._scanModeParameters,
            '_longName': self._longName,
            '_shortName': self._shortName,
            '_type': self._type,
            '_calibration_block': self._calibration_block,
            '_scan_mode': self._scan_mode,
            '_reference_resistance': self._reference_resistance
        }

    def get_max_loss(self):
        return self._maxLoss

    def getReferenceResistance(self):
        return self._reference_resistance

    def get_dib(self):
        copy.deepcopy(self)

    def getIfPhaseCorrection(self):
        return self._ifPhaseCorrection


class VNACalibrationBlock:
    def __init__(self):
        self._dib = VNADeviceInfoBlock()
        self._CALIBRATION_FILETYPE_3 = None
        self._CALIBRATION_FILETYPE_5 = None
        self._version = None
        self._analyserType = None
        self._calibrationData4Load = None
        self._calibrationData4Loop = None
        self._calibrationData4Open = None
        self._calibrationData4Short = None
        self._calibrationPoints = None
        self._comment = None
        self._file = None
        self._mathHelper = None
        self._scanMode = None
        self._startFrequency = None
        self._stopFrequency = None
        self._numberOfSteps = None
        self._numberOfOverscans = None
        self._temperature = None
        self._cal_blk = []

    def to_dict(self):
        return {
            '_dib': self._dib,
            '_CALIBRATION_FILETYPE_3': self._CALIBRATION_FILETYPE_3,
            '_CALIBRATION_FILETYPE_5': self._CALIBRATION_FILETYPE_5,
            '_version': self._version,
            '_analyserType': self._analyserType,
            '_calibrationData4Load': self._calibrationData4Load,
            '_calibrationData4Loop': self._calibrationData4Loop,
            '_calibrationData4Open': self._calibrationData4Open,
            '_calibrationData4Short': self._calibrationData4Short,
            '_calibrationPoints': self._calibrationPoints,
            '_comment': self._comment,
            '_file': self._file,
            '_mathHelper': self._mathHelper,
            '_scanMode': self._scanMode,
            '_startFrequency': self._startFrequency,
            '_stopFrequency': self._stopFrequency,
            '_numberOfSteps': self._numberOfSteps,
            '_numberOfOverscans': self._numberOfOverscans,
            '_temperature': self._temperature,
            '_cal_blk': self._cal_blk
        }

    def set_calib_param(self, cal_blk):
        self._cal_blk = cal_blk
        self._version = cal_blk["version"]
        self._analyserType = cal_blk["analyserType"]
        self._comment = cal_blk["comment"]
        self._startFrequency = cal_blk["startFrequency"].value
        self._stopFrequency = cal_blk["stopFrequency"].value
        self._numberOfSteps = cal_blk["numberOfSteps"].value
        self._numberOfOverscans = cal_blk["numberOfOverscans"].value
        self._scanMode = cal_blk["scanMode"].mode
        self._calibrationData4Load = cal_blk["calibrationData4Load"]
        self._calibrationData4Loop = cal_blk["calibrationData4Loop"]
        self._calibrationData4Open = cal_blk["calibrationData4Open"]
        self._calibrationData4Short = cal_blk["calibrationData4Short"]

    def get_calib_param(self):
        cal_block = copy.deepcopy(self)
        if hasattr(cal_block, '_dib'):
            delattr(cal_block, '_dib')
        print(cal_block)
        return cal_block
        # cal_blk = self._cal_blk
        # self._cal_blk["version"] = self._version
        # self._cal_blk["analyserType"] = self._analyserType
        # self._cal_blk["comment"] = self._comment
        # self._cal_blk["startFrequency"].value = self._startFrequency
        # self._cal_blk["stopFrequency"].value = self._stopFrequency
        # self._cal_blk["numberOfSteps"].value = self._numberOfSteps
        # self._cal_blk["numberOfOverscans"].value = self._numberOfOverscans
        # self._cal_blk["scanMode"].mode = self._scanMode
        # self._cal_blk["calibrationData4Load"] = self._calibrationData4Load
        # self._cal_blk["calibrationData4Loop"] = self._calibrationData4Loop
        # self._cal_blk["calibrationData4Open"] = self._calibrationData4Open
        # self._cal_blk["calibrationData4Short"] = self._calibrationData4Short
        # return cal_blk

    def setStartFrequency(self, startFrequency):
        self._startFrequency = startFrequency

    def setStopFrequency(self, stopFrequency):
        self._stopFrequency = stopFrequency

    def setNumberOfSteps(self, numberOfSteps):
        self._numberOfSteps = numberOfSteps

    def setAnalyserType(self, analyserType):
        self._analyserType = analyserType

    def setScanMode(self, scanMode):
        self._scanMode = scanMode

    def setTemperature(self, temperature):
        self._temperature = temperature

    def setnumberOfOverscans(self, numberOfOverscans):
        self._numberOfOverscans = numberOfOverscans

    def set_calib_file_name(self, file_name):
        self._file = file_name

    def setCalibrationPoints(self, value):
        self._calibrationPoints = value

    def getStartFrequency(self):
        return self._startFrequency

    def getStopFrequency(self):
        return self._stopFrequency

    def getNumberOfSteps(self):
        return self._numberOfSteps

    def getAnalyserType(self):
        return self._analyserType

    def getScanMode(self):
        return self._scanMode

    def getTemperature(self):
        return self._temperature

    def getnumberOfOverscans(self):
        return self._numberOfOverscans

    def getCalibrationPoints(self):
        return self._calibrationPoints


class VNACalibratedSample:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def setFrequency(self, f): self.set('frequency', f)

    def setRHO(self, rho): self.set('rho', rho)

    def setMag(self, mag): self.set('mag', mag)

    def setTheta(self, theta): self.set('theta', theta)

    def setReflectionLoss(self, loss): self.set('reflection_loss', loss)

    def setReflectionPhase(self, phase): self.set('reflection_phase', phase)

    # def setTransmissionLoss(self): self.get('transmission_loss')
    # def setTransmissionPhase(self): self.get('transmission_phase')
    def setSWR(self, swr): self.set('swr', swr)

    def setR(self, r): self.set('r', r)

    def setX(self, x): self.set('x', x)

    def setZ(self, z): self.set('z', z)

    def setGroupDelay(self, gd): self.set('group_delay', gd)

    # def getFrequency(self): return self.get('frequency')
    # def getRHO(self): return self.get('rho')
    # def getReflectionPhase(self): return self.get('reflection_phase')
    # def getReflectionLoss(self): return self.get('reflection_loss')
    # def getR(self): return self.get('r')
    # def getX(self): return self.get('x')
    # def getZ(self): return self.get('z')
    def getFrequency(self): return self.get('frequency')

    def getRHO(self): return self.get('rho')

    def getMag(self): return self.get('mag')

    def getTheta(self): return self.get('theta')

    def getReflectionLoss(self): return self.get('reflection_loss')

    def getReflectionPhase(self): return self.get('reflection_phase')

    # def getTransmissionLoss(self): return self.get('transmission_loss')
    # def getTransmissionPhase(self): return self.get('transmission_phase')
    def getSWR(self): return self.get('swr')

    def getR(self): return self.get('r')

    def getX(self): return self.get('x')

    def getZ(self): return self.get('z')

    def getGroupDelay(self): return self.get('group_delay')

    def __repr__(self): return str(self.data)


class SCALE_TYPE(Enum):
    SCALE_RETURNPHASE = "SCALE_RETURNPHASE"
    SCALE_TRANSMISSIONPHASE = "SCALE_TRANSMISSIONPHASE"
    SCALE_RETURNLOSS = "SCALE_RETURNLOSS"
    SCALE_TRANSMISSIONLOSS = "SCALE_TRANSMISSIONLOSS"
    SCALE_RS = "SCALE_RS"
    SCALE_RSS = "SCALE_RSS"
    SCALE_SWR = "SCALE_SWR"
    SCALE_THETA = "SCALE_THETA"
    SCALE_XS = "SCALE_XS"
    SCALE_Z_ABS = "SCALE_Z_ABS"
    SCALE_GRPDLY = "SCALE_GRPDLY"
    SCALE_PHASE = "SCALE_PHASE"


class VNACalibratedSampleBlock:
    def __init__(self, sample_count: int) -> None:
        self.calibrated_samples = [None] * sample_count
        self.samples = [None] * sample_count
        # self.mmGRPDLY = VNAMinMaxPair()
        self.mmRHO = MinMaxTracker()
        self.mmMag = MinMaxTracker()
        self.mmTheta = MinMaxTracker()
        self.mmRL = MinMaxTracker()
        self.mmRLPHASE = MinMaxTracker()
        self.mmTL = MinMaxTracker()
        self.mmTLPHASE = MinMaxTracker()
        self.mmSWR = MinMaxTracker()
        self.mmRS = MinMaxTracker()
        self.mmXS = MinMaxTracker()
        self.mmZABS = MinMaxTracker()
        self.mmGroupDelay = MinMaxTracker()

    def to_dict(self):
        return {
            'calibrated_samples': str(self.calibrated_samples),
            'samples': str(self.samples),
            'mmRHO': str(self.mmRHO),
            'mmMag': self.mmMag,
            'mmTheta': self.mmTheta,
            'mmRL': self.mmRL,
            'mmRLPHASE': self.mmRLPHASE,
            'mmTL': self.mmTL,
            'mmTLPHASE': self.mmTLPHASE,
            'mmSWR': self.mmSWR,
            'mmRS': self.mmRS,
            'mmXS': self.mmXS,
            'mmZABS': self.mmZABS,
            'mmGroupDelay': self.mmGroupDelay
        }

    def consume_calibrated_sample(self, sample, index: int):
        self.samples[index] = sample
        # self.mmRHO.consume(sample.getRHO(), index)
        self.mmMag.consume(sample.getMag(), index)
        self.mmTheta.consume(sample.getTheta(), index)
        self.mmRL.consume(sample.getReflectionLoss(), index)
        self.mmRLPHASE.consume(sample.getReflectionPhase(), index)
        # self.mmTL.consume(sample.getTransmissionLoss(), index)
        # self.mmTLPHASE.consume(sample.getTransmissionPhase(), index)
        self.mmSWR.consume(sample.getSWR(), index)
        self.mmRS.consume(sample.getR(), index)
        self.mmXS.consume(sample.getX(), index)
        self.mmZABS.consume(sample.getZ(), index)
        # self.mmGroupDelay.consume(sample.getGroupDelay(), index)
        # self.mmRSS.consume(sample.relative_signal_strength1, index)
        self.calibrated_samples[index] = sample

    def getCalibratedSamples(self):
        return self.samples

    def get_mm_group_delay(self):
        return self.mmGroupDelay

    # def get_mmMag(self):
    #     return self.mmMag
    # def get_mmTheta(self):
    #     return self.mmTheta
    # def get_mmRL(self):
    #     return self.mmRL
    # def get_mmRLPHASE(self):
    #     return self.mmRLPHASE
    # def get_mmTL(self):
    #     return self.mmTL
    # def get_mmTLPHASE(self):
    #     return self.mmTLPHASE
    # def get_mmSWR(self):
    #     return self.mmSWR
    def get_all_mmRL_values(self):
        return self.mmRL.values

    def get_all_mmRLPHASE_values(self):
        return self.mmRLPHASE.values


class MinMaxTracker:
    def __init__(self):
        self.min_value = float(-1e-10)
        self.min_index = -1
        self.max_value = float(1e10)
        self.max_index = -1
        self.values = []  # Store all values by index

    def to_dict(self):
        return {
            'min_value': self.min_value,
            'min_index': self.min_index,
            'max_value': self.max_value,
            'max_index': self.max_index,
            'values': self.values  # Optional: include all values here
        }

    def consume(self, val: float, idx: int) -> float:
        # Extend the list if needed
        while len(self.values) <= idx:
            self.values.append(None)
        self.values[idx] = val

        if val < self.min_value:
            self.min_value = val
            self.min_index = idx
        if val > self.max_value:
            self.max_value = val
            self.max_index = idx


class CalibratedSample:
    def __init__(self, reflection_loss, transmission_loss, reflection_phase, transmission_phase,
                 x, r, z, swr, relative_signal_strength1, theta, group_delay):
        self.reflection_loss = reflection_loss
        self.transmission_loss = transmission_loss
        self.reflection_phase = reflection_phase
        self.transmission_phase = transmission_phase
        self.x = x
        self.r = r
        self.z = z
        self.swr = swr
        self.relative_signal_strength1 = relative_signal_strength1
        self.theta = theta
        self.group_delay = group_delay

    def to_dict(self):
        return {
            'reflection_loss': self.reflection_loss,
            'transmission_loss': self.transmission_loss,
            'reflection_phase': self.reflection_phase,
            'transmission_phase': self.transmission_phase,
            'x': self.x,
            'r': self.r,
            'z': self.z,
            'swr': self.swr,
            'relative_signal_strength1': self.relative_signal_strength1,
            'theta': self.theta,
            'group_delay': self.group_delay
        }


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        # Add handling for JavaObject
        if obj.__class__.__name__ == 'JavaObject':
            # Example: convert to string or extract fields
            return str(obj)  # or implement a method to extract useful info
        # Handle dynamic types created for calibration data
        if obj.__class__.__name__ in ['CalibrationBlock', 'obj']:
            # Extract attributes as dict
            result = {}
            for attr in dir(obj):
                if not attr.startswith('_'):
                    try:
                        value = getattr(obj, attr)
                        # Skip methods
                        if not callable(value):
                            result[attr] = value
                    except:
                        pass
            return result
        # Handle complex numbers
        if isinstance(obj, complex):
            return {'real': obj.real, 'imag': obj.imag, '_type': 'complex'}
        return super().default(obj)


class SaveVar:
    def __init__(self):
        self._json_file_name = self.get_json_file_name()
        print(f"JSON debugging file name: {self._json_file_name}")

    def get_json_file_name(self):
        now = datetime.now()
        # Format as string suitable for filename, e.g., "2025-06-02_23-20-00"
        file_name_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        # Create filename with extension
        file_name = f"debug_output_{file_name_time_str}.json"
        return file_name

    def append_named_json_object(self, obj, name):
        entry = {
            "name": name,
            "data": obj  # CustomEncoder will handle serialization
        }
        with open(self._json_file_name, 'a') as f:
            json_str = json.dumps(entry, cls=CustomEncoder, indent=4)
            f.write(json_str + '\n\n\n')  # Add newlines for separation


class miniVNATiny:
    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def __init__(self):
        # For a 32-bit DDS and 125 MHz reference clock
        self.DDS_TICKS_PER_MHZ = 10000000  # 10000000 #34359738 # int(2 ** 32 / 125)  # 34359738  34359738.368
        self.port_name = '/dev/ttyUSB0'
        self.baud_rate = 921600  # 9600  # Set this to your device's baud rate
        self.ser_port = None
        self.PRESCALER_DEFAULT = 10
        self.data_samples = []
        self.temperature = None
        self.device_supply = None
        self.ser_port = serial.Serial(self.port_name, self.baud_rate, timeout=1)
        #self.ser_port.set_buffer_size(rx_size=4096, tx_size=4096)

    # getDeviceSupply: 8
    # getDeviceFirmwareInfo: 9
    # getDeviceTemperature: 10
    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def get_device_supply(self):
        print("Getting device supply")
        self.send_command("8")
        response = self.receive_data()
        print(response)
        # value = int.from_bytes(response, byteorder='little', signed=False)
        self.device_supply = 6.0
        return self.device_supply

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def get_device_firmwareInfo(self):
        print("Getting device firmware info")
        self.send_command("9")
        response = self.receive_data()
        print(response)

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def get_device_temperature(self):
        print("Getting device temperature")
        self.send_command("10")
        response = self.receive_data()
        value = int.from_bytes(response, byteorder='little', signed=False)
        self.temperature = float(value) // 10
        print(f"Device temperature: {self.temperature} C")
        return self.temperature

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def send_command(self, cmd_str):
        time.sleep(1)
        self.ser_port.reset_input_buffer()
        time.sleep(1)
        cmd_str_cr = cmd_str + "\r"
        # ser.write(message.encode('utf-8'))
        self.ser_port.write(cmd_str_cr.encode('ascii'))
        print(f"Sent: {cmd_str_cr.strip()}")

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def receive_data(self):
        # Read response (read one line)
        # response = ser.readline()
        try:
            time.sleep(1)
            num_bytes = self.ser_port.in_waiting  # Number of bytes available
            print(f"num_bytes in buffer: {num_bytes}")
            response = self.ser_port.read(num_bytes)
            if response:
                value = response
                return value
                # print("Received:", response.decode('utf-8').strip())
                # print("Received:", response.decode('utf-8', errors='ignore').strip())
                # print(f"Received: {response.decode('utf-8', errors='ignore')}")
                # value = int.from_bytes(b, 'little')
                # print(f"Received: {response}")
                # value = int.from_bytes(response, byteorder='little', signed=False)
                # print(f"Received: {value}")
            else:
                print("No response received.")
                value = None
                return value
        except serial.SerialException as e:
            print(f"Error opening or communicating with serial port: {e}")
            if 'self.ser_port' in locals() and self.ser_port.is_open:
                self.ser_port.close()

        finally:
            print("In receive data finally block")
            return value

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def receive_generator_data(self):
        pNumSamples = 10
        currentFrequency = 0
        pFrequencyStep = 1
        try:
            num_bytes = self.ser_port.in_waiting  # Number of bytes available
            print(f"num_bytes in buffer: {num_bytes}")
            response = self.ser_port.read(num_bytes)
            # response = self.ser_port.read(1024)
            if response:
                samples = []
                for i in range(pNumSamples):
                    offset = i * 12
                    # Extract 3-byte unsigned integers (little endian)
                    p1 = int.from_bytes(response[offset + 0:offset + 3], 'little')
                    p2 = int.from_bytes(response[offset + 6:offset + 9], 'little')
                    real = (p1 - p2) / 2.0
                    p3 = int.from_bytes(response[offset + 3:offset + 6], 'little')
                    p4 = int.from_bytes(response[offset + 9:offset + 12], 'little')
                    imaginary = (p3 - p4) / 2.0

                    sample = {
                        'p1': p1,
                        'p2': p2,
                        'p3': p3,
                        'p4': p4,
                        'real': real,
                        'imaginary': imaginary,
                        'frequency': currentFrequency
                    }
                    samples.append(sample)
                    currentFrequency += pFrequencyStep
                return samples
            else:
                print("No response received.")
        except serial.SerialException as e:
            print(f"Error opening or communicating with serial port: {e}")
            if 'self.ser_port' in locals() and self.ser_port.is_open:
                self.ser_port.close()
        finally:
            print("In receive data finally block")

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def receive_byte_stream(self, start_freq, stop_freq, num_freq_sample):
        # Testing with sweep range
        # start_freq = 1000000
        # stop_freq = 100000000

        print("Start Frequency:%s",start_freq)
        print("Stop Frequency:%s",stop_freq)


        # Clear previous data to ensure fresh measurements
        self.data_samples = []
        
        try:
            freq_step = (stop_freq - start_freq) // (num_freq_sample - 1)
        except ZeroDivisionError:
            freq_step = 0  # or some default value
            print("exception: Cannot divide by zero because num_freq_sample is too small.")

        time.sleep(1)
        num_bytes = self.ser_port.in_waiting  # Number of bytes available
        time.sleep(1)
        print(f"num_bytes in buffer: {num_bytes}")

        expected_bytes = 12 * num_freq_sample
        print(f"expected_bytes in buffer: {expected_bytes}")
        buffer = b''
        buffer = self.ser_port.read(12 * num_freq_sample)

        while len(buffer) < expected_bytes:
            bytes_to_read = expected_bytes - len(buffer)
            buffer += self.ser_port.read(bytes_to_read)
            time.sleep(0.01)  # small delay to allow more data to arrive

        print(f"Total bytes read: {len(buffer)}")

        time.sleep(1)
        current_freq = start_freq

        for i in range(num_freq_sample):
            offset = i * 12

            p1 = (buffer[offset + 0] & 0xFF) + ((buffer[offset + 1] & 0xFF) << 8) + ((buffer[offset + 2] & 0xFF) << 16)
            p2 = (buffer[offset + 6] & 0xFF) + ((buffer[offset + 7] & 0xFF) << 8) + ((buffer[offset + 8] & 0xFF) << 16)
            real = (p1 - p2) / 2.0

            p3 = (buffer[offset + 3] & 0xFF) + ((buffer[offset + 4] & 0xFF) << 8) + ((buffer[offset + 5] & 0xFF) << 16)
            p4 = (buffer[offset + 9] & 0xFF) + ((buffer[offset + 10] & 0xFF) << 8) + (
                        (buffer[offset + 11] & 0xFF) << 16)
            imaginary = (p3 - p4) / 2.0

            sample = {
                'angle': imaginary,
                'loss': real,
                'frequency': current_freq,
                'rss1': 0,
                'rss2': 0,
                'rss3': 0,
                'p1': p1,
                'p2': p2,
                'p3': p3,
                'p4': p4,
                'p1Ref': 0,
                'p2Ref': 0,
                'p3Ref': 0,
                'p4Ref': 0
            }

            self.data_samples.append(sample)
            current_freq += freq_step

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def frequency_to_tuning_word(self, freq_hz):
        # freq_hz in Hz
        freq_mhz = freq_hz / 1_000_000
        return int(freq_mhz * self.DDS_TICKS_PER_MHZ)

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def send_frequency(self, freq_hz):
        dds_tuning_word = int(float(freq_hz) / 1.0e7 * float(self.DDS_TICKS_PER_MHZ))
        # print(f"DDS_TICKS_PER_MHZ:{self.DDS_TICKS_PER_MHZ}")
        # print(f"freq_hz:{freq_hz}")
        # print(f"dds_tuning_word:{dds_tuning_word}")
        # print(f"PRESCALER_DEFAULT:{self.PRESCALER_DEFAULT}")

        freq_str = f"{int(round(dds_tuning_word / self.PRESCALER_DEFAULT))}"
        print(f"send frequency string:{freq_str}")
        # print(freq_str)
        self.send_command(freq_str)

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def start_generator(self, frequencyI, frequencyQ, num_freq_sample):
        self.ser_port.reset_input_buffer()
        self.send_command("21")
        time.sleep(0.1)
        self.send_frequency(frequencyI)
        time.sleep(0.1)
        self.send_frequency(frequencyI)
        time.sleep(0.1)
        self.send_command("1")
        time.sleep(0.1)
        self.send_command("0")
        time.sleep(0.1)
        self.receive_byte_stream(frequencyI, frequencyQ, num_freq_sample)
        print(f"scan_start_generator_mode: {self.data_samples}")
        self.plot_samples_db()
        self.data_samples = []
        # self.send_command("21")
        # self.send_frequency(frequencyI)
        # self.send_frequency(frequencyI)
        # self.send_command("1")
        # self.send_command("0")
        # st_gen_data = self.receive_generator_data()
        # time.sleep(0.01)  # 10millisecond delay
        # print(f"start generator data: {st_gen_data}")

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def start_generator_cust(self, frequencyI, frequencyQ):
        self.ser_port.reset_input_buffer()
        self.send_command("7")
        # self.ser_port.reset_input_buffer()
        self.send_command("21")
        # self.send_command("7")
        self.send_frequency(frequencyI)
        self.send_frequency(frequencyI)
        self.send_command("1")
        self.send_command("0")
        # self.send_command("606")
        time.sleep(0.1)  # 1millisecond delay
        st_gen_data = self.receive_generator_data()
        time.sleep(0.1)  # 1millisecond delay
        print(f"start generator data: {st_gen_data}")

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def scan_reflection_mode(self, start_freq, stop_freq, num_freq_sample):
        self.ser_port.reset_input_buffer()
        self.send_command("7")
        time.sleep(0.1)
        self.send_frequency(start_freq)
        time.sleep(0.1)
        self.send_frequency(stop_freq)
        time.sleep(0.1)
        self.send_command(str(num_freq_sample))  # send number of sample
        time.sleep(0.1)
        self.send_command("")
        self.receive_byte_stream(start_freq, stop_freq, num_freq_sample)
        # print(f"scan_reflection_mode: {self.data_samples}")
        self.plot_samples_db()
        # self.data_samples = []

    def scan_reflection_mode_new(self, start_freq, stop_freq, num_freq_sample):
        rc = VNASampleBlock()
        rc.setDeviceTemperature(self.temperature)
        rc.setDeviceSupply(self.device_supply)
        self.ser_port.reset_input_buffer()
        self.send_command("7")
        time.sleep(0.1)
        self.send_frequency(start_freq)
        time.sleep(0.1)
        self.send_frequency(stop_freq)
        time.sleep(0.1)
        self.send_command(str(num_freq_sample))  # send number of sample
        time.sleep(0.1)
        self.send_command("")
        self.receive_byte_stream(start_freq, stop_freq, num_freq_sample)
        # print(f"scan_reflection_mode: {self.data_samples}")
        # self.plot_samples_db()
        rc.setSamples(self.data_samples)
        rc.setScanMode(2)  # self.scanMode
        rc.setNumberOfSteps(num_freq_sample)
        rc.setStartFrequency(start_freq)
        rc.setStopFrequency(stop_freq)
        # rc.setAnalyserType(this.getDeviceInfoBlock().getType())
        # self.data_samples = []
        return rc

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def stop_generator(self):
        self.send_command("7")
        self.send_frequency(0)
        self.send_frequency(0)
        self.send_command("1")
        self.send_command("0")
        stop_gen_data = self.receive_generator_data()
        time.sleep(0.01)  # 10millisecond delay
        print(f"stop generator data: {stop_gen_data}")

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def plot_samples_db(self):
        freq = []
        magnitudes_db = []

        for sample in self.data_samples:
            real = sample['real']
            imaginary = sample['imaginary']
            frequency = sample['frequency']

            z = complex(real, imaginary)
            magnitude = abs(z)
            magnitude_db = 10 * np.log10(magnitude) if magnitude > 0 else -np.inf  # Avoid log(0)

            freq.append(frequency)
            magnitudes_db.append(magnitude_db)

        plt.figure(figsize=(10, 6))
        plt.plot(freq, magnitudes_db, marker='o', linestyle='-', color='b')
        plt.title('Magnitude (dB) vs Frequency')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude (dB)')
        plt.grid(True)
        plt.draw()
        plt.show()
        # plt.pause(0.001)  # Allow GUI event loop to update

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def loadCalibrationRAWData(self, filename):
        try:
            # Try to read the calibration file with javaobj-py3
            with open(filename, "rb") as f:
                # Read all data first
                data = f.read()
                
            # Try using javaobj-py3's new API
            try:
                import javaobj.v2 as javaobj_v2
                # Use v2 API which handles multiple objects better
                parser = javaobj_v2.JavaObjectParser(data)
                cal_data = {}
                
                print("Reading calibration file structure with javaobj-py3...")
                cal_data['version'] = parser.read_object()
                print(f"  Version: {cal_data['version']}")
                cal_data['analyserType'] = parser.read_object()
                print(f"  Analyser Type: {cal_data['analyserType']}")
                cal_data['comment'] = parser.read_object()
                cal_data['startFrequency'] = parser.read_object()
                cal_data['stopFrequency'] = parser.read_object()
                cal_data['numberOfSteps'] = parser.read_object()
                cal_data['numberOfOverscans'] = parser.read_object()
                cal_data['scanMode'] = parser.read_object()
                
                print("Reading calibration blocks...")
                block_names = ['calibrationData4Load', 'calibrationData4Open', 'calibrationData4Short',
                               'calibrationData4Loop']
                for block_name in block_names:
                    print(f"  Reading {block_name}...")
                    cal_data[block_name] = parser.read_object()
                    if cal_data[block_name] is not None:
                        print(f"    Successfully read {block_name}")
                    else:
                        print(f"    Warning: {block_name} is None")
                
                print("Calibration file loaded successfully with javaobj-py3")
                return cal_data
                
            except Exception as e:
                print(f"javaobj-py3 v2 API failed: {e}")
                # Try the legacy unmarshaller approach
                with open(filename, "rb") as f:
                    unmarshaller = javaobj.JavaObjectUnmarshaller(f)
                    cal_data = {}
                    
                    print("Trying legacy unmarshaller approach...")
                    cal_data['version'] = unmarshaller.readObject()
                    print(f"  Version: {cal_data['version']}")
                    cal_data['analyserType'] = unmarshaller.readObject()
                    print(f"  Analyser Type: {cal_data['analyserType']}")
                    cal_data['comment'] = unmarshaller.readObject()
                    cal_data['startFrequency'] = unmarshaller.readObject()
                    cal_data['stopFrequency'] = unmarshaller.readObject()
                    cal_data['numberOfSteps'] = unmarshaller.readObject()
                    cal_data['numberOfOverscans'] = unmarshaller.readObject()
                    cal_data['scanMode'] = unmarshaller.readObject()
                    
                    print("Reading calibration blocks...")
                    block_names = ['calibrationData4Load', 'calibrationData4Open', 'calibrationData4Short',
                                   'calibrationData4Loop']
                    for block_name in block_names:
                        print(f"  Reading {block_name}...")
                        cal_data[block_name] = unmarshaller.readObject()
                        if cal_data[block_name] is not None:
                            print(f"    Successfully read {block_name}")
                        else:
                            print(f"    Warning: {block_name} is None")
                    
                    print("Calibration file loaded successfully")
                    return cal_data
                    
        except FileNotFoundError:
            print(f"Error: Calibration file not found: {filename}")
            return None
        except Exception as e:
            print(f"Error opening calibration file: {type(e).__name__}: {e}")
            
        # Use alternative calibration loader as fallback
        print("\nUsing alternative calibration loader with default values...")
        print("WARNING: This is a temporary workaround - actual calibration data is not being loaded")
        return self.createDefaultCalibrationData()
    
    def createDefaultCalibrationData(self):
        """Create default calibration data structure as a workaround"""
        # Create dummy calibration data structure
        cal_data = {
            'version': 5,
            'analyserType': 20,
            'comment': 'Default calibration data (workaround)',
            'startFrequency': type('obj', (object,), {'value': 1000000}),  # 1 MHz
            'stopFrequency': type('obj', (object,), {'value': 3000000000}),  # 3 GHz
            'numberOfSteps': type('obj', (object,), {'value': 1000}),
            'numberOfOverscans': type('obj', (object,), {'value': 1}),
            'scanMode': type('obj', (object,), {'mode': 'Reflection'}),
        }
        
        # Create dummy calibration blocks with temperature data
        for block_name in ['calibrationData4Load', 'calibrationData4Open', 'calibrationData4Short', 'calibrationData4Loop']:
            cal_block = type('CalibrationBlock', (object,), {
                'deviceTemperature': type('obj', (object,), {'value': 49.133}),
                'samples': [VNABaseSample() for i in range(1000)]
            })
            # Initialize samples with default values
            block_instance = cal_block()
            for i, sample in enumerate(block_instance.samples):
                # Use different default values for each calibration type
                if block_name == 'calibrationData4Open':
                    sample.angle = 180.0  # Open circuit typically has 180 degree phase
                    sample.loss = 1.0
                elif block_name == 'calibrationData4Short':
                    sample.angle = -180.0  # Short circuit typically has -180 degree phase
                    sample.loss = -1.0
                elif block_name == 'calibrationData4Load':
                    sample.angle = 0.0  # Load (50 ohm) has 0 degree phase
                    sample.loss = 0.1  # Small loss
                else:  # Loop
                    sample.angle = 0.0
                    sample.loss = 0.0
                    
                sample.frequency = 1000000 + i * 1000
                sample.rss1 = 100
                sample.rss2 = 100
                sample.rss3 = 100
            cal_data[block_name] = block_instance
        
        return cal_data

    # ------------------------------------------------------
    # Method:
    # ------------------------------------------------------
    def calculateCalibrationTemperature(self, cal_block):
        if cal_block is None:
            print("Error: cal_block is None in calculateCalibrationTemperature")
            return
            
        count = 3
        temp_sum = []
        
        # Check each calibration data block
        blocks_to_check = [
            ('calibrationData4Open', 'Open'),
            ('calibrationData4Short', 'Short'),
            ('calibrationData4Load', 'Load')
        ]
        
        for block_key, block_name in blocks_to_check:
            if block_key not in cal_block:
                print(f"Warning: {block_key} not found in calibration block")
                continue
                
            block = cal_block[block_key]
            if block is None:
                print(f"Warning: {block_key} is None")
                continue
                
            if not hasattr(block, 'deviceTemperature'):
                print(f"Warning: {block_key} has no deviceTemperature attribute")
                continue
                
            if block.deviceTemperature is None:
                print(f"Warning: {block_key}.deviceTemperature is None")
                continue
                
            if not hasattr(block.deviceTemperature, 'value'):
                print(f"Warning: {block_key}.deviceTemperature has no value attribute")
                continue
                
            temp_sum.append(block.deviceTemperature.value)
            
        if len(temp_sum) == 0:
            print("Error: No valid temperature readings found in calibration data")
            self.temperature = 25.0  # Default room temperature
            print(f"Using default temperature: {self.temperature}°C")
        else:
            self.temperature = sum(temp_sum) / len(temp_sum)
            print(f"Calculated calibration temperature from {len(temp_sum)} readings: {self.temperature}°C")

    def createCalibrationContextForCalibrationPoints(self, cal_block):
        get_phase_correction = 0
        get_gain_correction = 1
        get_temp_correction = 0.011
        context = VNACalibrationContextTiny()
        # context.set_dib(dib)
        context.set_scan_mode("Reflection")
        context.set_calibration_block(cal_block)
        context.set_calibration_temperature(self.temperature)

        # Calculate phase correction in radians
        correction_radian = get_phase_correction * math.pi / 180.0
        context.set_sine_correction(math.sin(correction_radian))
        context.set_cosine_correction(math.cos(correction_radian))

        # Set gain and temperature correction factors
        context.set_gain_correction(get_gain_correction)
        context.set_temp_correction(get_temp_correction)

        return context

    def createCalibrationPoints(self, cal_context, cal_block):
        list_length = len(cal_block['calibrationData4Load'].samples)
        # list_length = 1000  # TODO: you have to change it
        rc = [None] * list_length

        for i in range(list_length):
            s_open = {cal_block['calibrationData4Open'].samples[i]}
            s_short = {cal_block['calibrationData4Short'].samples[i]}
            s_load = {cal_block['calibrationData4Load'].samples[i]}
            # s_loop = {calibration_data['calibrationData4Loap'].samples[i]}
            rc[i] = self.create_calibration_point(cal_context, s_open, s_short, s_load)

        # cal_block.setCalibrationPoints(rc)
        return rc

    def create_calibration_point(self, cal_context, sOpen, sShort, sLoad):
        corrOpen = VNABaseSample()
        corrShort = VNABaseSample()
        corrLoad = VNABaseSample()

        corrOpen = self.calculateCorrectedBaseSample(cal_context, sOpen, cal_context.get_calibration_temperature())
        corrShort = self.calculateCorrectedBaseSample(cal_context, sShort, cal_context.get_calibration_temperature())
        corrLoad = self.calculateCorrectedBaseSample(cal_context, sLoad, cal_context.get_calibration_temperature())
        rc = self.createCalibrationPointForReflection(corrOpen, corrShort, corrLoad)
        return rc

    def calculateCorrectedBaseSample(self, context, sample, temp):

        rc = VNABaseSample(sample)  # Copy the sample

        old_real = rc.getLoss()
        old_imag = rc.getAngle()

        delta_temp = 40.0 - temp
        corr_temp_factor = 1.0 - delta_temp * context.get_temp_correction()

        old_real *= corr_temp_factor
        old_imag *= corr_temp_factor

        new_real = int(old_real)
        # Calculation for newImag follows the Java formula
        new_imag = int((
                                   old_imag * context.get_gain_correction() - old_real * 1.0 * context.get_sine_correction()) / context.get_cosine_correction())
        rc.setLoss(float(new_real))
        rc.setAngle(float(new_imag))
        return rc

    def createCalibrationPointForReflection(self, sOpen, sShort, sLoad):
        rc = VNACalibrationPoint()

        m1 = sOpen.as_complex()
        m2 = sShort.as_complex()
        m3 = sLoad.as_complex()

        # Constants (not strictly necessary to define separately)
        A1 = 1.0
        A2 = -1.0
        A3 = 0.0

        p1 = (m2 * A2 - m1 * A1) * (m1 - m3)
        p2 = (m3 * A3 - m1 * A1) * (m2 - m1)
        p3 = (m2 * A2 - m1 * A1) * (-1.0)
        p4 = (m3 * A3 - m1 * A1) * (-2.0)

        try:
            delta_e = (p1 + p2) / (p3 - p4)
        except ZeroDivisionError:
            delta_e = 0 + 0j  # Default complex value
            print("Warning: Cannot divide by zero in delta_e calculation, using default value")

        rc.set_delta_e(delta_e)

        # Calculate e11 with zero division check
        denominator = m2 * -1.0 - m1 * 1.0
        if abs(denominator) < 1e-10:  # Check for near-zero
            e11 = 0 + 0j
            print("Warning: Near-zero denominator in e11 calculation, using default value")
        else:
            e11 = (m2 - m1 + delta_e * -2.0) / denominator
        rc.set_e11(e11)

        e00 = m1 - m1 * 1.0 * e11 + delta_e * 1.0
        rc.set_e00(e00)

        rc.set_frequency(sOpen.get_frequency())

        return rc

    def createResizedCalibrationBlock(self, mainCalibrationBlock, fStart, fStop, numSteps, scanMode):
        rc = VNACalibrationBlock()
        rc.setStartFrequency(fStart)
        rc.setStopFrequency(fStop)
        rc.setNumberOfSteps(numSteps)
        rc.setAnalyserType(mainCalibrationBlock.getAnalyserType())
        rc.setScanMode(mainCalibrationBlock.getScanMode())
        rc.setTemperature(mainCalibrationBlock.getTemperature())
        # source = [VNACalibrationPoint() for _ in range(1000)] #FIXME: auto pick this value
        source = mainCalibrationBlock.getCalibrationPoints()
        target = [None] * numSteps
        freq_step = (fStop - fStart) // numSteps
        target_freq = fStart
        source_index = 0
        source_steps = len(source)

        for target_index in range(numSteps):
            while source_index < source_steps and source[source_index].get_frequency() < target_freq:
                source_index += 1

            if source_index >= source_steps:
                source_index = source_steps - 1

            if source[source_index].get_frequency() == target_freq:
                target[target_index] = source[source_index]
            else:
                p1 = source[source_index - 1]
                p2 = source[source_index]
                target[target_index] = self.interpolate(p1, p2, target_freq)

            target_freq += freq_step

        rc._calibrationPoints = target
        # rc.setCalibrationPoints(target);
        return rc

    def interpolate_value(self, v1, v2, k1, k2):
        """Linear interpolation helper."""
        if k2 == 0:
            return v1  # avoid division by zero
        return v1 + (v2 - v1) * (k1 / k2)

    def interpolate(self, p1, p2, f):
        f1 = p1.get_frequency()
        f2 = p2.get_frequency()
        k1 = f - f1
        k2 = f2 - f1

        rc = VNACalibrationPoint()
        rc.frequency = f
        rc.loss = self.interpolate_value(p1.loss, p2.loss, k1, k2)
        rc.phase = self.interpolate_value(p1.phase, p2.phase, k1, k2)
        rc.delta_e = self.interpolate_value(p1.delta_e, p2.delta_e, k1, k2)
        rc.e00 = self.interpolate_value(p1.e00, p2.e00, k1, k2)
        rc.e11 = self.interpolate_value(p1.e11, p2.e11, k1, k2)
        # rc.edf = self.interpolate_value(p1.edf, p2.edf, k1, k2)
        # rc.erf = self.interpolate_value(p1.erf, p2.erf, k1, k2)
        # rc.esf = self.interpolate_value(p1.esf, p2.esf, k1, k2)
        rc.rss1 = self.interpolate_value(p1.rss1, p2.rss1, k1, k2)
        rc.rss2 = self.interpolate_value(p1.rss2, p2.rss2, k1, k2)
        rc.rss3 = self.interpolate_value(p1.rss3, p2.rss3, k1, k2)

        return rc

    def createCalibrationContextForCalibratedSamples(self, calBlock):
        get_phase_correction = 0
        get_gain_correction = 1
        get_temp_correction = 0.011

        context = VNACalibrationContextTiny()
        context.set_calibration_block(calBlock)
        context.set_scan_mode(calBlock.getScanMode())
        context.set_calibration_temperature(self.temperature)
        correction_radian = get_phase_correction * math.pi / 180.0
        context.set_sine_correction(math.sin(correction_radian))
        context.set_cosine_correction(math.cos(correction_radian))
        context.set_gain_correction(get_gain_correction)
        context.set_temp_correction(get_temp_correction)

        return context

    def createCalibratedSamples(self, context, raw_data):
        listLength = len(raw_data.getSamples())
        calBlock = context.get_calibration_block()
        rc = VNACalibratedSampleBlock(listLength)
        for i, sample in enumerate(raw_data.getSamples()):
            s = self.create_calibrated_sample(context, raw_data.getSamples()[i], calBlock.getCalibrationPoints()[i])
            self.post_process_calibrated_sample(s, context)
            # rc.consumeCalibratedSample(s, i)
            rc.consume_calibrated_sample(s, i)

        self.post_process_calibrated_samples(rc, context)
        return rc

    def create_calibrated_sample(self, context, raw_sample, calib_point):

        correctedRawSample = self.calculateCorrectedBaseSample(context, raw_sample,
                                                               context.get_calibration_temperature())
        dib = context.get_dib()
        deltaTemp = context.get_calibration_temperature() - context.get_conversion_temperature() + 0.001
        ifPhaseCorrection = deltaTemp * dib.getIfPhaseCorrection()
        rc = self.createCalibratedSampleForReflection(context, correctedRawSample, calib_point, ifPhaseCorrection)
        return rc

    def createCalibratedSampleForReflection(self, context, correctedRawSample, calib_point, ifPhaseCorrection):
        dib = context.get_dib()
        rhoM = correctedRawSample.as_complex()
        rho = (rhoM - calib_point.get_e00()) / (rhoM * calib_point.get_e11() - calib_point.get_delta_e())
        mag = abs(rho)
        if mag > 1.0:
            mag = 1.0

        # Check for division by zero in SWR calculation
        if mag >= 0.9999:  # Close to 1.0
            swr = 999.9  # Large but finite value representing very high SWR
        else:
            swr = (1.0 + mag) / (1.0 - mag)
            
        # Protect against log(0) for return loss calculation
        if mag <= 0:
            return_loss = context.get_dib().get_max_loss()
        else:
            return_loss = 20.0 * math.log10(mag)
            return_loss = max(return_loss, context.get_dib().get_max_loss())

        # Calculate the phase (argument) in degrees
        return_phase = math.degrees(math.atan2(rho.imag, rho.real))

        if 0.0 <= return_phase < 0.1:
            return_phase = 0.1
        elif -0.1 < return_phase < 0.0:
            return_phase = -0.1

        return_phase += ifPhaseCorrection

        if return_phase > 180.0:
            return_phase -= 360.0
        elif return_phase < -180.0:
            return_phase += 360.0

        f = math.cos(math.radians(return_phase))
        g = math.sin(math.radians(return_phase))

        rr = f * mag
        ss = g * mag

        ref_resistance = context.get_dib().getReferenceResistance().real

        denominator = ((1.0 - rr) ** 2) + (ss ** 2)

        x_imp = (2.0 * ss / denominator) * ref_resistance
        r_imp = ((1.0 - rr ** 2 - ss ** 2) / denominator) * ref_resistance

        if r_imp < 0.0:
            r_imp = 0.0

        z_imp = math.sqrt(r_imp ** 2 + x_imp ** 2)
        rc = VNACalibratedSample()
        rc.setFrequency(correctedRawSample.get_frequency())
        rc.setRHO(rho)
        rc.setMag(mag)
        rc.setReflectionLoss(return_loss)
        rc.setReflectionPhase(return_phase)
        rc.setSWR(swr)
        rc.setR(r_imp)
        rc.setX(x_imp)
        rc.setZ(z_imp)
        return rc

    def post_process_calibrated_sample(self, sample, context):
        sample.setTheta(math.degrees((math.pi / 2) - math.atan2(sample.getR(), sample.getX())))

        if sample.getRHO() is None:
            radian = math.radians(sample.getReflectionPhase())
            amplitude = 10.0 ** (sample.getReflectionLoss() / 20.0)
            real = amplitude * math.cos(radian)
            imag = amplitude * math.sin(radian)
            sample.setRHO(complex(real, imag))

    def post_process_calibrated_samples(self, csb, context):
        samples = csb.getCalibratedSamples()
        len_samples = len(samples)
        if len_samples > 1:
            mmGroupDelay = csb.get_mm_group_delay()
            diffFreq = samples[1].getFrequency() - samples[0].getFrequency()
            lastSample = samples[0]
            lastSample.setGroupDelay(0.0)
            if context.get_scan_mode() == 2:  # i.e. 'reflection':
                for i in range(1, len_samples):
                    currentSample = samples[i]
                    lastPhase = lastSample.getReflectionPhase()
                    currentPhase = currentSample.getReflectionPhase()
                    diffPhase = currentPhase - lastPhase
                    if diffPhase > 170.0:
                        diffPhase -= 360.0
                    elif diffPhase < -170.0:
                        diffPhase += 360.0

                    try:
                        groupDelay = -0.002777777777777778 * (diffPhase / diffFreq) * 1.0E9
                    except ZeroDivisionError:
                        groupDelay = 0  # or some default value
                        print(
                            "exception: Cannot divide by zero, Check  groupDelay = -0.002777777777777778 * (diffPhase / diffFreq) * 1.0E9")

                    currentSample.setGroupDelay(groupDelay)
                    mmGroupDelay.consume(groupDelay, i)
                    lastSample = currentSample
            # You can add transmission mode if needed


if __name__ == '__main__':

    plt.ion()
    freq_hz = 50000000  # 50MHz

    print("miniVNA Tiny is going to initialize")
    m_vna = miniVNATiny()
    time.sleep(0.1)
    print(f"serial port settings: {m_vna.ser_port}")
    print(f"miniVNA Tinay is connected to Port {m_vna.port_name}")
    print(f"Baud rate is {m_vna.baud_rate}")
    time.sleep(0.1)
    m_vna.get_device_supply()
    time.sleep(0.1)
    m_vna.get_device_firmwareInfo()
    time.sleep(0.1)
    m_vna.get_device_temperature()
    # time.sleep(0.1)
    # dds_ticks_per_mhz = m_vna.frequency_to_tuning_word(freq_hz)
    # print(f"DDS Ticks/MHz: {dds_ticks_per_mhz}")
    # print(" Going to start generator")
    # time.sleep(1)
    # m_vna.start_generator(frequencyI = 0, frequencyQ = 0, num_freq_sample = 1)
    # time.sleep(1)
    # m_vna.scan_reflection_mode(start_freq = 1000000, stop_freq = 2000000 , num_freq_sample = 100)

    # Load calibration data
    file_name = rf"./REFL_miniVNATiny.cal"
    calBlock = m_vna.loadCalibrationRAWData(file_name)
    
    # Check if calibration data was loaded successfully
    if calBlock is None:
        print("ERROR: Failed to load calibration file. Please check:")
        print(f"  1. File exists at: {file_name}")
        print(f"  2. File format is correct")
        print(f"  3. javaobj library is properly installed")
        m_vna.ser_port.close()
        exit(1)
    
    m_vna.calculateCalibrationTemperature(calBlock)
    calContext = m_vna.createCalibrationContextForCalibrationPoints(calBlock)
    cal_block_corr = m_vna.createCalibrationPoints(calContext, calBlock)
    mainCalibrationBlock = VNACalibrationBlock()
    mainCalibrationBlock.set_calib_param(calBlock)
    mainCalibrationBlock.set_calib_file_name(file_name)
    mainCalibrationBlock.setCalibrationPoints(cal_block_corr)
    mainCalibrationBlock.setTemperature(m_vna.temperature)

    # sv1 = SaveVar()
    # sv1.append_named_json_object(mainCalibrationBlock, name="mainCalibrationBlock")

    # VNACalibrationBlock
    rcb = m_vna.createResizedCalibrationBlock(mainCalibrationBlock, fStart=1000000, fStop=2000000, numSteps=100,
                                              scanMode="REFL")
    time.sleep(1)

    data = m_vna.scan_reflection_mode_new(start_freq=1000000, stop_freq=2000000, num_freq_sample=100)
    # sv1.append_named_json_object(data, name="data")

    context = m_vna.createCalibrationContextForCalibratedSamples(rcb)
    # sv1.append_named_json_object(context, name="context")

    dib = VNADeviceInfoBlock()
    # sv1.append_named_json_object(dib, name="dib")

    context.set_conversion_temperature(data.getDeviceTemperature())

    calSamples = m_vna.createCalibratedSamples(context, data)
    # Assuming 'block' is an instance of VNACalibratedSampleBlock or similar
    samples = calSamples.getCalibratedSamples()
    frequencies = [sample.getFrequency() for sample in samples if sample is not None]
    print(frequencies)
    # sv_vna_data = SaveVar()
    np_frequencies = np.array(frequencies)
    calSamples.getCalibratedSamples()
    print(calSamples.get_all_mmRL_values())
    print(calSamples.get_all_mmRLPHASE_values())

    now = datetime.now()
    # Format as string suitable for filename, e.g., "2025-06-02_23-20-00"
    file_name_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    # Create filename with extension
    file_name_vna_output = f"vna_data_{file_name_time_str}.json"

    vna_output_data = {
        "frequencies": frequencies,
        "RL": calSamples.get_all_mmRL_values(),
        "RLPHASE": calSamples.get_all_mmRLPHASE_values()
    }
    print(vna_output_data["frequencies"])
    #print(f"vna_output_data[RL]: {vna_output_data["RL"]}")
    #print(f"vna_output_data[RLPHASE]: {vna_output_data["RLPHASE"]}")
    # Save the data dictionary to a JSON file
    with open(file_name_vna_output, "w") as json_file:
        json.dump(vna_output_data, json_file, indent=4)

    system = platform.system()  # 'Windows', 'Linux', 'Darwin', etc.

    if system == "Windows":
        fig, ax = plt.subplots(2, 1, figsize=(10, 6))
        ax[0].plot(np_frequencies / 1e6, calSamples.get_all_mmRL_values(), marker='o', linestyle='-', color='b')
        ax[0].set_title('Reflection Loss (dB)')
        ax[0].set_xlabel('Frequency(MHz)')
        ax[0].set_xlim(1, 2)
        ax[0].set_ylim(-12, -4)  # Adjust y-axis limits as needed
        ax[0].set_ylabel('Reflection Loss (dB)')
        ax[0].grid(True)
        ax[1].plot(np_frequencies / 1e6, calSamples.get_all_mmRLPHASE_values(), marker='o', linestyle='-', color='r')
        ax[1].set_title('Reflection Phase (degrees)')
        ax[1].set_xlabel('Frequency(MHz)')
        ax[1].set_ylabel('Reflection Phase (degrees)')
        ax[1].set_xlim(1, 2)
        ax[1].set_ylim(50, 170)  # Adjust y-axis limits as needed
        ax[1].grid(True)
        plt.tight_layout()
        plt.ioff()
        plt.draw()
        plt.savefig(file_name[:-4] + ".png")
        plt.show()

    # plt.show()
    server_address = "FC:01:7C:92:05:6C"  # PC Bluetooth MAC address
    port = 4

    try:
        print(f"Attempting to connect to Bluetooth server at {server_address}:{port}")
        sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        sock.settimeout(10)  # 10 second timeout
        sock.connect((server_address, port))
        
        print("Bluetooth connection established, sending file...")
        with open(file_name_vna_output, "rb") as f:
            data = f.read(1024)
            while data:
                sock.sendall(data)
                data = f.read(1024)

        print("File sent successfully")
        sock.close()
        print("Socket closed on client side")
    except OSError as e:
        print(f"Bluetooth connection failed: {e}")
        print(f"Could not connect to {server_address}:{port}")
        print("Data has been saved locally to:", file_name_vna_output)
        print("You can transfer the file manually or fix the Bluetooth connection")
    except Exception as e:
        print(f"Unexpected error during Bluetooth transfer: {e}")
        print("Data has been saved locally to:", file_name_vna_output)
    
    print("Program End")
