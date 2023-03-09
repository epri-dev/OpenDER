# Copyright © 2023 Electric Power Research Institute, Inc. All rights reserved.

# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met: 
# · Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# · Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# · Neither the name of the EPRI nor the names of its contributors may be used 
#   to endorse or promote products derived from this software without specific
#   prior written permission.


# -*- coding: utf-8 -*-
# @Time    : 2/12/2021 11:18 AM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : common_file_format.py
# @Software: PyCharm

import pandas as pd
import numpy as np
import pathlib
import os
import logging


class DERCommonFileFormat:
    parameters_list = ['NP_NORMAL_OP_CAT', 'NP_ABNORMAL_OP_CAT', 'NP_P_MAX', 'NP_P_MAX_OVER_PF', 'NP_OVER_PF',
                       'NP_P_MAX_UNDER_PF', 'NP_UNDER_PF', 'NP_VA_MAX', 'NP_Q_MAX_INJ', 'NP_Q_MAX_ABS',
                       'NP_P_MAX_CHARGE', 'NP_APPARENT_POWER_CHARGE_MAX', 'NP_AC_V_NOM', 'NP_REACTIVE_SUSCEPTANCE',

                       'AP_LIMIT_ENABLE', 'AP_LIMIT',

                       'ES_RANDOMIZED_DELAY', 'ES_PERMIT_SERVICE',
                       'ES_V_LOW', 'ES_V_HIGH', 'ES_F_LOW', 'ES_F_HIGH', 'ES_DELAY', 'ES_RAMP_RATE',

                       'CONST_PF_MODE_ENABLE', 'CONST_PF_EXCITATION', 'CONST_PF', 'CONST_Q_MODE_ENABLE', 'CONST_Q',

                       'QV_MODE_ENABLE', 'QV_VREF', 'QV_VREF_AUTO_MODE',
                       'QV_VREF_TIME', 'QV_CURVE_V2', 'QV_CURVE_Q2', 'QV_CURVE_V3', 'QV_CURVE_Q3', 'QV_CURVE_V1',
                       'QV_CURVE_Q1', 'QV_CURVE_V4', 'QV_CURVE_Q4', 'QV_OLRT',

                       'QP_MODE_ENABLE', 'QP_CURVE_P3_GEN', 'QP_CURVE_P2_GEN', 'QP_CURVE_P1_GEN', 'QP_CURVE_Q3_GEN',
                       'QP_CURVE_Q2_GEN', 'QP_CURVE_Q1_GEN', 'QP_CURVE_P3_LOAD', 'QP_CURVE_P2_LOAD', 'QP_CURVE_P1_LOAD',
                       'QP_CURVE_Q3_LOAD', 'QP_CURVE_Q2_LOAD', 'QP_CURVE_Q1_LOAD',

                       'PV_MODE_ENABLE', 'PV_CURVE_V1', 'PV_CURVE_P1', 'PV_CURVE_V2', 'PV_CURVE_P2', 'PV_OLRT',

                       'OV2_TRIP_V', 'OV2_TRIP_T', 'OV1_TRIP_V', 'OV1_TRIP_T', 'UV1_TRIP_V', 'UV1_TRIP_T', 'UV2_TRIP_V',
                       'UV2_TRIP_T', 'OF2_TRIP_F', 'OF2_TRIP_T', 'OF1_TRIP_F', 'OF1_TRIP_T', 'UF1_TRIP_F', 'UF1_TRIP_T',
                       'UF2_TRIP_F', 'UF2_TRIP_T',

                       'PF_MODE_ENABLE', 'PF_DBOF', 'PF_DBUF', 'PF_KOF', 'PF_KUF', 'PF_OLRT',

                       'MC_LVRT_V1', 'MC_HVRT_V1',

                       'NP_EFFICIENCY', 'NP_V_DC', 'P_Q_INJ_PU', 'P_Q_ABS_PU', 'Q_MAX_INJ_PU', 'Q_MAX_ABS_PU',
                       'NP_PRIO_OUTSIDE_MIN_Q_REQ', 'NP_V_MEAS_UNBALANCE', 'NP_PHASE', 'NP_P_MIN_PU', 'AP_RT',
                       'CONST_PF_RT', 'CONST_Q_RT', 'QP_RT', 'NP_SET_EXE_TIME', 'NP_MODE_TRANSITION_TIME',
                       'STATUS_INIT', 'ES_RANDOMIZED_DELAY_ACTUAL', 'NP_Q_CAPABILITY_BY_P_CURVE',
                       'NP_Q_CAPABILITY_LOW_P', 'NP_TYPE', 'NP_RESISTANCE', 'NP_REACTANCE', 'NP_INV_DELAY',
                       'NP_CURRENT_PU', 'NP_RT_RAMP_UP_TIME','MC_RESP_T', 'NP_CTE_RESP_T', 'NP_REACT_TIME',
                       'NP_V_MEAS_DELAY',

                       'DVS_MODE_ENABLE', 'DVS_K',
                       ]

    # Creating object slots, so incorrect usage of variable names are rejected.
    __slots__ = tuple(['_' + param for param in parameters_list]) + tuple(['param_inputs'])

    def __init__(self,
                 as_file_path=pathlib.Path(os.path.dirname(__file__)).joinpath("../Parameters", "AS-with std-values.csv"),
                 model_file_path=pathlib.Path(os.path.dirname(__file__)).joinpath("../Parameters",
                                                                                  "Model-parameters.csv")):
        """
        Creating a DER common file format object
        :param as_file_path: File directory address for Common file format Applied Setting file.
        :param model_file_path: File directory address for Model custom parameter file.
        """

        # Read DER file and remove suffix
        df1 = pd.read_csv(as_file_path, index_col=0)
        df1.index = df1.index.map(lambda s: s.replace("-AS", ''))
        df1.index = df1.index.map(lambda s: s.replace("-SS", ''))

        # Read Model Parameters file
        df2 = pd.read_csv(model_file_path, index_col=0)

        frames = [df1, df2]

        # Filtering dataframe with the parameters present in the parameter_list array
        df = pd.concat(frames)
        df = df.reindex(index=self._get_parameter_list())

        df["New Index"] = self._get_parameter_list()
        self.param_inputs = df.reset_index().set_index("New Index")["VALUE"].apply(pd.to_numeric, errors="ignore")

        # Nameplate Variables with default values
        self._NP_NORMAL_OP_CAT = "CAT_A"
        self._NP_ABNORMAL_OP_CAT = "CAT_I"
        self._NP_EFFICIENCY = 1
        self._NP_P_MAX = None
        self._NP_VA_MAX = None
        self._NP_Q_MAX_INJ = None
        self._NP_Q_MAX_ABS = None
        self._NP_P_MIN_PU = 0
        self._NP_SET_EXE_TIME = 0
        self._P_Q_INJ_PU = None
        self._P_Q_ABS_PU = None
        self._Q_MAX_INJ_PU = None
        self._Q_MAX_ABS_PU = None
        self._NP_REACTIVE_SUSCEPTANCE = None
        self._NP_Q_CAPABILITY_BY_P_CURVE = None
        self._NP_Q_CAPABILITY_LOW_P = 'REDUCED'
        self._NP_P_MAX_CHARGE = 0
        self._NP_APPARENT_POWER_CHARGE_MAX = None

        # DER Model Variables with default values
        self._ES_RANDOMIZED_DELAY_ACTUAL = 0
        self._AP_RT = 15
        self._CONST_PF_RT = 5
        self._CONST_Q_RT = 5
        self._QP_RT = 5
        self._PF_MODE_ENABLE = True
        self._NP_MODE_TRANSITION_TIME = 15
        self._STATUS_INIT = True
        self._NP_V_MEAS_UNBALANCE = "AVG"
        self._NP_PRIO_OUTSIDE_MIN_Q_REQ = 'REACTIVE'
        self._NP_PHASE = 'THREE'
        self._NP_TYPE = None
        self._NP_V_DC = None
        self._NP_RESISTANCE = 0.001
        self._NP_REACTANCE = 0.2
        self._NP_INV_DELAY = 0.02
        self._NP_CURRENT_PU = 1.2
        self._NP_RT_RAMP_UP_TIME = 0
        self._MC_RESP_T = 0
        self._NP_CTE_RESP_T = 0.16
        self._NP_REACT_TIME = 0
        self._NP_V_MEAS_DELAY = 0

        self._DVS_MODE_ENABLE = False
        self._DVS_K = 2

        # Function settings with default values
        self._AP_LIMIT_ENABLE = False
        self._AP_LIMIT = 1

        self._ES_PERMIT_SERVICE = True
        self._ES_V_LOW = 0.917
        self._ES_V_HIGH = 1.05
        self._ES_F_LOW = 59.5
        self._ES_F_HIGH = 60.1
        self._ES_DELAY = 300
        self._ES_RAMP_RATE = 300
        self._ES_RANDOMIZED_DELAY = 0

        self._CONST_PF_MODE_ENABLE = False
        self._CONST_PF = 1
        self._CONST_PF_EXCITATION = "ABS"

        self._QV_MODE_ENABLE = False
        self._QV_VREF = 1
        self._QV_VREF_AUTO_MODE = False
        self._QV_VREF_TIME = 300
        self._QV_CURVE_V1 = None
        self._QV_CURVE_Q1 = None
        self._QV_CURVE_V2 = None
        self._QV_CURVE_Q2 = 0
        self._QV_CURVE_V3 = None
        self._QV_CURVE_Q3 = 0
        self._QV_CURVE_V4 = None
        self._QV_CURVE_Q4 = None
        self._QV_OLRT = 5

        self._CONST_Q_MODE_ENABLE = False
        self._CONST_Q = 0

        self._QP_CURVE_P1_GEN = None
        self._QP_CURVE_Q1_GEN = 0
        self._QP_CURVE_P2_GEN = 0.5
        self._QP_CURVE_Q2_GEN = 0
        self._QP_CURVE_P3_GEN = 1
        self._QP_CURVE_Q3_GEN = None
        self._QP_CURVE_P2_LOAD = -0.5
        self._QP_CURVE_Q2_LOAD = 0
        self._QP_CURVE_P1_LOAD = 0
        self._QP_CURVE_Q1_LOAD = 0
        self._QP_CURVE_P3_LOAD = -1
        self._QP_CURVE_Q3_LOAD = 0.44

        self._QP_MODE_ENABLE = False

        self._PV_MODE_ENABLE = False
        self._PV_CURVE_P1 = 1
        self._PV_CURVE_V1 = 1.06
        self._PV_CURVE_P2 = None
        self._PV_CURVE_V2 = 1.1
        self._PV_OLRT = 10

        self._OV2_TRIP_V = 1.2
        self._OV2_TRIP_T = 0.16
        self._OV1_TRIP_V = 1.1
        self._OV1_TRIP_T = None
        self._UV1_TRIP_V = None
        self._UV1_TRIP_T = None
        self._UV2_TRIP_V = None
        self._UV2_TRIP_T = None
        self._OF2_TRIP_F = 62
        self._OF2_TRIP_T = 0.16
        self._OF1_TRIP_F = 61.2
        self._OF1_TRIP_T = 300
        self._UF1_TRIP_F = 58.5
        self._UF1_TRIP_T = 300
        self._UF2_TRIP_F = 56.5
        self._UF2_TRIP_T = 0.16

        self._PF_DBOF = 0.036
        self._PF_DBUF = 0.036
        self._PF_KOF = 0.05
        self._PF_KUF = 0.05
        self._PF_OLRT = 5

        self._MC_LVRT_V1 = None
        self._MC_HVRT_V1 = None

        if self.isNotNaN(self.param_inputs.NP_TYPE):
            self.NP_TYPE = self.param_inputs.NP_TYPE

        if self.isNotNaN(self.param_inputs.NP_NORMAL_OP_CAT):
            self.NP_NORMAL_OP_CAT = self.param_inputs.NP_NORMAL_OP_CAT
        if self.isNotNaN(self.param_inputs.NP_ABNORMAL_OP_CAT):
            self.NP_ABNORMAL_OP_CAT = self.param_inputs.NP_ABNORMAL_OP_CAT

        if self.isNotNaN(self.param_inputs.NP_VA_MAX):
            self.NP_VA_MAX = self.param_inputs.NP_VA_MAX
        if self.isNotNaN(self.param_inputs.NP_P_MAX):
            self.NP_P_MAX = self.param_inputs.NP_P_MAX

        if self.isNotNaN(self.param_inputs.NP_P_MAX_OVER_PF):
            self.NP_P_MAX_OVER_PF = self.param_inputs.NP_P_MAX_OVER_PF
        if self.isNotNaN(self.param_inputs.NP_OVER_PF):
            self.NP_OVER_PF = self.param_inputs.NP_OVER_PF
        if self.isNotNaN(self.param_inputs.NP_P_MAX_UNDER_PF):
            self.NP_P_MAX_UNDER_PF = self.param_inputs.NP_P_MAX_UNDER_PF
        if self.isNotNaN(self.param_inputs.NP_UNDER_PF):
            self.NP_UNDER_PF = self.param_inputs.NP_UNDER_PF

        if self.isNotNaN(self.param_inputs.NP_Q_MAX_INJ):
            self.NP_Q_MAX_INJ = self.param_inputs.NP_Q_MAX_INJ
        if self.isNotNaN(self.param_inputs.NP_Q_MAX_ABS):
            self.NP_Q_MAX_ABS = self.param_inputs.NP_Q_MAX_ABS
        if self.isNotNaN(self.param_inputs.NP_P_MAX_CHARGE):
            self.NP_P_MAX_CHARGE = self.param_inputs.NP_P_MAX_CHARGE
        if self.isNotNaN(self.param_inputs.NP_APPARENT_POWER_CHARGE_MAX):
            self.NP_APPARENT_POWER_CHARGE_MAX = self.param_inputs.NP_APPARENT_POWER_CHARGE_MAX
        if self.isNotNaN(self.param_inputs.NP_AC_V_NOM):
            self.NP_V_DC = self.param_inputs.NP_AC_V_NOM * 1.5
            self.NP_AC_V_NOM = self.param_inputs.NP_AC_V_NOM

        if self.isNotNaN(self.param_inputs.NP_REACTIVE_SUSCEPTANCE):
            self.NP_REACTIVE_SUSCEPTANCE = self.param_inputs.NP_REACTIVE_SUSCEPTANCE

        self.nameplate_value_validity_check()

        if self.isNotNaN(self.param_inputs.P_Q_ABS_PU):
            self.P_Q_ABS_PU = self.param_inputs.P_Q_ABS_PU
        if self.isNotNaN(self.param_inputs.P_Q_INJ_PU):
            self.P_Q_INJ_PU = self.param_inputs.P_Q_INJ_PU
        if self.isNotNaN(self.param_inputs.Q_MAX_ABS_PU):
            self.Q_MAX_ABS_PU = self.param_inputs.Q_MAX_ABS_PU
        if self.isNotNaN(self.param_inputs.Q_MAX_INJ_PU):
            self.Q_MAX_INJ_PU = self.param_inputs.Q_MAX_INJ_PU

        self.initialize_NP_Q_CAPABILTY_BY_P_CURVE()

        if self.isNotNaN(self.param_inputs.NP_EFFICIENCY):
            self.NP_EFFICIENCY = self.param_inputs.NP_EFFICIENCY

        if self.isNotNaN(self.param_inputs.NP_V_DC):
            self.NP_V_DC = self.param_inputs.NP_V_DC

        if self.isNotNaN(self.param_inputs.NP_PRIO_OUTSIDE_MIN_Q_REQ):
            self.NP_PRIO_OUTSIDE_MIN_Q_REQ = self.param_inputs.NP_PRIO_OUTSIDE_MIN_Q_REQ

        if self.isNotNaN(self.param_inputs.NP_V_MEAS_UNBALANCE):
            self.NP_V_MEAS_UNBALANCE = self.param_inputs.NP_V_MEAS_UNBALANCE

        if self.isNotNaN(self.param_inputs.NP_PHASE):
            self.NP_PHASE = self.param_inputs.NP_PHASE

        if self.isNotNaN(self.param_inputs.NP_P_MIN_PU):
            self.NP_P_MIN_PU = self.param_inputs.NP_P_MIN_PU

        if self.isNotNaN(self.param_inputs.ES_RANDOMIZED_DELAY_ACTUAL):
            self.ES_RANDOMIZED_DELAY_ACTUAL = self.param_inputs.ES_RANDOMIZED_DELAY_ACTUAL

        if self.isNotNaN(self.param_inputs.AP_RT):
            self.AP_RT = self.param_inputs.AP_RT

        if self.isNotNaN(self.param_inputs.CONST_PF_RT):
            self.CONST_PF_RT = self.param_inputs.CONST_PF_RT

        if self.isNotNaN(self.param_inputs.CONST_Q_RT):
            self.CONST_Q_RT = self.param_inputs.CONST_Q_RT

        if self.isNotNaN(self.param_inputs.QP_RT):
            self.QP_RT = self.param_inputs.QP_RT

        if self.isNotNaN(self.param_inputs.PF_MODE_ENABLE):
            self.PF_MODE_ENABLE = self.param_inputs.PF_MODE_ENABLE

        if self.isNotNaN(self.param_inputs.NP_SET_EXE_TIME):
            self.NP_SET_EXE_TIME = self.param_inputs.NP_SET_EXE_TIME

        if self.isNotNaN(self.param_inputs.NP_MODE_TRANSITION_TIME):
            self.NP_MODE_TRANSITION_TIME = self.param_inputs.NP_MODE_TRANSITION_TIME

        if self.isNotNaN(self.param_inputs.STATUS_INIT):
            self.STATUS_INIT = self.param_inputs.STATUS_INIT

        if self.isNotNaN(self.param_inputs.NP_RESISTANCE):
            self.NP_RESISTANCE = self.param_inputs.NP_RESISTANCE

        if self.isNotNaN(self.param_inputs.NP_REACTANCE):
            self.NP_REACTANCE = self.param_inputs.NP_REACTANCE

        if self.isNotNaN(self.param_inputs.NP_INV_DELAY):
            self.NP_INV_DELAY = self.param_inputs.NP_INV_DELAY

        if self.isNotNaN(self.param_inputs.NP_CURRENT_PU):
            self.NP_CURRENT_PU = self.param_inputs.NP_CURRENT_PU

        if self.isNotNaN(self.param_inputs.NP_CTE_RESP_T):
            self.NP_CTE_RESP_T = self.param_inputs.NP_CTE_RESP_T

        if self.isNotNaN(self.param_inputs.MC_RESP_T):
            self.MC_RESP_T = self.param_inputs.MC_RESP_T

        if self.isNotNaN(self.param_inputs.DVS_MODE_ENABLE):
            self.DVS_MODE_ENABLE = self.param_inputs.DVS_MODE_ENABLE

        if self.isNotNaN(self.param_inputs.DVS_K):
            self.DVS_K = self.param_inputs.DVS_K

        if self.isNotNaN(self.param_inputs.NP_RT_RAMP_UP_TIME):
            self.NP_RT_RAMP_UP_TIME = self.param_inputs.NP_RT_RAMP_UP_TIME

        if self.isNotNaN(self.param_inputs.NP_REACT_TIME):
            self.NP_REACT_TIME = self.param_inputs.NP_REACT_TIME

        if self.isNotNaN(self.param_inputs.NP_V_MEAS_DELAY):
            self.NP_V_MEAS_DELAY = self.param_inputs.NP_V_MEAS_DELAY

        if self.isNotNaN(self.param_inputs.AP_LIMIT_ENABLE):
            self.AP_LIMIT_ENABLE = self.param_inputs.AP_LIMIT_ENABLE
        if self.isNotNaN(self.param_inputs.AP_LIMIT):
            self.AP_LIMIT = self.param_inputs.AP_LIMIT

        if self.isNotNaN(self.param_inputs.ES_PERMIT_SERVICE):
            self.ES_PERMIT_SERVICE = self.param_inputs.ES_PERMIT_SERVICE
        if self.isNotNaN(self.param_inputs.ES_V_LOW):
            self.ES_V_LOW = self.param_inputs.ES_V_LOW
        if self.isNotNaN(self.param_inputs.ES_V_HIGH):
            self.ES_V_HIGH = self.param_inputs.ES_V_HIGH

        if self.isNotNaN(self.param_inputs.ES_F_LOW):
            self.ES_F_LOW = self.param_inputs.ES_F_LOW
        if self.isNotNaN(self.param_inputs.ES_F_HIGH):
            self.ES_F_HIGH = self.param_inputs.ES_F_HIGH
        if self.isNotNaN(self.param_inputs.ES_DELAY):
            self.ES_DELAY = self.param_inputs.ES_DELAY
        if self.isNotNaN(self.param_inputs.ES_RAMP_RATE):
            self.ES_RAMP_RATE = self.param_inputs.ES_RAMP_RATE
        if self.isNotNaN(self.param_inputs.ES_RANDOMIZED_DELAY):
            self.ES_RANDOMIZED_DELAY = self.param_inputs.ES_RANDOMIZED_DELAY

        if self.isNotNaN(self.param_inputs.CONST_PF_MODE_ENABLE):
            self.CONST_PF_MODE_ENABLE = self.param_inputs.CONST_PF_MODE_ENABLE
        if self.isNotNaN(self.param_inputs.CONST_PF_EXCITATION):
            self.CONST_PF_EXCITATION = self.param_inputs.CONST_PF_EXCITATION
        if self.isNotNaN(self.param_inputs.CONST_PF):
            self.CONST_PF = self.param_inputs.CONST_PF

        if self.NP_NORMAL_OP_CAT == "CAT_A":
            self.QV_CURVE_V2 = 1
            self.QV_CURVE_V3 = 1
            self.QV_CURVE_V1 = 0.9
            self.QV_CURVE_Q1 = 0.25
            self.QV_CURVE_V4 = 1.1
            self.QV_CURVE_Q4 = -0.25
            self.QV_OLRT = 10
            self.QP_CURVE_Q3_GEN = -0.25
        else:
            self.QV_CURVE_V2 = 0.98
            self.QV_CURVE_V3 = 1.02
            self.QV_CURVE_V1 = 0.92
            self.QV_CURVE_Q1 = 0.44
            self.QV_CURVE_V4 = 1.08
            self.QV_CURVE_Q4 = -0.44
            self.QV_OLRT = 5
            self.QP_CURVE_Q3_GEN = -0.44

        if self.isNotNaN(self.param_inputs.QV_MODE_ENABLE):
            self.QV_MODE_ENABLE = self.param_inputs.QV_MODE_ENABLE
        if self.isNotNaN(self.param_inputs.QV_VREF):
            self.QV_VREF = self.param_inputs.QV_VREF
        if self.isNotNaN(self.param_inputs.QV_VREF_TIME):
            self.QV_VREF_TIME = self.param_inputs.QV_VREF_TIME
        if self.isNotNaN(self.param_inputs.QV_VREF_AUTO_MODE):
            self.QV_VREF_AUTO_MODE = self.param_inputs.QV_VREF_AUTO_MODE

        if self.isNotNaN(self.param_inputs.QV_CURVE_V2):
            self.QV_CURVE_V2 = self.param_inputs.QV_CURVE_V2
        if self.isNotNaN(self.param_inputs.QV_CURVE_V3):
            self.QV_CURVE_V3 = self.param_inputs.QV_CURVE_V3
        if self.isNotNaN(self.param_inputs.QV_CURVE_V1):
            self.QV_CURVE_V1 = self.param_inputs.QV_CURVE_V1
        if self.isNotNaN(self.param_inputs.QV_CURVE_V4):
            self.QV_CURVE_V4 = self.param_inputs.QV_CURVE_V4

        if self.isNotNaN(self.param_inputs.QV_CURVE_Q1):
            self.QV_CURVE_Q1 = self.param_inputs.QV_CURVE_Q1
        if self.isNotNaN(self.param_inputs.QV_CURVE_Q2):
            self.QV_CURVE_Q2 = self.param_inputs.QV_CURVE_Q2
        if self.isNotNaN(self.param_inputs.QV_CURVE_Q3):
            self.QV_CURVE_Q3 = self.param_inputs.QV_CURVE_Q3
        if self.isNotNaN(self.param_inputs.QV_CURVE_Q4):
            self.QV_CURVE_Q4 = self.param_inputs.QV_CURVE_Q4
        if self.isNotNaN(self.param_inputs.QV_OLRT):
            self.QV_OLRT = self.param_inputs.QV_OLRT

        if self.isNotNaN(self.param_inputs.CONST_Q_MODE_ENABLE):
            self.CONST_Q_MODE_ENABLE = self.param_inputs.CONST_Q_MODE_ENABLE
        if self.isNotNaN(self.param_inputs.CONST_Q):
            self.CONST_Q = self.param_inputs.CONST_Q

        if self.isNotNaN(self.param_inputs.QP_MODE_ENABLE):
            self.QP_MODE_ENABLE = self.param_inputs.QP_MODE_ENABLE

        if self.isNotNaN(self.param_inputs.QP_CURVE_P1_GEN):
            self.QP_CURVE_P1_GEN = self.param_inputs.QP_CURVE_P1_GEN
        else:
            if self.NP_P_MIN_PU > 0.2:
                self.QP_CURVE_P1_GEN = self.NP_P_MIN_PU
            else:
                self.QP_CURVE_P1_GEN = 0.2
        if self.NP_TYPE == 'PV':
            self.QP_CURVE_Q1_LOAD = self.QP_CURVE_Q1_GEN

        if self.isNotNaN(self.param_inputs.QP_CURVE_P2_GEN):
            self.QP_CURVE_P2_GEN = self.param_inputs.QP_CURVE_P2_GEN
        if self.isNotNaN(self.param_inputs.QP_CURVE_P3_GEN):
            self.QP_CURVE_P3_GEN = self.param_inputs.QP_CURVE_P3_GEN
        if self.isNotNaN(self.param_inputs.QP_CURVE_Q3_GEN):
            self.QP_CURVE_Q3_GEN = self.param_inputs.QP_CURVE_Q3_GEN
        if self.isNotNaN(self.param_inputs.QP_CURVE_Q2_GEN):
            self.QP_CURVE_Q2_GEN = self.param_inputs.QP_CURVE_Q2_GEN
        if self.isNotNaN(self.param_inputs.QP_CURVE_Q1_GEN):
            self.QP_CURVE_Q1_GEN = self.param_inputs.QP_CURVE_Q1_GEN

        if self.isNotNaN(self.param_inputs.QP_CURVE_P1_LOAD):
            self.QP_CURVE_P1_LOAD = self.param_inputs.QP_CURVE_P1_LOAD
        if self.isNotNaN(self.param_inputs.QP_CURVE_P2_LOAD):
            self.QP_CURVE_P2_LOAD = self.param_inputs.QP_CURVE_P2_LOAD
        if self.isNotNaN(self.param_inputs.QP_CURVE_P3_LOAD):
            self.QP_CURVE_P3_LOAD = self.param_inputs.QP_CURVE_P3_LOAD
        if self.isNotNaN(self.param_inputs.QP_CURVE_Q3_LOAD):
            self.QP_CURVE_Q3_LOAD = self.param_inputs.QP_CURVE_Q3_LOAD
        if self.isNotNaN(self.param_inputs.QP_CURVE_Q2_LOAD):
            self.QP_CURVE_Q2_LOAD = self.param_inputs.QP_CURVE_Q2_LOAD
        if self.isNotNaN(self.param_inputs.QP_CURVE_Q1_LOAD):
            self.QP_CURVE_Q1_LOAD = self.param_inputs.QP_CURVE_Q1_LOAD

        if self.isNotNaN(self.param_inputs.PV_MODE_ENABLE):
            self.PV_MODE_ENABLE = self.param_inputs.PV_MODE_ENABLE
        if self.isNotNaN(self.param_inputs.PV_CURVE_V2):
            self.PV_CURVE_V2 = self.param_inputs.PV_CURVE_V2
        if self.isNotNaN(self.param_inputs.PV_CURVE_P2):
            self.PV_CURVE_P2 = self.param_inputs.PV_CURVE_P2
        else:
            if (self.NP_P_MIN_PU > 0.2):
                self.PV_CURVE_P2 = 0.2
            else:
                self.PV_CURVE_P2 = self.NP_P_MIN_PU
        if self.isNotNaN(self.param_inputs.PV_CURVE_V1):
            self.PV_CURVE_V1 = self.param_inputs.PV_CURVE_V1
        if self.isNotNaN(self.param_inputs.PV_CURVE_P1):
            self.PV_CURVE_P1 = self.param_inputs.PV_CURVE_P1
        if self.isNotNaN(self.param_inputs.PV_OLRT):
            self.PV_OLRT = self.param_inputs.PV_OLRT

        if self.NP_ABNORMAL_OP_CAT == "CAT_I":
            self.OV1_TRIP_T = 2
            self.UV1_TRIP_V = 0.7
            self.UV1_TRIP_T = 2
            self.UV2_TRIP_V = 0.45
            self.UV2_TRIP_T = 0.16
            self.MC_LVRT_V1 = 0
            self.MC_HVRT_V1 = 2

        elif self.NP_ABNORMAL_OP_CAT == "CAT_II":
            self.OV1_TRIP_T = 2
            self.UV1_TRIP_V = 0.7
            self.UV1_TRIP_T = 10
            self.UV2_TRIP_V = 0.45
            self.UV2_TRIP_T = 0.16
            self.MC_LVRT_V1 = 0
            self.MC_HVRT_V1 = 2
        else:
            self.OV1_TRIP_T = 13
            self.UV1_TRIP_V = 0.88
            self.UV1_TRIP_T = 21
            self.UV2_TRIP_V = 0.5
            self.UV2_TRIP_T = 2
            self.MC_LVRT_V1 = 0.5
            self.MC_HVRT_V1 = 1.1

        if self.isNotNaN(self.param_inputs.OV2_TRIP_V):
            self.OV2_TRIP_V = self.param_inputs.OV2_TRIP_V
        if self.isNotNaN(self.param_inputs.OV2_TRIP_T):
            self.OV2_TRIP_T = self.param_inputs.OV2_TRIP_T
        if self.isNotNaN(self.param_inputs.OV1_TRIP_V):
            self.OV1_TRIP_V = self.param_inputs.OV1_TRIP_V
        if self.isNotNaN(self.param_inputs.OF2_TRIP_F):
            self.OF2_TRIP_F = self.param_inputs.OF2_TRIP_F
        if self.isNotNaN(self.param_inputs.OF1_TRIP_F):
            self.OF1_TRIP_F = self.param_inputs.OF1_TRIP_F
        if self.isNotNaN(self.param_inputs.OF1_TRIP_T):
            self.OF1_TRIP_T = self.param_inputs.OF1_TRIP_T
        if self.isNotNaN(self.param_inputs.OF2_TRIP_T):
            self.OF2_TRIP_T = self.param_inputs.OF2_TRIP_T
        if self.isNotNaN(self.param_inputs.UF1_TRIP_F):
            self.UF1_TRIP_F = self.param_inputs.UF1_TRIP_F
        if self.isNotNaN(self.param_inputs.UF1_TRIP_T):
            self.UF1_TRIP_T = self.param_inputs.UF1_TRIP_T
        if self.isNotNaN(self.param_inputs.UF2_TRIP_F):
            self.UF2_TRIP_F = self.param_inputs.UF2_TRIP_F
        if self.isNotNaN(self.param_inputs.UF2_TRIP_T):
            self.UF2_TRIP_T = self.param_inputs.UF2_TRIP_T

        if self.isNotNaN(self.param_inputs.OV1_TRIP_T):
            self.OV1_TRIP_T = self.param_inputs.OV1_TRIP_T
        if self.isNotNaN(self.param_inputs.UV1_TRIP_V):
            self.UV1_TRIP_V = self.param_inputs.UV1_TRIP_V
        if self.isNotNaN(self.param_inputs.UV1_TRIP_T):
            self.UV1_TRIP_T = self.param_inputs.UV1_TRIP_T
        if self.isNotNaN(self.param_inputs.UV2_TRIP_V):
            self.UV2_TRIP_V = self.param_inputs.UV2_TRIP_V
        if self.isNotNaN(self.param_inputs.UV2_TRIP_T):
            self.UV2_TRIP_T = self.param_inputs.UV2_TRIP_T

        if self.isNotNaN(self.param_inputs.PF_DBOF):
            self.PF_DBOF = self.param_inputs.PF_DBOF
        if self.isNotNaN(self.param_inputs.PF_DBUF):
            self.PF_DBUF = self.param_inputs.PF_DBUF
        if self.isNotNaN(self.param_inputs.PF_KOF):
            self.PF_KOF = self.param_inputs.PF_KOF
        if self.isNotNaN(self.param_inputs.PF_KUF):
            self.PF_KUF = self.param_inputs.PF_KUF
        if self.isNotNaN(self.param_inputs.PF_OLRT):
            self.PF_OLRT = self.param_inputs.PF_OLRT
        if self.isNotNaN(self.param_inputs.MC_LVRT_V1):
            self.MC_LVRT_V1 = self.param_inputs.MC_LVRT_V1
        if self.isNotNaN(self.param_inputs.MC_HVRT_V1):
            self.MC_HVRT_V1 = self.param_inputs.MC_HVRT_V1



    def _get_parameter_list(self):
        return self.__class__.parameters_list

    def nameplate_value_validity_check(self):
        """
        Validity Check for Nameplate Parameters
        Reference: Section 3.1, part of Table 3-1 in Report #3002025583: IEEE 1547-2018 OpenDER Model
        Other validity checks are performed in variable setters
        """


        if self._NP_VA_MAX is None:
            raise ValueError("DER nameplate apparent power rating NP_VA_MAX needs to be defined!")

        if self._NP_AC_V_NOM is None:
            raise ValueError("DER nameplate voltage rating NP_AC_V_NOM needs to be defined!")

        if self._NP_P_MAX is None:
            logging.error("DER nameplate power rating NP_P_MAX needs to be defined! Using apparent power instead")
            self._NP_P_MAX = self._NP_VA_MAX

        if self._NP_Q_MAX_INJ is None:
            logging.error("DER nameplate reactive power injection rating NP_Q_MAX_INJ needs to be defined! "
                          "Using apparent power instead")
            self._NP_Q_MAX_INJ = self._NP_VA_MAX

        if self._NP_Q_MAX_ABS is None:
            logging.error("DER nameplate reactive power absorption rating NP_Q_MAX_ABS needs to be defined!"
                          " Using apparent power instead")
            self._NP_Q_MAX_ABS = self._NP_VA_MAX

        if self._NP_P_MAX > self._NP_VA_MAX:
            logging.warning("Warning: Please make sure to have DER nameplate active power rating "
                            "less than or equal to DER nameplate apparent power rating.")

        if self._NP_Q_MAX_INJ < (self._NP_VA_MAX * 0.44) or self._NP_Q_MAX_INJ > self._NP_VA_MAX:
            logging.warning("Warning: Regardless DER’s category, its nameplate reactive power injection rating"
                            " should be greater than 44%, and less than 100% of nameplate apparent power rating.")

        if self._NP_P_MAX_CHARGE < self._NP_APPARENT_POWER_CHARGE_MAX:
            logging.warning("Warning: Please make sure to have DER nameplate active power charge rating "
                            "less than or equal to DER nameplate apparent power charge rating.")

        if self._NP_NORMAL_OP_CAT == "CAT_A":
            if self._NP_Q_MAX_ABS < (self._NP_VA_MAX * 0.25) or self._NP_Q_MAX_ABS > self._NP_VA_MAX:
                logging.warning("Warning: For category A DER, its nameplate reactive power absorption rating "
                                "should be greater than 25%, and less than 100% of nameplate apparent power rating.")
        elif self.NP_NORMAL_OP_CAT == "CAT_B":
            if self._NP_Q_MAX_ABS < (self._NP_VA_MAX * 0.44) or self._NP_Q_MAX_ABS > self._NP_VA_MAX:
                logging.warning("Warning: For category B DER, its nameplate reactive power absorption rating "
                                "should be greater than 44%, and less than 100% of nameplate apparent power rating.")


    def check_enabled(self, value):
        """
        Change ENABLED and DISABLED to bool True and False.

        Parameters
        ----------
        value: str, Value with ENABLED or DISABLED

        Returns
        -------
        : bool, True or False

        """
        if type(value) is bool:
            return value
        elif value == "ENABLED" or value == "ENABLE" or value == "enabled" or value == "enable":
            return True
        elif value == "DISABLED" or value == "DISABLE" or value == "disabled" or value == "disable":
            return False
        else:
            logging.warning(f"Issue with ENABLED and DISABLED values: {value}")

    def isNotNaN(self, param):
        # if param is NaN (Not a number), Python considers param != param. This function checks whether param is valid.
        return (param == param) and (param is not None)

    def initialize_NP_Q_CAPABILTY_BY_P_CURVE(self):
        """
        Initialize nameplate reactive power capability curve using 4 array inputs of P_Q_ABS_PU, Q_MAX_ABS_PU,
        P_Q_INJ_PU, Q_MAX_INJ_PU
        """
        if self.isNotNaN(self.P_Q_ABS_PU) and self.isNotNaN(self.P_Q_INJ_PU) \
                and self.isNotNaN(self.Q_MAX_ABS_PU) and self.isNotNaN(self.Q_MAX_INJ_PU):
            self.NP_Q_CAPABILITY_BY_P_CURVE = {
                'P_Q_ABS_PU': [float(x) for x in self.P_Q_ABS_PU.split(' ')],
                'Q_MAX_ABS_PU': [float(x) for x in self.Q_MAX_ABS_PU.split(' ')],
                'P_Q_INJ_PU': [float(x) for x in self.P_Q_INJ_PU.split(' ')],
                'Q_MAX_INJ_PU': [float(x) for x in self.Q_MAX_INJ_PU.split(' ')],
            }
            if self.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_ABS_PU'][0] > -1:
                self.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_ABS_PU'].insert(0, -1)
                self.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_ABS_PU'].\
                    insert(0,self.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_ABS_PU'][0])
            if self.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_INJ_PU'][0] > -1:
                self.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_INJ_PU'].insert(0, -1)
                self.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_INJ_PU'].\
                    insert(0,self.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_INJ_PU'][0])

            if self.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_ABS_PU'][-1] < 1:
                self.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_ABS_PU'].append(1)
                self.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_ABS_PU'].append(
                    self.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_ABS_PU'][-1])
            if self.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_INJ_PU'][-1] < 1:
                self.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_INJ_PU'].append(1)
                self.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_INJ_PU'].append(
                    self.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_INJ_PU'][-1])
        else:
            q_max_inj_pu = self.NP_Q_MAX_INJ / self.NP_VA_MAX
            q_max_abs_pu = self.NP_Q_MAX_ABS / self.NP_VA_MAX

            if self.NP_Q_CAPABILITY_LOW_P == 'REDUCED':
                self.NP_Q_CAPABILITY_BY_P_CURVE = {
                    'P_Q_INJ_PU': [0, 0.04999, 0.05, 0.2, 1],
                    'P_Q_ABS_PU': [0, 0.04999, 0.05, 0.2, 1],
                    'Q_MAX_INJ_PU': [0, 0, q_max_inj_pu / 4, q_max_inj_pu, q_max_inj_pu],
                    'Q_MAX_ABS_PU': [0, 0, q_max_abs_pu / 4, q_max_abs_pu, q_max_abs_pu]
                }
            else:
                self.NP_Q_CAPABILITY_BY_P_CURVE = {
                    'P_Q_INJ_PU': [-1, 1],
                    'P_Q_ABS_PU': [-1, 1],
                    'Q_MAX_INJ_PU': [q_max_inj_pu, q_max_inj_pu],
                    'Q_MAX_ABS_PU': [q_max_abs_pu, q_max_abs_pu]
                }

        if (len(self.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_INJ_PU']) !=
           len(self.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_INJ_PU'])) or \
           (len(self.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_ABS_PU']) !=
           len(self.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_ABS_PU'])):
            raise ValueError("ValueError: Check failed for reactive power curve NP_Q_CAPABILITY_BY_P_CURVE, please"
                             "make sure all four arrays have the same length")

        if not self.der_q_capability_validity_check(self.NP_Q_CAPABILITY_BY_P_CURVE, self.NP_NORMAL_OP_CAT):
            logging.warning("Warning: DER reactive capability curve defined by NP_Q_CAPABILITY_BY_P_CURVE "
                            "should be greater than the range defined in IEEE 1547-2018 Clause 5.2")



    def der_q_capability_validity_check(self, NP_Q_CAPABILITY_BY_P_CURVE, NP_NORMAL_OP_CAT):
        """
        Check if the DER reactive power capability custom curve is greater than the requirement

        Variable used in this function:
        :NP_Q_CAPABILITY_BY_P_CURVE: User defined reactive power capability curve
        :NP_NORMAL_OP_CAT: DER normal operating performance category

        Internal variables:
        :p_capability_pu, q_capability_pu: DER Q capability curve in terms of P, user custom defined
        :p_requirement_pu, q_requirement_pu: Minimum Q capability in terms of P, defined by IEEE 1547-2018

        return: True: custom capability curve greater than the requirement
        """

        p_requirement_pu = [0, 0.0499999999, 0.05, 0.2, 1]
        q_requirement_pu = [0, 0, 0.11, 0.44, 0.44]
        p_capability_pu = NP_Q_CAPABILITY_BY_P_CURVE['P_Q_INJ_PU']
        q_capability_pu = NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_INJ_PU']

        for i in range(len(p_capability_pu)):
            if q_capability_pu[i] < np.interp(p_capability_pu[i], p_requirement_pu, q_requirement_pu):
                return False

        if NP_NORMAL_OP_CAT == 'CAT_A':
            p_requirement_pu = [0, 0.0499999999, 0.05, 0.2, 1]
            q_requirement_pu = [0, 0, 0.11, 0.44, 0.44]
        else:
            p_requirement_pu = [0, 0.0499999999, 0.05, 0.2, 1]
            q_requirement_pu = [0, 0, 0.0625, 0.25, 0.25]

        p_capability_pu = NP_Q_CAPABILITY_BY_P_CURVE['P_Q_ABS_PU']
        q_capability_pu = NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_ABS_PU']

        for i in range(len(p_capability_pu)):
            if q_capability_pu[i] < np.interp(p_capability_pu[i], p_requirement_pu, q_requirement_pu):
                return False

        return True


    @property
    def NP_NORMAL_OP_CAT(self):
        return self._NP_NORMAL_OP_CAT

    @NP_NORMAL_OP_CAT.setter
    def NP_NORMAL_OP_CAT(self, NP_NORMAL_OP_CAT):
        if NP_NORMAL_OP_CAT.upper() == 'CAT_A' or NP_NORMAL_OP_CAT.upper() == 'CAT_B':
            self._NP_NORMAL_OP_CAT = NP_NORMAL_OP_CAT.upper()
        else:
            logging.error("Error: Value of NP_NORMAL_OP_CAT should be either CAT_A or CAT_B, CAT_B is used by default")
            self._NP_NORMAL_OP_CAT = 'CAT_B'

    @property
    def NP_ABNORMAL_OP_CAT(self):
        return self._NP_ABNORMAL_OP_CAT

    @NP_ABNORMAL_OP_CAT.setter
    def NP_ABNORMAL_OP_CAT(self, NP_ABNORMAL_OP_CAT):
        if NP_ABNORMAL_OP_CAT.upper() == 'CAT_I' or NP_ABNORMAL_OP_CAT.upper() == 'CAT_II' \
                or NP_ABNORMAL_OP_CAT.upper() == 'CAT_III':
            self._NP_ABNORMAL_OP_CAT = NP_ABNORMAL_OP_CAT
        else:
            logging.error("Error: Value of NP_ABNORMAL_OP_CAT should be CAT_I, CAT_II"
                          " or CAT_III, CAT_III is used by default")
            self._NP_NORMAL_OP_CAT = 'CAT_III'

    @property
    def NP_P_MAX(self) -> float:
        return self._NP_P_MAX

    @NP_P_MAX.setter
    def NP_P_MAX(self, NP_P_MAX):
        self._NP_P_MAX = NP_P_MAX
        if self._NP_P_MAX <= 0:
            raise ValueError("DER nameplate power NP_P_MAX should be greater than 0")

    @property
    def NP_P_MAX_OVER_PF(self):
        return self._NP_P_MAX_OVER_PF

    @NP_P_MAX_OVER_PF.setter
    def NP_P_MAX_OVER_PF(self, NP_P_MAX_OVER_PF):
        self._NP_P_MAX_OVER_PF = NP_P_MAX_OVER_PF


    @property
    def NP_OVER_PF(self):
        return self._NP_OVER_PF

    @NP_OVER_PF.setter
    def NP_OVER_PF(self, NP_OVER_PF):
        self._NP_OVER_PF = NP_OVER_PF
        if self._NP_OVER_PF < 0 or self._NP_OVER_PF > 1:
            logging.warning("Warning: By definition, power factor NP_OVER_PF cannot be greater than 1 or less than 0.")

    @property
    def NP_P_MAX_UNDER_PF(self):
        return self._NP_P_MAX_UNDER_PF

    @NP_P_MAX_UNDER_PF.setter
    def NP_P_MAX_UNDER_PF(self, NP_P_MAX_UNDER_PF):
        self._NP_P_MAX_UNDER_PF = NP_P_MAX_UNDER_PF

    @property
    def NP_UNDER_PF(self):
        return self._NP_UNDER_PF

    @NP_UNDER_PF.setter
    def NP_UNDER_PF(self, NP_UNDER_PF):
        self._NP_UNDER_PF = NP_UNDER_PF
        if self._NP_UNDER_PF < 0 or self._NP_UNDER_PF > 1:
            logging.warning("Warning: By definition, power factor NP_UNDER_PF cannot be greater than 1 or less than 0.")

    @property
    def NP_VA_MAX(self):
        return self._NP_VA_MAX

    @NP_VA_MAX.setter
    def NP_VA_MAX(self, NP_VA_MAX):
        self._NP_VA_MAX = NP_VA_MAX
        if self._NP_VA_MAX <= 0:
            raise ValueError("DER nameplate apparent power rating NP_VA_MAX should be greater than 0")

    @property
    def NP_Q_MAX_INJ(self):
        return self._NP_Q_MAX_INJ

    @NP_Q_MAX_INJ.setter
    def NP_Q_MAX_INJ(self, NP_Q_MAX_INJ):
        self._NP_Q_MAX_INJ = NP_Q_MAX_INJ
        if self._NP_Q_MAX_INJ <= 0:
            raise ValueError("DER nameplate reactive power injection rating NP_Q_MAX_INJ should be greater than 0")

    @property
    def NP_Q_MAX_ABS(self):
        return self._NP_Q_MAX_ABS

    @NP_Q_MAX_ABS.setter
    def NP_Q_MAX_ABS(self, NP_Q_MAX_ABS):
        self._NP_Q_MAX_ABS = NP_Q_MAX_ABS
        if self._NP_Q_MAX_INJ <= 0:
            raise ValueError("DER nameplate reactive power absorption rating NP_Q_MAX_ABS should be greater than 0")

    @property
    def NP_P_MAX_CHARGE(self):
        return self._NP_P_MAX_CHARGE

    @NP_P_MAX_CHARGE.setter
    def NP_P_MAX_CHARGE(self, NP_P_MAX_CHARGE):
        self._NP_P_MAX_CHARGE = NP_P_MAX_CHARGE
        if self._NP_P_MAX_CHARGE <= 0:
            logging.error("DER nameplate power for charging NP_P_MAX_CHARGE should be greater than 0, "
                          "converting to positive")
            self._NP_P_MAX_CHARGE = - self._NP_P_MAX_CHARGE

    @property
    def NP_APPARENT_POWER_CHARGE_MAX(self):
        return self._NP_APPARENT_POWER_CHARGE_MAX

    @NP_APPARENT_POWER_CHARGE_MAX.setter
    def NP_APPARENT_POWER_CHARGE_MAX(self, NP_APPARENT_POWER_CHARGE_MAX):
        self._NP_APPARENT_POWER_CHARGE_MAX = NP_APPARENT_POWER_CHARGE_MAX
        if self._NP_APPARENT_POWER_CHARGE_MAX <= 0:
            logging.error("DER nameplate apparent power for charging NP_APPARENT_POWER_CHARGE_MAX should be "
                          "greater than 0, converting to positive")
            self._NP_APPARENT_POWER_CHARGE_MAX = - self._NP_APPARENT_POWER_CHARGE_MAX

    @property
    def NP_AC_V_NOM(self):
        return self._NP_AC_V_NOM

    @NP_AC_V_NOM.setter
    def NP_AC_V_NOM(self, NP_AC_V_NOM):
        self._NP_AC_V_NOM = NP_AC_V_NOM
        if self._NP_AC_V_NOM < 0:
            raise ValueError("ValueError: DER nameplate voltage NP_AC_V_NOM should be greater than 0.")
        if self._NP_AC_V_NOM * 1.414 > self._NP_V_DC:
            self._NP_V_DC = self._NP_AC_V_NOM * 1.5
            logging.warning("DER inverter DC voltage should be greater than system line to line voltage peak")

    @property
    def NP_REACTIVE_SUSCEPTANCE(self):
        return self._NP_REACTIVE_SUSCEPTANCE

    @NP_REACTIVE_SUSCEPTANCE.setter
    def NP_REACTIVE_SUSCEPTANCE(self, NP_REACTIVE_SUSCEPTANCE):
        self._NP_REACTIVE_SUSCEPTANCE = NP_REACTIVE_SUSCEPTANCE

    @property
    def NP_P_MIN_PU(self):
        return self._NP_P_MIN_PU

    @NP_P_MIN_PU.setter
    def NP_P_MIN_PU(self, NP_P_MIN_PU):
        self._NP_P_MIN_PU = NP_P_MIN_PU
        if self._NP_P_MIN_PU > 1 or self._NP_P_MIN_PU < 0 :
            logging.error("Error: DER minimum active power in per unit should be greater or equal to 0 and less than 1")

    @property
    def NP_PHASE(self):
        return self._NP_PHASE

    @NP_PHASE.setter
    def NP_PHASE(self, NP_PHASE):
        if isinstance(NP_PHASE, str):
            if NP_PHASE.upper() == 'SINGLE' or NP_PHASE.upper() == 'THREE':
                self._NP_PHASE = NP_PHASE.upper()
            else:
                raise ValueError("NP_PHASE should be either 'SINGLE' or 'THREE'")
        else:
            raise ValueError("NP_PHASE should be either 'SINGLE' or 'THREE'")

    @property
    def NP_TYPE(self):
        return self._NP_TYPE

    @NP_TYPE.setter
    def NP_TYPE(self, NP_TYPE):
        if isinstance(NP_TYPE, str):
            if NP_TYPE.upper() == 'PV' or NP_TYPE.upper() == 'BESS':
                self._NP_PHASE = NP_TYPE.upper()
            else:
                raise ValueError("NP_TYPE should be either 'PV' or 'BESS'")
        else:
            raise ValueError("NP_TYPE should be either 'BESS' or 'BESS'")

    @property
    def NP_SET_EXE_TIME(self):
        return self._NP_SET_EXE_TIME

    @NP_SET_EXE_TIME.setter
    def NP_SET_EXE_TIME(self, NP_SET_EXE_TIME):
        self._NP_SET_EXE_TIME = NP_SET_EXE_TIME
        if self._NP_SET_EXE_TIME < 0 or self._NP_SET_EXE_TIME > 30:
            logging.warning("Warning: Mode and setting change execution delay time should be greater than or equal to"
                            " 0, and smaller than or equal to 30 seconds, according to IEEE 1547-2018 Clause 4.6.3.")

    @property
    def NP_MODE_TRANSITION_TIME(self):
        return self._NP_MODE_TRANSITION_TIME

    @NP_MODE_TRANSITION_TIME.setter
    def NP_MODE_TRANSITION_TIME(self, NP_MODE_TRANSITION_TIME):
        self._NP_MODE_TRANSITION_TIME = NP_MODE_TRANSITION_TIME
        if self._NP_MODE_TRANSITION_TIME < 5 or self._NP_MODE_TRANSITION_TIME > 300:
            logging.warning("Warning: Time for DER to smoothly transition between reactive power support modes should"
                            " be greater than or equal to 5 seconds, and smaller than or equal to 300 seconds, "
                            "according to IEEE 1547-2018 Clause 4.6.3.")

    @property
    def NP_V_DC(self):
        return self._NP_V_DC

    @NP_V_DC.setter
    def NP_V_DC(self, NP_V_DC):
        self._NP_V_DC = NP_V_DC

    @property
    def ES_RANDOMIZED_DELAY_ACTUAL(self):
        return self._ES_RANDOMIZED_DELAY_ACTUAL

    @ES_RANDOMIZED_DELAY_ACTUAL.setter
    def ES_RANDOMIZED_DELAY_ACTUAL(self, ES_RANDOMIZED_DELAY_ACTUAL):
        self._ES_RANDOMIZED_DELAY_ACTUAL = ES_RANDOMIZED_DELAY_ACTUAL

    @property
    def AP_LIMIT_ENABLE(self):
        return self._AP_LIMIT_ENABLE

    @AP_LIMIT_ENABLE.setter
    def AP_LIMIT_ENABLE(self, AP_LIMIT_ENABLE):
        self._AP_LIMIT_ENABLE = self.check_enabled(AP_LIMIT_ENABLE)

    @property
    def AP_LIMIT(self):
        return self._AP_LIMIT

    @AP_LIMIT.setter
    def AP_LIMIT(self, AP_LIMIT):
        self._AP_LIMIT = AP_LIMIT
        if self._AP_LIMIT < -1 or self._AP_LIMIT > 1:
            logging.warning("Warning: Active power limit signal AP_LIMIT should be within -1 to 1")

    @property
    def CONST_PF_RT(self):
        return self._CONST_PF_RT

    @CONST_PF_RT.setter
    def CONST_PF_RT(self, CONST_PF_RT):
        self._CONST_PF_RT = CONST_PF_RT
        if self.CONST_PF_RT < 0 or self.CONST_PF_RT > 10:
            logging.warning("Warning: Constant power factor function response time should be greater than or equal to"
                            " 0, and smaller than or equal to 10 seconds, according to IEEE 1547-2018 Clause 5.3.2.")

    @property
    def CONST_Q_RT(self):
        return self._CONST_Q_RT

    @CONST_Q_RT.setter
    def CONST_Q_RT(self, CONST_Q_RT):
        self._CONST_Q_RT = CONST_Q_RT
        if (self._CONST_Q_RT < 0 or self._CONST_Q_RT > 10):
            logging.warning("Warning: Constant reactive power function response time should be greater than or equal "
                            "to 0, and smaller than or equal to 10 seconds, according to IEEE 1547-2018 Clause 5.3.5.")

    @property
    def ES_PERMIT_SERVICE(self):
        return self._ES_PERMIT_SERVICE

    @ES_PERMIT_SERVICE.setter
    def ES_PERMIT_SERVICE(self, ES_PERMIT_SERVICE):
        self._ES_PERMIT_SERVICE = self.check_enabled(ES_PERMIT_SERVICE)

    @property
    def ES_V_LOW(self):
        return self._ES_V_LOW

    @ES_V_LOW.setter
    def ES_V_LOW(self, ES_V_LOW):
        self._ES_V_LOW = ES_V_LOW
        if self._ES_V_LOW < 0.88 or self._ES_V_LOW > 0.95:
            logging.warning("Warning: check failed for ES_V_LOW. Minimum and maximum applicable voltage for enter"
                            " service criteria should be within the ranges defined in IEEE 1547-2018 Clause 4.10.2")

    @property
    def ES_V_HIGH(self):
        return self._ES_V_HIGH

    @ES_V_HIGH.setter
    def ES_V_HIGH(self, ES_V_HIGH):
        self._ES_V_HIGH = ES_V_HIGH
        if self._ES_V_HIGH < 1.05 or self._ES_V_HIGH > 1.06:
            logging.warning("Warning: check failed for ES_V_HIGH. Minimum and maximum applicable voltage for enter"
                            " service criteria should be within the ranges defined in IEEE 1547-2018 Clause 4.10.2")

    @property
    def ES_F_LOW(self):
        return self._ES_F_LOW

    @ES_F_LOW.setter
    def ES_F_LOW(self, ES_F_LOW):
        self._ES_F_LOW = ES_F_LOW
        if self._ES_F_LOW < 59.0 or self._ES_F_LOW > 59.9:
            logging.warning("Warning: check failed for ES_F_LOW. Minimum and maximum applicable frequency for enter"
                            " service criteria should be within the ranges defined in IEEE 1547-2018 Clause 4.10.2")

    @property
    def ES_F_HIGH(self):
        return self._ES_F_HIGH

    @ES_F_HIGH.setter
    def ES_F_HIGH(self, ES_F_HIGH):
        self._ES_F_HIGH = ES_F_HIGH
        if self._ES_F_HIGH < 60.1 or self._ES_F_HIGH > 61:
            logging.warning("Warning: check failed for ES_F_HIGH. Minimum and maximum applicable frequency for enter"
                            " service criteria should be within the ranges defined in IEEE 1547-2018 Clause 4.10.2")

    @property
    def ES_DELAY(self):
        return self._ES_DELAY

    @ES_DELAY.setter
    def ES_DELAY(self, ES_DELAY):
        self._ES_DELAY = ES_DELAY
        if self._ES_DELAY < 0 or self._ES_DELAY > 600:
            logging.warning("Warning: check failed for ES_DELAY. Minimum intentional delay before initiating "
                            "softstart should be greater than or equal to 0, and smaller than or equal to 600 s,"
                            " according to IEEE 1547-2018 Clause 4.10.3")

    @property
    def ES_RANDOMIZED_DELAY(self):
        return self._ES_RANDOMIZED_DELAY

    @ES_RANDOMIZED_DELAY.setter
    def ES_RANDOMIZED_DELAY(self, ES_RANDOMIZED_DELAY):
        self._ES_RANDOMIZED_DELAY = ES_RANDOMIZED_DELAY
        if self._ES_RANDOMIZED_DELAY != 0:
            if (self._NP_VA_MAX > 500e3) or (self._ES_RANDOMIZED_DELAY < 0 or self._ES_RANDOMIZED_DELAY > 1000):
                logging.warning("Warning: check failed for ES_RANDOMIZED_DELAY. If enabled, maximum time for enter "
                                "service randomized delay should be greater than or equal to 1, and smaller than or "
                                "equal to 1000 s, according to IEEE 1547-2018 Clause 4.10.3. "
                                "Randomized delay is only applicable for DERs less than 500kVA")

        if self._ES_RANDOMIZED_DELAY != 0 and self._ES_RAMP_RATE != 0:
            logging.warning("Warning: Enter service randomized delay and ramp are mutually exclusive. "
                            "They cannot be enabled together")


    @property
    def ES_RAMP_RATE(self):
        return self._ES_RAMP_RATE

    @ES_RAMP_RATE.setter
    def ES_RAMP_RATE(self, ES_RAMP_RATE):
        self._ES_RAMP_RATE = ES_RAMP_RATE
        if self._ES_RAMP_RATE != 0:
            if self._ES_RAMP_RATE < 1 or self._ES_RAMP_RATE > 1000:
                logging.warning("Warning: Enter service soft-start duration should be greater than or equal to 1 s, "
                                "and smaller than or equal to 1000 s, according to IEEE 1547-2018 Clause 4.10.3")

        if self._ES_RANDOMIZED_DELAY != 0 and self._ES_RAMP_RATE != 0:
            logging.warning("Warning: Enter service randomized delay and ramp are mutually exclusive. "
                            "They cannot be enabled together")

    @property
    def CONST_PF_MODE_ENABLE(self):
        return self._CONST_PF_MODE_ENABLE

    @CONST_PF_MODE_ENABLE.setter
    def CONST_PF_MODE_ENABLE(self, CONST_PF_MODE_ENABLE):
        self._CONST_PF_MODE_ENABLE = self.check_enabled(CONST_PF_MODE_ENABLE)
        if self._CONST_PF_MODE_ENABLE:
            if any([self.QV_MODE_ENABLE, self.QP_MODE_ENABLE, self.CONST_Q_MODE_ENABLE]):
                self.QV_MODE_ENABLE, self.QP_MODE_ENABLE, self.CONST_Q_MODE_ENABLE = False, False, False
                logging.info("Only one of the four reactive power control modes (constant reactive power, constant "
                             "power factor, volt-var, and watt-var) can be enabled at a time, disabling the other "
                             "function")


    @property
    def CONST_PF_EXCITATION(self):
        return self._CONST_PF_EXCITATION

    @CONST_PF_EXCITATION.setter
    def CONST_PF_EXCITATION(self, CONST_PF_EXCITATION):
        if isinstance(CONST_PF_EXCITATION, str):
            if CONST_PF_EXCITATION.upper() == 'INJ' or CONST_PF_EXCITATION.upper() == 'ABS':
                self._CONST_PF_EXCITATION = CONST_PF_EXCITATION.upper()
            else:
                logging.error("CONST_PF_EXCITATION should be either 'INJ' or 'ABS'")
        else:
            logging.error("CONST_PF_EXCITATION should be either 'INJ' or 'ABS'")

    @property
    def CONST_PF(self):
        return self._CONST_PF

    @CONST_PF.setter
    def CONST_PF(self, CONST_PF):
        if CONST_PF < 0:
            raise ValueError("ValueError: CONST_PF must be positive")
        if CONST_PF > 1:
            raise ValueError("ValueError: CONST_PF must be less or equal to 1")
        self._CONST_PF = CONST_PF

    @property
    def CONST_Q_MODE_ENABLE(self):
        return self._CONST_Q_MODE_ENABLE

    @CONST_Q_MODE_ENABLE.setter
    def CONST_Q_MODE_ENABLE(self, CONST_Q_MODE_ENABLE):
        self._CONST_Q_MODE_ENABLE = self.check_enabled(CONST_Q_MODE_ENABLE)
        if self._CONST_Q_MODE_ENABLE:
            if any([self.QV_MODE_ENABLE, self.QP_MODE_ENABLE, self.CONST_PF_MODE_ENABLE]):
                self.QV_MODE_ENABLE, self.QP_MODE_ENABLE, self.CONST_PF_MODE_ENABLE = False, False, False
                logging.info("Only one of the four reactive power control modes (constant reactive power, constant "
                             "power factor, volt-var, and watt-var) can be enabled at a time, disabling the other "
                             "function")

    @property
    def CONST_Q(self):
        return self._CONST_Q

    @CONST_Q.setter
    def CONST_Q(self, CONST_Q):
        self._CONST_Q = CONST_Q
        if (self.CONST_Q < (-self.NP_Q_MAX_ABS / self.NP_VA_MAX) or self.CONST_Q > (
                self.NP_Q_MAX_INJ / self.NP_VA_MAX)):
            logging.warning("Warning: Constant reactive power function setpoint uses DER nameplate apparent power "
                            "rating as base. It should be within its nameplate reactive power injection and "
                            "absorption ratings.")

    @property
    def P_Q_INJ_PU(self):
        return self._P_Q_INJ_PU

    @P_Q_INJ_PU.setter
    def P_Q_INJ_PU(self, P_Q_INJ_PU):
        self._P_Q_INJ_PU = P_Q_INJ_PU

    @property
    def P_Q_ABS_PU(self):
        return self._P_Q_ABS_PU

    @P_Q_ABS_PU.setter
    def P_Q_ABS_PU(self, P_Q_ABS_PU):
        self._P_Q_ABS_PU = P_Q_ABS_PU

    @property
    def Q_MAX_INJ_PU(self):
        return self._Q_MAX_INJ_PU

    @Q_MAX_INJ_PU.setter
    def Q_MAX_INJ_PU(self, Q_MAX_INJ_PU):
        self._Q_MAX_INJ_PU = Q_MAX_INJ_PU

    @property
    def Q_MAX_ABS_PU(self):
        return self._Q_MAX_ABS_PU

    @Q_MAX_ABS_PU.setter
    def Q_MAX_ABS_PU(self, Q_MAX_ABS_PU):
        self._Q_MAX_ABS_PU = Q_MAX_ABS_PU

    @property
    def QV_MODE_ENABLE(self):
        return self._QV_MODE_ENABLE

    @QV_MODE_ENABLE.setter
    def QV_MODE_ENABLE(self, QV_MODE_ENABLE):
        self._QV_MODE_ENABLE = self.check_enabled(QV_MODE_ENABLE)
        if self._QV_MODE_ENABLE:
            if any([self.CONST_Q_MODE_ENABLE, self.QP_MODE_ENABLE, self.CONST_PF_MODE_ENABLE]):
                self.CONST_Q_MODE_ENABLE, self.QP_MODE_ENABLE, self.CONST_PF_MODE_ENABLE = False, False, False
                logging.info("Only one of the four reactive power control modes (constant reactive power, constant "
                             "power factor, volt-var, and watt-var) can be enabled at a time, disabling the other "
                             "function")

    @property
    def QV_VREF(self):
        return self._QV_VREF

    @QV_VREF.setter
    def QV_VREF(self, QV_VREF):
        self._QV_VREF = QV_VREF
        if self._QV_VREF < 0.95 or self._QV_VREF > 1.05:
            logging.warning("Warning: V/Q Curve VRef Setting should be greater than or equal to 0.95, and smaller "
                            "than or equal to 1.05 per unit, according to IEEE 1547-2018 Clause 5.3.3")

    @property
    def QV_VREF_AUTO_MODE(self):
        return self._QV_VREF_AUTO_MODE

    @QV_VREF_AUTO_MODE.setter
    def QV_VREF_AUTO_MODE(self, QV_VREF_AUTO_MODE):
        self._QV_VREF_AUTO_MODE = self.check_enabled(QV_VREF_AUTO_MODE)

    @property
    def QV_VREF_TIME(self):
        return self._QV_VREF_TIME

    @QV_VREF_TIME.setter
    def QV_VREF_TIME(self, QV_VREF_TIME):
        self._QV_VREF_TIME = QV_VREF_TIME
        if self._QV_VREF_TIME < 300 or self._QV_VREF_TIME > 5000:
            logging.warning("Warning: Vref adjustment time constant should be greater than or equal to 300, and "
                            "smaller than or equal to 5000 s, according to IEEE 1547-2018 Clause 5.3.3")

    @property
    def QV_CURVE_V2(self):
        return self._QV_CURVE_V2

    @QV_CURVE_V2.setter
    def QV_CURVE_V2(self, QV_CURVE_V2):
        self._QV_CURVE_V2 = QV_CURVE_V2
        if self._QV_CURVE_V2 < (self._QV_VREF - 0.03) or self._QV_CURVE_V2 > self._QV_VREF:
            logging.warning("Warning: check failed for QV_CURVE_V2. For the piecewise linear curve setting of "
                            "volt-var control, the four corner points should have their voltage settings "
                            "monotonically increasing and within the ranges defined in IEEE 1547-2018 Clause 5.3.3")

    @property
    def QV_CURVE_Q2(self):
        return self._QV_CURVE_Q2

    @QV_CURVE_Q2.setter
    def QV_CURVE_Q2(self, QV_CURVE_Q2):
        self._QV_CURVE_Q2 = QV_CURVE_Q2
        if (self.QV_CURVE_Q2 < (-self.NP_Q_MAX_ABS / self.NP_VA_MAX) or self.QV_CURVE_Q2 > (
                self.NP_Q_MAX_INJ / self.NP_VA_MAX)):
            logging.warning("Warning: check failed for QV_CURVE_Q2. Volt-var function reactive power setpoints use "
                            "DER nameplate apparent power rating as base. The setpoints should be within its "
                            "nameplate reactive power injection and absorption ratings, and the ranges defined "
                            "in IEEE 1547-2018 Clause 5.3.3.")

    @property
    def QV_CURVE_V3(self):
        return self._QV_CURVE_V3

    @QV_CURVE_V3.setter
    def QV_CURVE_V3(self, QV_CURVE_V3):
        self._QV_CURVE_V3 = QV_CURVE_V3
        if self.QV_CURVE_V3 < self.QV_VREF or self.QV_CURVE_V3 > (self.QV_VREF + 0.03):
            logging.warning("Warning: check failed for QV_CURVE_V3. For the piecewise linear curve setting of "
                            "volt-var control, the four corner points should have their voltage settings "
                            "monotonically increasing and within the ranges defined in IEEE 1547-2018 Clause 5.3.3")

    @property
    def QV_CURVE_Q3(self):
        return self._QV_CURVE_Q3

    @QV_CURVE_Q3.setter
    def QV_CURVE_Q3(self, QV_CURVE_Q3):
        self._QV_CURVE_Q3 = QV_CURVE_Q3
        if (self.QV_CURVE_Q3 < (-self.NP_Q_MAX_ABS / self.NP_VA_MAX) or self.QV_CURVE_Q3 > (
                self.NP_Q_MAX_INJ / self.NP_VA_MAX)):
            logging.warning("Warning: check failed for QV_CURVE_Q3. Volt-var function reactive power setpoints"
                            " use DER nameplate apparent power rating as base. The setpoints should be within "
                            "its nameplate reactive power injection and absorption ratings, and the ranges defined "
                            "in IEEE 1547-2018 Clause 5.3.3.")

    @property
    def QV_CURVE_V1(self):
        return self._QV_CURVE_V1

    @QV_CURVE_V1.setter
    def QV_CURVE_V1(self, QV_CURVE_V1):
        self._QV_CURVE_V1 = QV_CURVE_V1
        if self.QV_CURVE_V1 < (self.QV_VREF - 0.18) or self.QV_CURVE_V1 > (self.QV_CURVE_V2 - 0.02):
            logging.warning("Warning: check failed for QV_CURVE_V1. For the piecewise linear curve setting of "
                            "volt-var control, the four corner points should have their voltage settings "
                            "monotonically increasing and within the ranges defined in IEEE 1547-2018 Clause 5.3.3")

    @property
    def QV_CURVE_Q1(self):
        return self._QV_CURVE_Q1

    @QV_CURVE_Q1.setter
    def QV_CURVE_Q1(self, QV_CURVE_Q1):
        self._QV_CURVE_Q1 = QV_CURVE_Q1
        if self.QV_CURVE_Q1 < 0 or self.QV_CURVE_Q1 > (self.NP_Q_MAX_INJ / self.NP_VA_MAX):
            logging.warning("Warning: check failed for QV_CURVE_Q1. Volt-var function reactive power setpoints"
                            " use DER nameplate apparent power rating as base. The setpoints should be within "
                            "its nameplate reactive power injection and absorption ratings, and the ranges defined"
                            " in IEEE 1547-2018 Clause 5.3.3.")

    @property
    def QV_CURVE_V4(self):
        return self._QV_CURVE_V4

    @QV_CURVE_V4.setter
    def QV_CURVE_V4(self, QV_CURVE_V4):
        self._QV_CURVE_V4 = QV_CURVE_V4
        if self.QV_CURVE_V4 < (self.QV_CURVE_V3 + 0.02) or self.QV_CURVE_V3 > (self.QV_VREF + 0.18):
            logging.warning("Warning: check failed for QV_CURVE_V4. For the piecewise linear curve setting of "
                            "volt-var control, the four corner points should have their voltage settings "
                            "monotonically increasing and within the ranges defined in IEEE 1547-2018 Clause 5.3.3")

    @property
    def QV_CURVE_Q4(self):
        return self._QV_CURVE_Q4

    @QV_CURVE_Q4.setter
    def QV_CURVE_Q4(self, QV_CURVE_Q4):
        self._QV_CURVE_Q4 = QV_CURVE_Q4
        if self.QV_CURVE_Q4 < (-self.NP_Q_MAX_ABS / self.NP_VA_MAX) or self.QV_CURVE_Q4 > 0:
            logging.warning("Warning: check failed for QV_CURVE_Q4. Volt-var function reactive power setpoints use "
                            "DER nameplate apparent power rating as base. The setpoints should be within its "
                            "nameplate reactive power injection and absorption ratings, and the ranges defined in "
                            "IEEE 1547-2018 Clause 5.3.3.")

    @property
    def QV_OLRT(self):
        return self._QV_OLRT

    @QV_OLRT.setter
    def QV_OLRT(self, QV_OLRT):
        self._QV_OLRT = QV_OLRT
        if self.QV_OLRT < 1 or self.QV_OLRT > 90:
            logging.warning("Warning: Volt-var function open loop response time should be within the range defined "
                            "in IEEE 1547-2018 Clause 5.3.3")

    @property
    def QP_MODE_ENABLE(self):
        return self._QP_MODE_ENABLE

    @QP_MODE_ENABLE.setter
    def QP_MODE_ENABLE(self, QP_MODE_ENABLE):
        self._QP_MODE_ENABLE = self.check_enabled(QP_MODE_ENABLE)
        if self._QP_MODE_ENABLE:
            if any([self.CONST_Q_MODE_ENABLE, self.QV_MODE_ENABLE, self.CONST_PF_MODE_ENABLE]):
                self.CONST_Q_MODE_ENABLE, self.QV_MODE_ENABLE, self.CONST_PF_MODE_ENABLE = False, False, False
                logging.info("Only one of the four reactive power control modes (constant reactive power, constant "
                             "power factor, volt-var, and watt-var) can be enabled at a time, disabling the other "
                             "function")


    @property
    def QP_CURVE_P3_GEN(self):
        return self._QP_CURVE_P3_GEN

    @QP_CURVE_P3_GEN.setter
    def QP_CURVE_P3_GEN(self, QP_CURVE_P3_GEN):
        self._QP_CURVE_P3_GEN = QP_CURVE_P3_GEN
        if self.QP_CURVE_P3_GEN < (self.QP_CURVE_P2_GEN + 0.1) or self.QP_CURVE_P3_GEN > 1:
            logging.warning("Warning: check failed for QP_CURVE_P3_GEN. For the piecewise linear curve setting of "
                            "watt-var control, the corner points should have their active power settings monotonically "
                            "increasing and within the ranges defined in IEEE 1547-2018 Clause 5.3.4")

    @property
    def QP_CURVE_P2_GEN(self):
        return self._QP_CURVE_P2_GEN

    @QP_CURVE_P2_GEN.setter
    def QP_CURVE_P2_GEN(self, QP_CURVE_P2_GEN):
        self._QP_CURVE_P2_GEN = QP_CURVE_P2_GEN
        if self.QP_CURVE_P2_GEN < 0.4 or self.QP_CURVE_P2_GEN > 0.8:
            logging.warning("Warning: check failed for QP_CURVE_P2_GEN. For the piecewise linear curve setting of "
                            "watt-var control, the corner points should have their active power settings monotonically "
                            "increasing and within the ranges defined in IEEE 1547-2018 Clause 5.3.4")

    @property
    def QP_CURVE_P1_GEN(self):
        return self._QP_CURVE_P1_GEN

    @QP_CURVE_P1_GEN.setter
    def QP_CURVE_P1_GEN(self, QP_CURVE_P1_GEN):
        self._QP_CURVE_P1_GEN = QP_CURVE_P1_GEN
        if self.QP_CURVE_P1_GEN < self.NP_P_MIN_PU or self.QP_CURVE_P1_GEN > (self.QP_CURVE_P2_GEN - 0.1):
            logging.warning("Warning: check failed for QP_CURVE_P1_GEN. For the piecewise linear curve setting of "
                            "watt-var control, the corner points should have their active power settings monotonically "
                            "increasing and within the ranges defined in IEEE 1547-2018 Clause 5.3.4")

    @property
    def QP_CURVE_P1_LOAD(self):
        return self._QP_CURVE_P1_LOAD

    @QP_CURVE_P1_LOAD.setter
    def QP_CURVE_P1_LOAD(self, QP_CURVE_P1_LOAD):
        self._QP_CURVE_P1_LOAD = QP_CURVE_P1_LOAD
        if self._QP_CURVE_P1_LOAD < (self.QP_CURVE_P2_LOAD + 0.1) or self._QP_CURVE_P1_LOAD > 0:
            logging.warning("Warning: check failed for QP_CURVE_P1_LOAD. For the piecewise linear curve setting of "
                            "watt-var control, the corner points should have their active power settings monotonically "
                            "increasing and within the ranges defined in IEEE 1547-2018 Clause 5.3.4")


    @property
    def QP_CURVE_P2_LOAD(self):
        return self._QP_CURVE_P2_LOAD

    @QP_CURVE_P2_LOAD.setter
    def QP_CURVE_P2_LOAD(self, QP_CURVE_P2_LOAD):
        self._QP_CURVE_P2_LOAD = QP_CURVE_P2_LOAD
        if self._QP_CURVE_P2_LOAD < -0.8 or self._QP_CURVE_P2_LOAD > -0.4:
            logging.warning("Warning: check failed for QP_CURVE_P2_LOAD. For the piecewise linear curve setting of "
                            "watt-var control, the corner points should have their active power settings monotonically "
                            "increasing and within the ranges defined in IEEE 1547-2018 Clause 5.3.4")

    @property
    def QP_CURVE_P3_LOAD(self):
        return self._QP_CURVE_P3_LOAD

    @QP_CURVE_P3_LOAD.setter
    def QP_CURVE_P3_LOAD(self, QP_CURVE_P3_LOAD):
        self._QP_CURVE_P3_LOAD = QP_CURVE_P3_LOAD
        if self._QP_CURVE_P3_LOAD < -1 or self._QP_CURVE_P3_LOAD > (self.QP_CURVE_P2_LOAD + 0.1):
            logging.warning("Warning: check failed for QP_CURVE_P3_LOAD. For the piecewise linear curve setting of "
                            "watt-var control, the corner points should have their active power settings monotonically "
                            "increasing and within the ranges defined in IEEE 1547-2018 Clause 5.3.4")


    @property
    def QP_CURVE_Q3_GEN(self):
        return self._QP_CURVE_Q3_GEN

    @QP_CURVE_Q3_GEN.setter
    def QP_CURVE_Q3_GEN(self, QP_CURVE_Q3_GEN):
        self._QP_CURVE_Q3_GEN = QP_CURVE_Q3_GEN
        if (self.QP_CURVE_Q3_GEN < (-self.NP_Q_MAX_ABS / self.NP_VA_MAX) or self.QP_CURVE_Q3_GEN > (
                self.NP_Q_MAX_INJ / self.NP_VA_MAX)):
            logging.warning("Warning: check failed for QP_CURVE_Q3_GEN. Watt-var function reactive power setpoints "
                            "use DER nameplate apparent power rating as base. The setpoints should be within its  "
                            "nameplate reactive power injection and absorption ratings.")
    @property
    def QP_CURVE_Q2_GEN(self):
        return self._QP_CURVE_Q2_GEN

    @QP_CURVE_Q2_GEN.setter
    def QP_CURVE_Q2_GEN(self, QP_CURVE_Q2_GEN):
        self._QP_CURVE_Q2_GEN = QP_CURVE_Q2_GEN
        if (self.QP_CURVE_Q2_GEN < (-self.NP_Q_MAX_ABS / self.NP_VA_MAX) or self.QP_CURVE_Q2_GEN > (
                self.NP_Q_MAX_INJ / self.NP_VA_MAX)):
            logging.warning("Warning: check failed for QP_CURVE_Q2_GEN. Watt-var function reactive power setpoints "
                            "use DER nameplate apparent power rating as base. The setpoints should be within its  "
                            "nameplate reactive power injection and absorption ratings.")

    @property
    def QP_CURVE_Q1_GEN(self):
        return self._QP_CURVE_Q1_GEN

    @QP_CURVE_Q1_GEN.setter
    def QP_CURVE_Q1_GEN(self, QP_CURVE_Q1_GEN):
        self._QP_CURVE_Q1_GEN = QP_CURVE_Q1_GEN
        if (self.QP_CURVE_Q1_GEN < (-self.NP_Q_MAX_ABS / self.NP_VA_MAX) or self.QP_CURVE_Q1_GEN > (
                self.NP_Q_MAX_INJ / self.NP_VA_MAX)):
            logging.warning("Warning: check failed for QP_CURVE_Q1_GEN. Watt-var function reactive power setpoints "
                            "use DER nameplate apparent power rating as base. The setpoints should be within its  "
                            "nameplate reactive power injection and absorption ratings.")

    @property
    def QP_CURVE_Q1_LOAD(self):
        return self._QP_CURVE_Q1_LOAD

    @QP_CURVE_Q1_LOAD.setter
    def QP_CURVE_Q1_LOAD(self, QP_CURVE_Q1_LOAD):
        self._QP_CURVE_Q1_LOAD = QP_CURVE_Q1_LOAD
        if (self._QP_CURVE_Q1_LOAD < (-self.NP_Q_MAX_ABS / self.NP_VA_MAX) or self._QP_CURVE_Q1_LOAD > (
                self.NP_Q_MAX_INJ / self.NP_VA_MAX)):
            logging.warning("Warning: check failed for QP_CURVE_Q1_LOAD. Watt-var function reactive power setpoints "
                            "use DER nameplate apparent power rating as base. The setpoints should be within its  "
                            "nameplate reactive power injection and absorption ratings.")

    @property
    def QP_CURVE_Q2_LOAD(self):
        return self._QP_CURVE_Q2_LOAD

    @QP_CURVE_Q2_LOAD.setter
    def QP_CURVE_Q2_LOAD(self, QP_CURVE_Q2_LOAD):
        self._QP_CURVE_Q2_LOAD = QP_CURVE_Q2_LOAD
        if (self._QP_CURVE_Q2_LOAD < (-self.NP_Q_MAX_ABS / self.NP_VA_MAX) or self._QP_CURVE_Q2_LOAD > (
                self.NP_Q_MAX_INJ / self.NP_VA_MAX)):
            logging.warning("Warning: check failed for QP_CURVE_Q2_LOAD. Watt-var function reactive power setpoints "
                            "use DER nameplate apparent power rating as base. The setpoints should be within its  "
                            "nameplate reactive power injection and absorption ratings.")

    @property
    def QP_CURVE_Q3_LOAD(self):
        return self._QP_CURVE_Q3_LOAD

    @QP_CURVE_Q3_LOAD.setter
    def QP_CURVE_Q3_LOAD(self, QP_CURVE_Q3_LOAD):
        self._QP_CURVE_Q3_LOAD = QP_CURVE_Q3_LOAD
        if (self._QP_CURVE_Q3_LOAD < (-self.NP_Q_MAX_ABS / self.NP_VA_MAX) or self._QP_CURVE_Q3_LOAD > (
                self.NP_Q_MAX_INJ / self.NP_VA_MAX)):
            logging.warning("Warning: check failed for QP_CURVE_Q3_LOAD. Watt-var function reactive power setpoints "
                            "use DER nameplate apparent power rating as base. The setpoints should be within its  "
                            "nameplate reactive power injection and absorption ratings.")

    @property
    def QP_RT(self):
        return self._QP_RT

    @QP_RT.setter
    def QP_RT(self, QP_RT):
        self._QP_RT = QP_RT
        if self._QP_RT < 0 or self._QP_RT > 10:
            logging.error("Warning: Watt-var function response time should be greater than or equal to 0, and smaller "
                          "than or equal to 10 seconds, according to IEEE 1547-2018 Clause 5.3.4.")

    @property
    def PV_MODE_ENABLE(self):
        return self._PV_MODE_ENABLE

    @PV_MODE_ENABLE.setter
    def PV_MODE_ENABLE(self, PV_MODE_ENABLE):
        self._PV_MODE_ENABLE = self.check_enabled(PV_MODE_ENABLE)

    @property
    def PV_CURVE_V1(self):
        return self._PV_CURVE_V1

    @PV_CURVE_V1.setter
    def PV_CURVE_V1(self, PV_CURVE_V1):
        self._PV_CURVE_V1 = PV_CURVE_V1
        if self.PV_CURVE_V1 < 1.05 or self.PV_CURVE_V1 > 1.09:
            logging.warning("Warning: check failed for PV_CURVE_V1. For the piecewise linear curve setting of "
                            "volt-watt control, the two corner points should have their voltage settings "
                            "monotonically increasing and within the ranges defined in IEEE 1547-2018 Clause 5.4.2")

    @property
    def PV_CURVE_P1(self):
        return self._PV_CURVE_P1

    @PV_CURVE_P1.setter
    def PV_CURVE_P1(self, PV_CURVE_P1):
        self._PV_CURVE_P1 = PV_CURVE_P1
        if self.PV_CURVE_P1 < self.PV_CURVE_P2:
            logging.warning("Warning: check failed for PV_CURVE_P1. Volt-watt power settings should be within the"
                            " ranges defined in IEEE 1547-2018 Clause 5.4.2")

    @property
    def PV_CURVE_V2(self):
        return self._PV_CURVE_V2

    @PV_CURVE_V2.setter
    def PV_CURVE_V2(self, PV_CURVE_V2):
        self._PV_CURVE_V2 = PV_CURVE_V2
        if self.PV_CURVE_V2 < self.PV_CURVE_V1 + 0.01 or self.PV_CURVE_V1 > 1.1:
            logging.warning("Warning: check failed for PV_CURVE_V2. For the piecewise linear curve setting of "
                            "volt-watt control, the two corner points should have their voltage settings "
                            "monotonically increasing and within the ranges defined in IEEE 1547-2018 Clause 5.4.2")

    @property
    def PV_CURVE_P2(self):
        return self._PV_CURVE_P2

    @PV_CURVE_P2.setter
    def PV_CURVE_P2(self, PV_CURVE_P2):
        self._PV_CURVE_P2 = PV_CURVE_P2
        if self.PV_CURVE_P2 < self.NP_P_MIN_PU or self.PV_CURVE_P2 > 1:
            logging.warning("Warning: check failed for PV_CURVE_P2. Volt-watt power settings should be within "
                            "the ranges defined in IEEE 1547-2018 Clause 5.4.2")

    @property
    def PV_OLRT(self):
        return self._PV_OLRT

    @PV_OLRT.setter
    def PV_OLRT(self, PV_OLRT):
        self._PV_OLRT = PV_OLRT
        if self.PV_OLRT < 0.5 or self.PV_OLRT > 60:
            logging.warning("Warning: Volt-watt function open loop response time should be within the range defined "
                            "in IEEE 1547-2018 Clause 5.4.2")

    @property
    def NP_V_MEAS_UNBALANCE(self):
        return self._NP_V_MEAS_UNBALANCE

    @NP_V_MEAS_UNBALANCE.setter
    def NP_V_MEAS_UNBALANCE(self, NP_V_MEAS_UNBALANCE):
        if isinstance(NP_V_MEAS_UNBALANCE, str):
            if NP_V_MEAS_UNBALANCE.upper() == 'POS' or NP_V_MEAS_UNBALANCE.upper() == 'AVG':
                self._NP_V_MEAS_UNBALANCE = NP_V_MEAS_UNBALANCE.upper()
            else:
                logging.error("NP_V_MEAS_UNBALANCE should be either 'POS' or 'AVG'")
        else:
            logging.error("NP_V_MEAS_UNBALANCE should be either 'POS' or 'AVG'")

    @property
    def NP_PRIO_OUTSIDE_MIN_Q_REQ(self):
        return self._NP_PRIO_OUTSIDE_MIN_Q_REQ

    @NP_PRIO_OUTSIDE_MIN_Q_REQ.setter
    def NP_PRIO_OUTSIDE_MIN_Q_REQ(self, NP_PRIO_OUTSIDE_MIN_Q_REQ):
        if isinstance(NP_PRIO_OUTSIDE_MIN_Q_REQ, str):
            if NP_PRIO_OUTSIDE_MIN_Q_REQ.upper() == 'ACTIVE' or NP_PRIO_OUTSIDE_MIN_Q_REQ.upper() == 'REACTIVE':
                self._NP_PRIO_OUTSIDE_MIN_Q_REQ = NP_PRIO_OUTSIDE_MIN_Q_REQ.upper()
            else:
                logging.error("NP_PRIO_OUTSIDE_MIN_Q_REQ should be either 'ACTIVE' or 'REACTIVE'")
        else:
            logging.error("NP_PRIO_OUTSIDE_MIN_Q_REQ should be either 'ACTIVE' or 'REACTIVE'")

    @property
    def NP_Q_CAPABILITY_BY_P_CURVE(self):
        return self._NP_Q_CAPABILITY_BY_P_CURVE

    @NP_Q_CAPABILITY_BY_P_CURVE.setter
    def NP_Q_CAPABILITY_BY_P_CURVE(self, NP_Q_CAPABILITY_BY_P_CURVE):
        self._NP_Q_CAPABILITY_BY_P_CURVE = NP_Q_CAPABILITY_BY_P_CURVE

    @property
    def NP_Q_CAPABILITY_LOW_P(self):
        return self._NP_Q_CAPABILITY_LOW_P

    @NP_Q_CAPABILITY_LOW_P.setter
    def NP_Q_CAPABILITY_LOW_P(self, NP_Q_CAPABILITY_LOW_P):
        self._NP_Q_CAPABILITY_LOW_P = NP_Q_CAPABILITY_LOW_P
        self.initialize_NP_Q_CAPABILTY_BY_P_CURVE()

    @property
    def NP_EFFICIENCY(self):
        return self._NP_EFFICIENCY

    @NP_EFFICIENCY.setter
    def NP_EFFICIENCY(self, NP_EFFICIENCY):
        self._NP_EFFICIENCY = NP_EFFICIENCY
        if self.NP_EFFICIENCY < 0 or self.NP_EFFICIENCY > 1:
            logging.error("Error: DER Efficiency should be greater than 0, and less than or equal to 1")
            self._NP_EFFICIENCY = 1

    @property
    def OV2_TRIP_V(self):
        return self._OV2_TRIP_V

    @OV2_TRIP_V.setter
    def OV2_TRIP_V(self, OV2_TRIP_V):
        self._OV2_TRIP_V = OV2_TRIP_V
        if self.OV2_TRIP_V != 1.2:
            logging.warning("Warning: check failed for OV2_TRIP_V. Over- and under-voltage must trip curve point "
                            "voltage settings should be within the ranges defined in IEEE 1547-2018 Clause 6.4.1")

    @property
    def OV2_TRIP_T(self):
        return self._OV2_TRIP_T

    @OV2_TRIP_T.setter
    def OV2_TRIP_T(self, OV2_TRIP_T):
        self._OV2_TRIP_T = OV2_TRIP_T
        if self.OV2_TRIP_T != 0.16:
            logging.warning("Warning: check failed for OV2_TRIP_T. Over- and under-voltage must trip curve point time "
                            "settings should be within the ranges defined in IEEE 1547-2018 Clause 6.4.1")

    @property
    def OV1_TRIP_V(self):
        return self._OV1_TRIP_V

    @OV1_TRIP_V.setter
    def OV1_TRIP_V(self, OV1_TRIP_V):
        self._OV1_TRIP_V = OV1_TRIP_V
        if self.OV1_TRIP_V < 1.1 or self.OV1_TRIP_V > 1.2:
            logging.warning("Warning: check failed for OV1_TRIP_V. Over- and under-voltage must trip curve point "
                            "voltage settings should be within the ranges defined in IEEE 1547-2018 Clause 6.4.1")

    @property
    def OV1_TRIP_T(self):
        return self._OV1_TRIP_T

    @OV1_TRIP_T.setter
    def OV1_TRIP_T(self, OV1_TRIP_T):
        self._OV1_TRIP_T = OV1_TRIP_T
        if self.OV1_TRIP_T < 1 or self.OV1_TRIP_T > 13:
            logging.warning("Warning: check failed for OV1_TRIP_T. Over- and under-voltage must trip curve point time "
                            "settings should be within the ranges defined in IEEE 1547-2018 Clause 6.4.1")

    @property
    def UV1_TRIP_V(self):
        return self._UV1_TRIP_V

    @UV1_TRIP_V.setter
    def UV1_TRIP_V(self, UV1_TRIP_V):
        self._UV1_TRIP_V = UV1_TRIP_V
        if self.UV1_TRIP_V < 0 or self.UV1_TRIP_V > 0.88:
            logging.warning("Warning: check failed for UV1_TRIP_V. Over- and under-voltage must trip curve point "
                            "voltage settings should be within the ranges defined in IEEE 1547-2018 Clause 6.4.1")

    @property
    def UV1_TRIP_T(self):
        return self._UV1_TRIP_T

    @UV1_TRIP_T.setter
    def UV1_TRIP_T(self, UV1_TRIP_T):
        self._UV1_TRIP_T = UV1_TRIP_T
        if self.UV1_TRIP_T < 2 or self.UV1_TRIP_T > 50:
            logging.warning("Warning: check failed for UV1_TRIP_T. Over- and under-voltage must trip curve point time "
                            "settings should be within the ranges defined in IEEE 1547-2018 Clause 6.4.1")

    @property
    def UV2_TRIP_V(self):
        return self._UV2_TRIP_V

    @UV2_TRIP_V.setter
    def UV2_TRIP_V(self, UV2_TRIP_V):
        self._UV2_TRIP_V = UV2_TRIP_V
        if self.UV2_TRIP_V < 0 or self.UV2_TRIP_V > 0.5:
            logging.warning("Warning: check failed for UV2_TRIP_V. Over- and under-voltage must trip curve point "
                            "voltage settings should be within the ranges defined in IEEE 1547-2018 Clause 6.4.1")

    @property
    def UV2_TRIP_T(self):
        return self._UV2_TRIP_T

    @UV2_TRIP_T.setter
    def UV2_TRIP_T(self, UV2_TRIP_T):
        self._UV2_TRIP_T = UV2_TRIP_T
        if self.UV2_TRIP_T < 0.16 or self.UV2_TRIP_T > 21:
            logging.warning("Warning: check failed for UV2_TRIP_T. Over- and under-voltage must trip curve point time "
                            "settings should be within the ranges defined in IEEE 1547-2018 Clause 6.4.1")

    @property
    def OF2_TRIP_F(self):
        return self._OF2_TRIP_F

    @OF2_TRIP_F.setter
    def OF2_TRIP_F(self, OF2_TRIP_F):
        self._OF2_TRIP_F = OF2_TRIP_F
        if self.OF2_TRIP_F < 61.8 or self.OF2_TRIP_F > 66:
            logging.warning("Warning: check failed for OF2_TRIP_F. Over- and under-frequency must trip curve point "
                            "frequency settings should be within the ranges defined in IEEE 1547-2018 Clause 6.5.1")

    @property
    def OF2_TRIP_T(self):
        return self._OF2_TRIP_T

    @OF2_TRIP_T.setter
    def OF2_TRIP_T(self, OF2_TRIP_T):
        self._OF2_TRIP_T = OF2_TRIP_T
        if self.OF2_TRIP_T < 0.16 or self.OF2_TRIP_T > 1000:
            logging.warning("Warning: check failed for OF2_TRIP_T. Over- and under-frequency must trip curve point "
                            "time settings should be within the ranges defined in IEEE 1547-2018 Clause 6.5.1")

    @property
    def OF1_TRIP_F(self):
        return self._OF1_TRIP_F

    @OF1_TRIP_F.setter
    def OF1_TRIP_F(self, OF1_TRIP_F):
        self._OF1_TRIP_F = OF1_TRIP_F
        if self.OF1_TRIP_F < 61 or self.OF1_TRIP_F > 66:
            logging.warning("Warning: check failed for OF1_TRIP_F. Over- and under-frequency must trip curve point "
                            "frequency settings should be within the ranges defined in IEEE 1547-2018 Clause 6.5.1")

    @property
    def OF1_TRIP_T(self):
        return self._OF1_TRIP_T

    @OF1_TRIP_T.setter
    def OF1_TRIP_T(self, OF1_TRIP_T):
        self._OF1_TRIP_T = OF1_TRIP_T
        if self.OF1_TRIP_T < 180 or self.OF1_TRIP_T > 1000:
            logging.warning("Warning: check failed for OF1_TRIP_T. Over- and under-frequency must trip curve point "
                            "time settings should be within the ranges defined in IEEE 1547-2018 Clause 6.5.1")

    @property
    def UF1_TRIP_F(self):
        return self._UF1_TRIP_F

    @UF1_TRIP_F.setter
    def UF1_TRIP_F(self, UF1_TRIP_F):
        self._UF1_TRIP_F = UF1_TRIP_F
        if self.UF1_TRIP_F < 50 or self.UF1_TRIP_F > 59:
            logging.warning("Warning: check failed for UF1_TRIP_F. Over- and under-frequency must trip curve point "
                            "frequency settings should be within the ranges defined in IEEE 1547-2018 Clause 6.5.1")

    @property
    def UF1_TRIP_T(self):
        return self._UF1_TRIP_T

    @UF1_TRIP_T.setter
    def UF1_TRIP_T(self, UF1_TRIP_T):
        self._UF1_TRIP_T = UF1_TRIP_T
        if self.UF1_TRIP_T < 180 or self.UF1_TRIP_T > 1000:
            logging.warning("Warning: check failed for UF1_TRIP_T. Over- and under-frequency must trip curve point "
                            "time settings should be within the ranges defined in IEEE 1547-2018 Clause 6.5.1")

    @property
    def UF2_TRIP_F(self):
        return self._UF2_TRIP_F

    @UF2_TRIP_F.setter
    def UF2_TRIP_F(self, UF2_TRIP_F):
        self._UF2_TRIP_F = UF2_TRIP_F
        if self.UF2_TRIP_F < 50 or self.UF2_TRIP_F > 57:
            logging.warning("Warning: check failed for UF2_TRIP_F. Over- and under-frequency must trip curve point "
                            "frequency settings should be within the ranges defined in IEEE 1547-2018 Clause 6.5.1")

    @property
    def UF2_TRIP_T(self):
        return self._UF2_TRIP_T

    @UF2_TRIP_T.setter
    def UF2_TRIP_T(self, UF2_TRIP_T):
        self._UF2_TRIP_T = UF2_TRIP_T
        if self.UF2_TRIP_T < 0.16 or self.UF2_TRIP_T > 1000:
            logging.warning("Warning: check failed for UF2_TRIP_T. Over- and under-frequency must trip curve point "
                            "time settings should be within the ranges defined in IEEE 1547-2018 Clause 6.5.1")

    @property
    def PF_MODE_ENABLE(self):
        return self._PF_MODE_ENABLE

    @PF_MODE_ENABLE.setter
    def PF_MODE_ENABLE(self, PF_MODE_ENABLE):
        self._PF_MODE_ENABLE = self.check_enabled(PF_MODE_ENABLE)

    @property
    def PF_DBOF(self):
        return self._PF_DBOF

    @PF_DBOF.setter
    def PF_DBOF(self, PF_DBOF):
        self._PF_DBOF = PF_DBOF
        if self.PF_DBOF < 0.017 or self.PF_DBOF > 1:
            logging.warning("Warning: check failed for PF_DBOF. Over- and under-frequency deadband offset from "
                            "nominal frequency settings for frequency-droop function should be within the ranges "
                            "defined in IEEE 1547-2018 Clause 6.5.2.7.2")

    @property
    def PF_DBUF(self):
        return self._PF_DBUF

    @PF_DBUF.setter
    def PF_DBUF(self, PF_DBUF):
        self._PF_DBUF = PF_DBUF
        if self.PF_DBUF < 0.017 or self.PF_DBUF > 1:
            logging.warning("Warning: check failed for PF_DBUF. Over- and under-frequency deadband offset from "
                            "nominal frequency settings for frequency-droop function should be within the ranges "
                            "defined in IEEE 1547-2018 Clause 6.5.2.7.2")

    @property
    def PF_KOF(self):
        return self._PF_KOF

    @PF_KOF.setter
    def PF_KOF(self, PF_KOF):
        self._PF_KOF = PF_KOF
        if self.PF_KOF < 0.02 or self.PF_KOF > 0.05:
            logging.warning("Warning: check failed for PF_KOF. Over- and under-frequency frequency-droop values "
                            "should be within the ranges defined in IEEE 1547-2018 Clause 6.5.2.7.2")

    @property
    def PF_KUF(self):
        return self._PF_KUF

    @PF_KUF.setter
    def PF_KUF(self, PF_KUF):
        self._PF_KUF = PF_KUF
        if self.PF_KUF < 0.02 or self.PF_KUF > 10:
            logging.warning("Warning: check failed for PF_KUF. Over- and under-frequency frequency-droop values "
                            "should be within the ranges defined in IEEE 1547-2018 Clause 6.5.2.7.2")

    @property
    def PF_OLRT(self):
        return self._PF_OLRT

    @PF_OLRT.setter
    def PF_OLRT(self, PF_OLRT):
        self._PF_OLRT = PF_OLRT
        if self.PF_OLRT < 0.2 or self.PF_OLRT > 10:
            logging.warning("Warning: Frequency-droop function open-loop response time should be within the range "
                            "defined in IEEE 1547-2018 Clause 6.5.2.7.2")
    @property
    def MC_LVRT_V1(self):
        return self._MC_LVRT_V1

    @MC_LVRT_V1.setter
    def MC_LVRT_V1(self, MC_LVRT_V1):
        self._MC_LVRT_V1 = MC_LVRT_V1
        if self._MC_LVRT_V1 < 0 or self._MC_LVRT_V1 > 0.5:
            logging.warning("Warning: Low-voltage momentary cessation curve point 1 voltage should be 0.5 for Category "
                            "III DER. For other categories, there is no requirements on momentary cessation")

    @property
    def MC_HVRT_V1(self):
        return self._MC_HVRT_V1

    @MC_HVRT_V1.setter
    def MC_HVRT_V1(self, MC_HVRT_V1):
        self._MC_HVRT_V1 = MC_HVRT_V1
        if self._MC_HVRT_V1 < 1.1:
            logging.warning("Warning: High-voltage momentary cessation curve point 1 voltage should be 1.1 for Category"
                            " III DER. For other categories, there is no requirements on momentary cessation")

    @property
    def STATUS_INIT(self):
        return self._STATUS_INIT

    @STATUS_INIT.setter
    def STATUS_INIT(self, STATUS_INIT):
        if type(STATUS_INIT) is str:
            if (STATUS_INIT.upper() == "ON") or (STATUS_INIT.upper() == "ENABLED"):
                self._STATUS_INIT = True
            elif (STATUS_INIT.upper() == "OFF") or (STATUS_INIT.upper() == "DISABLED") or (STATUS_INIT.upper() == "TRIP"):
                self._STATUS_INIT = False
            else:
                raise ValueError('STATUS_INIT value not valid')
        elif type(STATUS_INIT) is bool:
            self._STATUS_INIT = STATUS_INIT
        else:
            raise ValueError('STATUS_INIT value not valid')

    @property
    def AP_RT(self):
        return self._AP_RT

    @AP_RT.setter
    def AP_RT(self, AP_RT):
        self._AP_RT = AP_RT
        if (self._AP_RT < 0 or self._AP_RT > 30):
            logging.warning("Warning: Active power limit function response time should be greater than or equal to 0,"
                            " and smaller than or equal to 30 seconds, according to IEEE 1547-2018 Clause 4.6.2.")

    @property
    def NP_RESISTANCE(self):
        return self._NP_RESISTANCE

    @NP_RESISTANCE.setter
    def NP_RESISTANCE(self, NP_RESISTANCE):
        self._NP_RESISTANCE = NP_RESISTANCE

    @property
    def NP_REACTANCE(self):
        return self._NP_REACTANCE

    @NP_REACTANCE.setter
    def NP_REACTANCE(self, NP_REACTANCE):
        self._NP_REACTANCE = NP_REACTANCE

    @property
    def NP_INV_DELAY(self):
        return self._NP_INV_DELAY

    @NP_INV_DELAY.setter
    def NP_INV_DELAY(self, NP_INV_DELAY):
        self._NP_INV_DELAY = NP_INV_DELAY

    @property
    def DVS_MODE_ENABLE(self):
        return self._DVS_MODE_ENABLE

    @DVS_MODE_ENABLE.setter
    def DVS_MODE_ENABLE(self, DVS_MODE_ENABLE):
        self._DVS_MODE_ENABLE = self.check_enabled(DVS_MODE_ENABLE)

    @property
    def DVS_K(self):
        return self._DVS_K

    @DVS_K.setter
    def DVS_K(self, DVS_K):
        self._DVS_K = DVS_K
        if DVS_K > 6 or DVS_K < 2:
            logging.warning('Dynamic voltage support gain is expected to be between 2 and 6')

    @property
    def NP_RT_RAMP_UP_TIME(self):
        return self._NP_RT_RAMP_UP_TIME

    @NP_RT_RAMP_UP_TIME.setter
    def NP_RT_RAMP_UP_TIME(self, NP_RT_RAMP_UP_TIME):
        self._NP_RT_RAMP_UP_TIME = NP_RT_RAMP_UP_TIME
        if NP_RT_RAMP_UP_TIME < 0:
            logging.error('DER ride-through ramp up time should be greater than 0')
            self._NP_RT_RAMP_UP_TIME = 0
        if NP_RT_RAMP_UP_TIME > 0.5:
            logging.warning('DER ride-through ramp up time should be smaller than 0.5 s')


    @property
    def MC_RESP_T(self):
        return self._MC_RESP_T

    @MC_RESP_T.setter
    def MC_RESP_T(self, MC_RESP_T):
        self._MC_RESP_T = MC_RESP_T
        if MC_RESP_T < 0:
            logging.error('Momentary cessation response time should be greater than 0')
            self._MC_RESP_T = 0
        if MC_RESP_T > 0.083:
            logging.warning('Momentary cessation response time should be less than 0.083')

    @property
    def NP_CTE_RESP_T(self):
        return self._NP_CTE_RESP_T

    @NP_CTE_RESP_T.setter
    def NP_CTE_RESP_T(self, NP_CTE_RESP_T):
        self._NP_CTE_RESP_T = NP_CTE_RESP_T
        if NP_CTE_RESP_T < 0:
            logging.error('Cease to energize response time should be greater than 0')
            self._NP_CTE_RESP_T = 0
        if NP_CTE_RESP_T > 0.16:
            logging.warning('Cease to energize response time should be less than 0.16')


    @property
    def NP_CURRENT_PU(self):
        return self._NP_CURRENT_PU

    @NP_CURRENT_PU.setter
    def NP_CURRENT_PU(self, NP_CURRENT_PU):
        self._NP_CURRENT_PU = NP_CURRENT_PU
        if NP_CURRENT_PU < 1:
            logging.warning('Inverter nameplate current should be greater than 1 per unit')

    @property
    def NP_REACT_TIME(self):
        return self._NP_REACT_TIME

    @NP_REACT_TIME.setter
    def NP_REACT_TIME(self, NP_REACT_TIME):
        self._NP_REACT_TIME = NP_REACT_TIME
        if NP_REACT_TIME < 0:
            self._NP_REACT_TIME = 0
            logging.error('DER grid support functions reaction time should be greater than 0')

    @property
    def NP_V_MEAS_DELAY(self):
        return self._NP_V_MEAS_DELAY

    @NP_V_MEAS_DELAY.setter
    def NP_V_MEAS_DELAY(self, NP_V_MEAS_DELAY):
        self._NP_V_MEAS_DELAY = NP_V_MEAS_DELAY
        if NP_V_MEAS_DELAY < 0:
            self._NP_V_MEAS_DELAY = 0
            logging.error('DER voltage measurement time should be greater than 0')





if __name__ == "__main__":
    import pathlib
    import os

    script_path = pathlib.Path(os.path.dirname(__file__)).parent

    as_file_path = script_path.joinpath("commonfileformat", "Parameters", "AS-with std-values.csv")
    model_file_path = script_path.joinpath("commonfileformat", "Parameters", "Model-parameters.csv")

    print(as_file_path)
    print(model_file_path)

    file_ss_obj = DERCommonFileFormat(as_file_path, model_file_path)
