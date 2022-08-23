"""
Copyright © 2022 Electric Power Research Institute, Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
· Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
· Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
· Neither the name of the EPRI nor the names of its contributors may be used
  to endorse or promote products derived from this software without specific
  prior written permission.
"""

# -*- coding: utf-8 -*-
# @Time    : 4/16/2021 9:35 AM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : conftest.py
# @Software: PyCharm

import pytest
import pathlib
import os
from opender import der, der_pv, der_bess
from opender import DERCommonFileFormat


@pytest.fixture
def si_obj_creation():
    script_path = pathlib.Path(os.path.dirname(__file__)).parent.parent

    as_file_path = script_path.joinpath("src", "opender", "Parameters", "AS-with std-values.csv")
    model_file_path = script_path.joinpath("src", "opender", "Parameters", "Model-parameters.csv")

    # print(as_file_path)
    # print(model_file_path)

    file_ss_obj = DERCommonFileFormat(as_file_path, model_file_path)

    # ss_file_path = script_path.joinpath("dermodel", "Parameters", "1547_settings_for_exchange_SS.csv")
    #
    # file_ss_obj = common_file_format.DERCommonFileFormat(ss_file_path)

    #
    # file_ss_obj.CONST_PF_MODE_ENABLE = "DISABLED"
    # file_ss_obj.QV_MODE_ENABLE = "DISABLED"
    # file_ss_obj.QP_MODE_ENABLE = "DISABLED"
    # file_ss_obj.CONST_Q_MODE_ENABLE = "DISABLED"
    # file_ss_obj.PV_MODE_ENABLE = "DISABLED"
    # file_ss_obj.AP_LIMIT_ENABLE = "DISABLED"
    # file_ss_obj.NP_AC_V_NOM = 480
    # file_ss_obj.NP_P_MAX = 100
    # file_ss_obj.NP_V_MEAS_UNBALANCE = "AVG"
    # file_ss_obj.NP_PRIO_OUTSIDE_MIN_Q_REQ = "REACTIVE"
    # file_ss_obj.NP_Q_CAPABILITY_LOW_P = "REDUCED"

    si_obj = der_pv.DER_PV(file_ss_obj)
    si_obj.der_input.freq_hz = 60
    der.DER.t_s = 10000

    return si_obj


@pytest.fixture
def bess_obj_creation():

    bess_obj = der_bess.DER_BESS()
    bess_obj.der_input.freq_hz = 60
    der.DER.t_s = 10000

    return bess_obj
