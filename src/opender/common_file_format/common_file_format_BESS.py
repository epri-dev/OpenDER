# Copyright © 2022 Electric Power Research Institute, Inc. All rights reserved.

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
from opender.common_file_format.common_file_format import DERCommonFileFormat


class DERCommonFileFormatBESS(DERCommonFileFormat):
    parameters_list = DERCommonFileFormat.parameters_list + \
                      ['NP_BESS_SOC_MAX', 'NP_BESS_SOC_MIN', 'NP_BESS_CAPACITY', 'NP_BESS_SELF_DISCHARGE',
                       'NP_BESS_SELF_DISCHARGE_SOC', 'NP_BESS_P_MAX_BY_SOC', 'P_DISCHARGE_MAX_PU',
                       'SOC_P_DISCHARGE_MAX', 'P_CHARGE_MAX_PU', 'SOC_P_CHARGE_MAX', 'SOC_INIT'
                       ]

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
        super(DERCommonFileFormatBESS, self).__init__(as_file_path, model_file_path)

        self._NP_P_MIN_PU = -1

        if self.isNotNaN(self.param_inputs.PV_CURVE_P2):
            self.PV_CURVE_P2 = self.param_inputs.PV_CURVE_P2
        else:
            self.PV_CURVE_P2 = 0

        self._NP_BESS_SOC_MAX = 1
        self._NP_BESS_SOC_MIN = 0
        self._NP_BESS_CAPACITY = None
        self._NP_BESS_SELF_DISCHARGE = 0
        self._NP_BESS_SELF_DISCHARGE_SOC = 0
        self._NP_BESS_P_MAX_BY_SOC = dict()
        self._P_DISCHARGE_MAX_PU = None
        self._SOC_P_DISCHARGE_MAX = None
        self._P_CHARGE_MAX_PU = None
        self._SOC_P_CHARGE_MAX = None
        self._SOC_INIT = 0.5

        if self.isNotNaN(self.param_inputs.NP_BESS_SOC_MAX):
            self.NP_BESS_SOC_MAX = self.param_inputs.NP_BESS_SOC_MAX
        if self.isNotNaN(self.param_inputs.NP_BESS_SOC_MIN):
            self.NP_BESS_SOC_MIN = self.param_inputs.NP_BESS_SOC_MIN
        if self.isNotNaN(self.param_inputs.NP_BESS_CAPACITY):
            self.NP_BESS_CAPACITY = self.param_inputs.NP_BESS_CAPACITY
        if self.isNotNaN(self.param_inputs.NP_BESS_SELF_DISCHARGE):
            self.NP_BESS_SELF_DISCHARGE = self.param_inputs.NP_BESS_SELF_DISCHARGE
        if self.isNotNaN(self.param_inputs.NP_BESS_SELF_DISCHARGE_SOC):
            self.NP_BESS_SELF_DISCHARGE_SOC = self.param_inputs.NP_BESS_SELF_DISCHARGE_SOC
        if self.isNotNaN(self.param_inputs.NP_BESS_P_MAX_BY_SOC):
            self.NP_BESS_P_MAX_BY_SOC = self.param_inputs.NP_BESS_P_MAX_BY_SOC
        if self.isNotNaN(self.param_inputs.P_DISCHARGE_MAX_PU):
            self.P_DISCHARGE_MAX_PU = self.param_inputs.P_DISCHARGE_MAX_PU
        if self.isNotNaN(self.param_inputs.SOC_P_DISCHARGE_MAX):
            self.SOC_P_DISCHARGE_MAX = self.param_inputs.SOC_P_DISCHARGE_MAX
        if self.isNotNaN(self.param_inputs.P_CHARGE_MAX_PU):
            self.P_CHARGE_MAX_PU = self.param_inputs.P_CHARGE_MAX_PU
        if self.isNotNaN(self.param_inputs.SOC_P_CHARGE_MAX):
            self.SOC_P_CHARGE_MAX = self.param_inputs.SOC_P_CHARGE_MAX
        if self.isNotNaN(self.param_inputs.SOC_INIT):
            self.SOC_INIT = self.param_inputs.SOC_INIT
        self.initialize_NP_BESS_P_MAX_BY_SOC()
    #
    def _get_parameter_list(self):
        return self.__class__.parameters_list

    def initialize_NP_BESS_P_MAX_BY_SOC(self):
        """
        Initialize Maximum active power limitation by SOC curve using 4 array inputs of P_DISCHARGE_MAX_PU,
        SOC_P_DISCHARGE_MAX, P_CHARGE_MAX_PU, SOC_P_CHARGE_MAX
        """
        if self.isNotNaN(self.P_DISCHARGE_MAX_PU) and self.isNotNaN(self.SOC_P_DISCHARGE_MAX) \
                and self.isNotNaN(self.P_CHARGE_MAX_PU) and self.isNotNaN(self.SOC_P_CHARGE_MAX):
            self.NP_BESS_P_MAX_BY_SOC = {
                'P_DISCHARGE_MAX_PU': [float(x) for x in self.P_DISCHARGE_MAX_PU.strip('][').split(',')],
                'SOC_P_DISCHARGE_MAX': [float(x) for x in self.SOC_P_DISCHARGE_MAX.strip('][').split(',')],
                'P_CHARGE_MAX_PU': [float(x) for x in self.P_CHARGE_MAX_PU.strip('][').split(',')],
                'SOC_P_CHARGE_MAX': [float(x) for x in self.SOC_P_CHARGE_MAX.strip('][').split(',')],
            }

        else:

            self.NP_BESS_P_MAX_BY_SOC = {
                'P_DISCHARGE_MAX_PU': [1, 1],
                'SOC_P_DISCHARGE_MAX': [self.NP_BESS_SOC_MIN, self.NP_BESS_SOC_MAX],
                'P_CHARGE_MAX_PU': [1, 1],
                'SOC_P_CHARGE_MAX': [self.NP_BESS_SOC_MIN, self.NP_BESS_SOC_MAX]
            }

        if (len(self.NP_BESS_P_MAX_BY_SOC['P_DISCHARGE_MAX_PU']) !=
            len(self.NP_BESS_P_MAX_BY_SOC['SOC_P_DISCHARGE_MAX'])) or \
                (len(self.NP_BESS_P_MAX_BY_SOC['P_CHARGE_MAX_PU']) !=
                 len(self.NP_BESS_P_MAX_BY_SOC['SOC_P_CHARGE_MAX'])):
            raise ValueError("ValueError: Check failed for reactive power curve NP_BESS_SELF_DISCHARGE_SOC, please"
                             "make sure all four arrays have the same length")


    @property
    def NP_BESS_SOC_MAX(self):
        return self._NP_BESS_SOC_MAX

    @NP_BESS_SOC_MAX.setter
    def NP_BESS_SOC_MAX(self, NP_BESS_SOC_MAX):
        self._NP_BESS_SOC_MAX = NP_BESS_SOC_MAX
        if self._NP_BESS_SOC_MAX > 1 or self._NP_BESS_SOC_MAX < 0:
            logging.warning("Warning: BESS maximum state of charge should be between 0 an 1")

    @property
    def NP_BESS_SOC_MIN(self):
        return self._NP_BESS_SOC_MIN

    @NP_BESS_SOC_MIN.setter
    def NP_BESS_SOC_MIN(self, NP_BESS_SOC_MIN):
        self._NP_BESS_SOC_MIN = NP_BESS_SOC_MIN
        if self._NP_BESS_SOC_MIN > 1 or self._NP_BESS_SOC_MIN < 0:
            logging.warning("Warning: BESS minimum state of charge should be between 0 an 1")

    @property
    def NP_BESS_CAPACITY(self):
        return self._NP_BESS_CAPACITY

    @NP_BESS_CAPACITY.setter
    def NP_BESS_CAPACITY(self, NP_BESS_CAPACITY):
        self._NP_BESS_CAPACITY = NP_BESS_CAPACITY

    @property
    def NP_BESS_SELF_DISCHARGE(self):
        return self._NP_BESS_SELF_DISCHARGE

    @NP_BESS_SELF_DISCHARGE.setter
    def NP_BESS_SELF_DISCHARGE(self, NP_BESS_SELF_DISCHARGE):
        self._NP_BESS_SELF_DISCHARGE = NP_BESS_SELF_DISCHARGE

    @property
    def NP_BESS_SELF_DISCHARGE_SOC(self):
        return self._NP_BESS_SELF_DISCHARGE_SOC

    @NP_BESS_SELF_DISCHARGE_SOC.setter
    def NP_BESS_SELF_DISCHARGE_SOC(self, NP_BESS_SELF_DISCHARGE_SOC):
        self._NP_BESS_SELF_DISCHARGE_SOC = NP_BESS_SELF_DISCHARGE_SOC

    @property
    def NP_BESS_P_MAX_BY_SOC(self):
        return self._NP_BESS_P_MAX_BY_SOC

    @NP_BESS_P_MAX_BY_SOC.setter
    def NP_BESS_P_MAX_BY_SOC(self, NP_BESS_P_MAX_BY_SOC):
        self._NP_BESS_P_MAX_BY_SOC = NP_BESS_P_MAX_BY_SOC

    @property
    def P_DISCHARGE_MAX_PU(self):
        return self._P_DISCHARGE_MAX_PU

    @P_DISCHARGE_MAX_PU.setter
    def P_DISCHARGE_MAX_PU(self, P_DISCHARGE_MAX_PU):
        self._P_DISCHARGE_MAX_PU = P_DISCHARGE_MAX_PU

    @property
    def SOC_P_DISCHARGE_MAX(self):
        return self._SOC_P_DISCHARGE_MAX

    @SOC_P_DISCHARGE_MAX.setter
    def SOC_P_DISCHARGE_MAX(self, SOC_P_DISCHARGE_MAX):
        self._SOC_P_DISCHARGE_MAX = SOC_P_DISCHARGE_MAX

    @property
    def P_CHARGE_MAX_PU(self):
        return self._P_CHARGE_MAX_PU

    @P_CHARGE_MAX_PU.setter
    def P_CHARGE_MAX_PU(self, P_CHARGE_MAX_PU):
        self._P_CHARGE_MAX_PU = P_CHARGE_MAX_PU

    @property
    def SOC_P_CHARGE_MAX(self):
        return self._SOC_P_CHARGE_MAX

    @SOC_P_CHARGE_MAX.setter
    def SOC_P_CHARGE_MAX(self, SOC_P_CHARGE_MAX):
        self._SOC_P_CHARGE_MAX = SOC_P_CHARGE_MAX

    @property
    def SOC_INIT(self):
        return self._SOC_INIT

    @SOC_INIT.setter
    def SOC_INIT(self, SOC_INIT):
        self._SOC_INIT = SOC_INIT
        if self._SOC_INIT > 1 or self._SOC_INIT < 0:
            self._SOC_INIT = 0.5
            logging.error('SoC initial value not valid, using 0.5 instead')

