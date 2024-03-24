#! /usr/bin/env python3
#
# Copyright 2024 Kenneth J. Gibson, kenjgibson@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Python class definitions for IEEE 2030.5 data objects

  This module defines python classes for a subset of the IEEE 2030.5
  Smart Energy Profile (SEP) elements described in sep.xsd.  

  IEEE 2030.5 defines a protocol for communication between Smart Grid devices
  and encompasses the communications between Distributed Energy Resources (DER)
  and DER Management Systems (DERMS).  It is a RESTful protocol wherein a DER
  initiates regular PUTs to report status and nameplate information to the DERMS
  and issues GETs to receive command & control info from the DERMS.

  This initial 'V0.1' is focused on the minimum required info as specific in
  IEEE 2030.11 and assumes both endpoints are implemented in Python so does
  not strictly map to the correct foundation data types (UInt16, 32, etc.)
"""

__authors__ = [
  '"Ken Gibson" <kenjgibson@gmail.com>'
]

# Scientific notation class used for many values (Watts, VArs, Volts, etc.)
# Value = mantissa x 10^exponent
# TO-DO:  Add methods for coversion to/from Int, UInt, etc.
class SciNum(object):
    def __init__(self, mantissa=0, exponent=0):
      self._mant = int(mantissa)   # Int32 
      self._exp = int(exponent)     # 10^multiplier as UInt8

# The following is wrong.  TimeType is one of few data elementes in sep.xsd
# that uses 64-bit integers.  For my simple prototype, will use the type
# returned by the standard Python 'time' module
class TimeType(float):
    def __init__(self, value=0):
        super().__init__(value)

class DateTimeInterval(object):
    def __init__(self, startTime, duration):
        self.start = TimeType(startTime)
        self.duration = int(duration)

# Abstract base class for top-level SEP objects to define common methods
# shared by all classes.  These objects get serialized to/from http messages
# so member data is stored in dictionaries which are easily serializable.
class SEPObject(object):
    def __init__(self):
        self._dict = {}

    def set(self, key, value):
        # Insure that only the items defined in 2030.5 are included
        # Future to-do:  Set the 'exists' flag to match
        if key in self._dict.keys():
            self._dict[key] = value
            return value
        return None

    def get(self, key):
        # Future to-do: Check the 'exists' flag
        if key in self._dict.keys():
            return self._dict[key]
        return None
    
    def toDict(self):
        # Return the dictionary for serializing into HTTP
        return self._dict
    
    def fromDict(self, dict={}):
        for key in dict:
            self.set(key, dict[key])


# Simplified Device Capability class.  This is one of the first resources a
# DER GETs from the DERMS server to determine the function sets supported
# by the server and the endpoints for each supported function set.
#
# First define the bits in the flags field
DC_TimeLink_exists = (1 << 4)
DC_ResponseSetListLink_exists = (1 << 7)
DC_FileListLink_exists = (1 << 10)
DC_DERProgramListLink_exists = (1 << 11)
DC_SelfDeviceLink_exists = (1 << 14)
DC_EndDeviceListLink_exists = (1 << 16)
DC_pollRate_exists = (1 << 17)

class DeviceCapability(SEPObject):
    def __init__(self, dict={}):
        # Explicity instantiate just the elements defined in 2030.5/sep.xsd
        self._dict = {
            'flags': None,
            'pollRate': None,
            'DERProgramList': None,
            'FileList': None,
            'TimeLink': None,
            'EndDeviceList': None
        }
        self.fromDict(dict)

# Immutable tuples repsenting status and operating performance categories
NormalOpPerfCat = ('not specified', 'Category A', 'Category B')
AbnormalOpPerfCat = ('not specified', 'Category I', 'Category II', 'Category III')

# Inverter Status values
IS_NA           = 0
IS_OFF          = 1
IS_SLEEPING     = 2
IS_TRACKING     = 3
IS_FORCED_DERATING  = 4
IS_SHUTTING_DOWN    = 5
IS_FAULT_EXISTS     = 6
IS_STANDBY      = 7
IS_TEST_MODE    = 8
IS_VENDOR_SPECIFIC  = 9

# Connect Status values
CS_CONNECTED    = 0
CS_AVAILABLE    = 1
CS_OPERATING    = 2
CS_TEST         = 3
CS_FAULT        = 4

# Operational Mode Status values
OMS_NA          = 0
OMS_OFF         = 1
OMS_OPERATIONAL = 2
OMS_TEST        = 3

# Alarm Status (DER Fault) bitmap, used in DERStatus object
DF_OVER_CURRENT       = (1 << 0)
DF_OVER_VOLTAGE       = (1 << 1)
DF_UNDER_VOLTAGE      = (1 << 2)
DF_OVER_FREQUENCY     = (1 << 3)
DF_UNDER_FREQUENCY    = (1 << 4)
DF_VOLTAGE_IMBALANCE  = (1 << 5)
DF_CURRENT_IMBALANCE  = (1 << 6)
DF_EMERGENCY_LOCAL    = (1 << 7)
DF_EMERGENCY_REMOTE   = (1 << 8)
DF_LOW_POWER_INPUT    = (1 << 9)
DF_PHASE_ROTATION     = (1 << 10)

# DERTypes reported in DERCapability.
TYPE_VIRT_MIXED = 1
TYPE_ENGINE     = 2
TYPE_FUEL_CELL  = 3
TYPE_PV         = 4
TYPE_HEAT_PWR   = 5
TYPE_STORAGE    = 6
TYPE_EV         = 81
TYPE_PV_STORAGE = 82

# For constructing the path to Function Set resources as defined in 2030.5
EP_DEVCAP       = '/dcap'
EP_TIME         = '/tm'
EP_END_DEVICE   = '/edev'
EP_DER          = '/der'
EP_DERPGM       = '/derp'
EP_EVENTLOG     = '/lel'
EP_CONFIG       = '/cfg'
EP_LOADSHED     = '/lsl'
EP_DERSETTINGS  = '/derg'
EP_DERSTATUS    = '/ders'
EP_DERAVAIL     = '/dera'
EP_DERCAP       = '/dercap'
EP_DERCTL       = '/derc'
EP_DDERCTL      = '/dderc'

# As defined in sep.xsd, vendor info is provided through an element named "File"
# FileFlags
mfSerNum_exists = (1 << 5)
mfHwVer_exists = (1 << 6)
activateTime_exists = (1 << 7)

FileTypes = (
   'Software Image',
   'Security Credential',
   'Configuration',
   'Log'
)
# IEEE 2030 'File' object 
class DERFile(SEPObject):
    def __init__(self):
        self._dict = {
            'flags':None,              # UInt32
            'href':None,               # string
            'activateTime':None,       # Time type
            'fileURI':None,            # string
            'lFDI':None,               # sep.xsd says = lFDI of the device??
            'mfHwVer':None,            # HW Version string
            'mfID':None,               # Vendor's "Private Enterprise Number"
            'mfModel':None,            # String32 type
            'mfSerNum':None,           # String32
            'mvVer':None,              # String16
            'size':None,               # Size of the file @fileURI
            'type':None                # One of FileTypes above
        }

# DER Capability Flags.  From se_types.h in EPRI's 2030 client reference implementtion
# These are bits in the Flags field of the DERCapability object
rtgWh_exists = (1 << 5)
rtgVarNeg_exists = (1 << 6)
rtgVar_exists = (1 << 7)
rtgVA_exists = (1 << 8)
rtgUnderExcitedW_exists = (1 << 9)
rtgUnderExcitedPF_exists = (1 << 10)
rtgOverExcitedW_exists = (1 << 11)
rtgOverExcitedPF_exists = (1 << 12)
rtgNormalCategory_exists = (1 << 13)
rtgMinPFNeg_exists = (1 << 14)
rtgMinPF_exists = (1 << 15)
rtgMaxDischargeRateW_exists = (1 << 16)
rtgMaxDischargeRateVA_exists = (1 << 17)
rtgMaxChargeRateW_exists = (1 << 18)
rtgMaxChargeRateVA_exists = (1 << 19)
rtgAh_exists = (1 << 20)
rtgAbnormalCategory_exists = (1 << 21)

# Bit positions for DER Modes Supported as defined in 2030.5 use in type 
# DERControlType, the type of the 'modesSupported' field of DERCapability and
# 'modesEnabled' field in DERSettings
capChargeMode =    (1 << 0)
capDischargeMode = (1 << 1)
capOpModConnect =  (1 << 2)
capOpModEnergize = (1 << 3)
capOpModFixedPFAbsorbW = (1 << 4)
capOpModFixedPFInjectW = (1 << 5)
capOpModFixedVar = (1 << 6)
capOpModFixedW =    (1 << 7)
capOpModFreqDroop = (1 << 8)
capOpModFreqWatt =  (1 << 9)
capOpModHFRTMayTrip = (1 << 10)
capOpModHFRTMustTrip = (1 << 11)
capOpModHVRTMayTrip = (1 << 12)
capOpModHVRTMomentaryCessation = (1 << 13)
capOpModHVRTMustTrip = (1 << 14)
capOpModLFRTMayTrip = (1 << 15)

# SEP class for reporting the DER's Nameplate ratings.
# These are fixed, read-only values based on how the DER
# is designed and manufactured.
# As such, these should not be expected to change
# Unless noted otherwise, the type of most of these values is the
# Scientific notation defined by 2030.5.
class DERCapability(SEPObject):
    def __init__(self):
        self._dict = {
            'capFlags': None,               # UInt32 
            'href': None,
            'modesSupported': None,         # UInt32, flags defined above
            'rtgAmps': None,                # Nameplate Amps RMS
            'rtgAbnormalCategory': None,    # UInt8
            'rtgAh': None,                  # Amp-hours
            'rtgMaxChargeRateVA': None,
            'rtgMaxChargeRateW': None,
            'rtgMaxDischargeRateVA': None,  # type ActivePower
            'rtgMaxDischargeRateW': None,   # type PowerFactor
            'rtgMinPF': None,
            'rtgMinPFNeg': None,
            'rtgNormalCategory': None,      # UInt8
            'rtgOverExcitedPF': None,       # type PowerFactor
            'rtgOverExcitedW': None,        # ActivePower, type SciNum
            'rtgUnderExcitedPF': None,      # type PowerFactor
            'rtgUnderExcitedW': None,       
            'rtgVA': None,                  # Nameplate apparent pwr, type SciNum
            'rtgVar': None,                 # Nameplate reactive pwr, type SciNum
            'rtgVarNeg': None,              # Max negative VARs, type SciNum
            'rtgW': None,                   # Nameplate real pwr, type SciNum
            'rtgWh': None,                  # Nameplate Watt-hours, type SciNum
            'DERtype': None                 # UInt8 w/ types defined above
        }

# Variations from NP ratings based on how the device is configured
# at installation time by the installer, or due to aging over time.
# As such, these are also read-only to the DERMS but could change
# over time due to age or DER maintenance actions.
# Fields can remaine None if the value is the same as DERCapability
class DERSettings(SEPObject):
    def __init__(self):
        self._dict = {
            'modesEnabled':None,    # Bit map with DERControlType bit positions defined above
            'setESDelay':None,      # UInt16, Enter svc delay in units of .01 seconds
            'setESHighFreq':None,   # UInt16, Enter svc freq high, in .01 Hz
            'setESHighVolt':None,   # UInt16, Enter svc high as % in .01 percents
            'setESLowFreq':None,
            'setESLowVolt':None,
            'setESRandomDelay':None,  #Randomized delay in .01 Sec units
            'setGradW':None,        # UInt16, Active Pwr ramp rate in .01%/Sec
            'setMaxA':None,         # Max AC Current RMS, type SciNum
            'setMaxAh':None,        # Max usable energy storage.  Type SciNum
            'setMaxChargeRateVA':None,  #Max Apparent pwr the DER can absorb
            'setMaxChargeRateW':None,   #Max Real pwr the DER can absorb 
            'setMaxDischargeRateVA':None, # Max Apparent Power delivered
            'setMaxDischargeRateW':None,  # Max Real Power delivered
            'setMaxVA':None,              # limits max apparant power delivered
            'setMaxVar':None,             # limits max reactive power delivered
            'setMaxVarNeg':None,          # limit max Q consumed.  Interpreted as neg num
            'setMaxW':None,         # Limits max real power delivered by the DER
            'setMaxWh':None,        # Limit max storage capacity
            'setMinPF':None,        # Set minimum PF positive 'displacement'  Type PF
            'setMinPFNeg':None,     # Corrolary to above.  Type PowerFactor
            'setSoftGradeW':None,   # UInt16, Soft Start rate of change in .01%/Sec
            'setVRef':None,         # Nominal AC V at utility PCC.  Type SciNum
            'setVRefOfs':None,      # Offset between Utility PCC and actual interface to the DER's inverter
            'updatedTime':None      # Time these settings were last updated
        }

# DER Control Base structure
# Control Values retrieved by the DER through http GET
# These are the more static, time-invariant control parameters set by the DER
# Note:
#   HFRT/LFRT = High and Low Frequency Ride-Through
#   HVRT/LVRT = High and Low Voltage Ride-Through
# TEMPORARY SHORTCUT:
#  For curve datapoints, use Python tuples containing int32 x and y values
#  and store in Python lists.
# For Voltage and Freq, time (x value) in 100s of S
# y value is % of nominal
#
class DERControlBase(SEPObject):
    def __init__(self):
        self._dict = {
            'opModConnect':None,      # Boolean Connect (TRUE) or Not
            'opModEnergize':None,     # Boolean Energize or not
            'opModFixedPF':None,      # set Power Factor
            'opModFixedVar':None,     # Either setMaxW, setMaxVar, or statVarAvail
            'opModFixedW':None,       # Signed Percent Type
            'opModFreqDroop':None,    # FreqDroopType. VAR limit based on freq
            'opModFreqWatt':None,     # DER Curve Link type
            'opModHFRTMustTrip':None, # DER Curve Link type
            'opModHVRTMomentaryCessation':None, #DER Curve Link type
            'opModHVRTMustTrip':None,
            'opModLFRTMustTrip':None,
            'opModLVRTMomentaryCessation':None,
            'opModLVRTMustTrip':None,
            'opModMaxLimW':None,      # Percent type.  Max % of NP active pwr allowed
            'opModTargetVar':None,    # Reactive pwr.  Desired target VARs
            'opModTargetW':None,      # Desired target real power
            'opModVoltVar':None,      # DER Curve Link type
            'opModVoltWatt':None,     # DER Curve Link type
            'opModWattPF':None,       # DER Curve Link type
            'opModWattVar':None,      # Curve Link
            'rampTms':None            # UInt16, desired transition time in .01 secs
        }

# Dictionary of bit positions for control modes enabled on the DER
# These will be used in the DERSettings object provided by the DERMS
# to the DER
# NOTE:  sep.xsd and se_types.h in EPRI's client don't seem to match.
opModVoltVar = 0x01 
opModFreqWatt = 0x01<<1
opModFreqDroop = 0x01<<2
opModWattPF = 0x01<<3
opModVoltWatt = 0x01<<4
opModLVRTMomentaryCessation = 0x01<<5
opModLVRTMustTrip = 0x01<<6
opModHVRTMomentaryCessation = 0x01<<7
opModHVRTMustTrip = 0x01<<8
opModLFRTMustTrip = 0x01<<9
opModHFRTMustTrip = 0x01<<10
opModConnect = 0x01<<11
opModEnergize = 0x01<<12
opModMaxLimW = 0x01<<13
opModFixedVar = 0x01<<14
opModFixedPF = 0x01<<15
opModFixedW = 0x01<<16
opModTargetW = 0x01<<17
opModTargetVar = 0x01<<18
ChargeMode = 0x01<<19
DischargeMode = 0x01<<20

# The DERControl object for issueing Control Events to a DER
# Contains a DER ControlBase structure
class DERControl(SEPObject):
    def __init__(self):
        self._dict = {
            'flags': None,
            'replyTo': None,            #URI endpoint to send DERControResponse
            'responseRequired': None,   # Boolean byte
            'subscribable': None,
            'mRID': None,
            'description': None,        #Character string
            'version': None,
            'creationTime': None,       #Float seconds since epoch
            'EventStatus': None,
            'interval': None,           #DateTimeInterval type
            'randomizeDuration': None,  #Int16
            'randomizeStart': None,     #Int16
            'DERControlBase': None      #DER Control Base object
        }

class DefaultDERControl(SEPObject):
    def __init__(self, dict={}):
        self._dict = {
            'flags': None,
            'subscribable': None,
            'mRID': None,
            'description': None,        #Character string
            'version': None,
            'DERControlBase': None,
            'setESDelay': None,         #UInt16
            'setESHighFreq': None,      #UInt16
            'setESHighVolt': None,      #Int16
            'setESLowFreq': None,       #UInt16
            'setESLowVolt': None,       #Int16
            'setESRandomDelay': None,   #UInt16
            'setGradW': None,           #UInt16
            'setSoftGradW': None        #UInt16
        }
        self.fromDict(dict)

class DERControlResponse(SEPObject):
    def __init__(self):
        self._dict = {
            'flags': None,
            'createdDateTime': None,      #Float seconds since epoch
            'endDeviceLFDI': None,        #Hex Binary 160
            'status': None,               #UInt8
            'subject': None               #mRIDType
        }

class DERStatus(SEPObject):
    def __init__(self):
        self._dict = {
            'alarmStatus':None,
            'genConnectStatus':None,
            'inverterStatus':None,
            'localControlModeStatus':None,
            'manufacturerStatus':None,
            'operationalModeStatus':None,
            'readingTime':None,
            'stateOfChargeStatus':None,
            'storageModeStatus':None,
            'storConnectStatus':None
        }

class DERAvailability(SEPObject):
    def __init__(self):
        self._dict = {
            'availabilityDuration':None,
            'maxChargeDuration':None,
            'readingTime':None,
            'reserveChargePercent':None,
            'reservePercent':None,
            'statVarAvail':None,
            'statWAvail':None
        }
