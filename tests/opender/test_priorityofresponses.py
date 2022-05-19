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
# @Time    : 5/6/2021 5:33 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : test_vv_vw_344_2.py
# @Software: PyCharm

import pytest
from opender import der
from opender import common_file_format
import pathlib
import os
import math

input_list = [
    ['DER_CAT_A.csv', 'QV', 0, -0.225, -0.225, -0.225, -0.225, 0,0,0],# Q_volt-var=0.25 in Table 38 of IEEE 1547.1-2020, seems to be incorrect.
    ['DER_CAT_A.csv', 'CONST_Q', 0.44,0.44,0.44,0.44,0.44,0.44,0.44,0.44],
    ['DER_CAT_A.csv', 'CONST_PF', 0.9,0.9,0.9,0.9,0.9,0.9,0.9,0.9],
    ['DER_CAT_A.csv', 'QP',0,0,0,0,0,-0.05,0,-0.1],
    ['DER_CAT_B.csv', 'QV', 0, -0.44, -0.44, -0.44, -0.44, 0, 0, 0],
    ['DER_CAT_B.csv', 'CONST_Q', 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44],
    ['DER_CAT_B.csv', 'CONST_PF', 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
    ['DER_CAT_B.csv', 'QP', 0, 0, 0, 0, 0, -0.088, 0, -0.176] # 0.09 and 0.18 in Table 39, can be more accurate
]
# t_s_list = [1, 10,100,1000000]

class TestPriorityOfResponse:
    #IEEE 1547.1-2020, section 5.16.1: type test


    @pytest.mark.parametrize("input_list", input_list)
    def test_priority_of_response_5_16_1(self, input_list):
        der.DER.t_s = 10000
        script_path = pathlib.Path(os.path.dirname(__file__))
        as_file_path = script_path.joinpath(input_list[0])
        file_ss_obj = common_file_format.DERCommonFileFormat(as_file_path)
        self.si_obj = der.DER(file_ss_obj)

        epsilon = 1.e-5
        if input_list[1]=='QV':
            self.si_obj.der_file.QV_MODE_ENABLE = True
        elif input_list[1]=='CONST_PF':
            self.si_obj.der_file.CONST_PF_MODE_ENABLE = True
            self.si_obj.der_file.CONST_PF = 0.9
            self.si_obj.der_file.CONST_PF_EXCITATION = 'INJ'
            input_list[2:]=[math.sqrt(1-0.81)*i/0.9 for i in [0.5, 0.4, 0.3, 0.4, 0.4, 0.6, 0.5, 0.7]]

        elif input_list[1] == 'QP':
            self.si_obj.der_file.QP_MODE_ENABLE = True
        elif input_list[1] == 'CONST_Q':
            self.si_obj.der_file.CONST_Q_MODE_ENABLE = True
            self.si_obj.der_file.CONST_Q = 0.44

        self.si_obj.update_der_input(p_dc_pu=1.1)
        self.si_obj.der_file.AP_LIMIT = 0.5
        self.si_obj.der_file.AP_LIMIT_ENABLE = True
        self.si_obj.der_file.PV_MODE_ENABLE = True
        self.si_obj.der_file.PV_CURVE_P2 = 0.2

        self.si_obj.update_der_input(v_pu=1,f=60) #step 1
        self.si_obj.run()
        assert abs(0.5 * self.si_obj.der_file.NP_P_MAX - self.si_obj.p_out_kw) < epsilon
        assert abs(input_list[2] * self.si_obj.der_file.NP_VA_MAX - self.si_obj.q_out_kvar) < epsilon

        self.si_obj.update_der_input(v_pu=1.09,f=60) #step 2
        self.si_obj.run()
        assert abs(0.4 * self.si_obj.der_file.NP_P_MAX - self.si_obj.p_out_kw) < epsilon
        assert abs(input_list[3] * self.si_obj.der_file.NP_VA_MAX - self.si_obj.q_out_kvar) < epsilon

        self.si_obj.update_der_input(v_pu=1.09,f=60.336) #step 3
        self.si_obj.run()
        assert abs(0.3 * self.si_obj.der_file.NP_P_MAX - self.si_obj.p_out_kw) < epsilon
        assert abs(input_list[4] * self.si_obj.der_file.NP_VA_MAX - self.si_obj.q_out_kvar) < epsilon

        self.si_obj.update_der_input(v_pu=1.09,f=60) #step 4
        self.si_obj.run()
        assert abs(0.4 * self.si_obj.der_file.NP_P_MAX - self.si_obj.p_out_kw) < epsilon
        assert abs(input_list[5] * self.si_obj.der_file.NP_VA_MAX - self.si_obj.q_out_kvar) < epsilon

        self.si_obj.update_der_input(v_pu=1.09,f=59.364) #step 5
        self.si_obj.run()
        assert abs(0.4 * self.si_obj.der_file.NP_P_MAX - self.si_obj.p_out_kw) < epsilon
        assert abs(input_list[6] * self.si_obj.der_file.NP_VA_MAX - self.si_obj.q_out_kvar) < epsilon

        self.si_obj.update_der_input(v_pu=1,f=59.364) #step 6
        self.si_obj.run()
        assert abs(0.6 * self.si_obj.der_file.NP_P_MAX - self.si_obj.p_out_kw) < epsilon
        assert abs(input_list[7] * self.si_obj.der_file.NP_VA_MAX - self.si_obj.q_out_kvar) < epsilon

        self.si_obj.update_der_input(v_pu=1, f=60)  # step 7
        self.si_obj.run()
        assert abs(0.5 * self.si_obj.der_file.NP_P_MAX - self.si_obj.p_out_kw) < epsilon
        assert abs(input_list[8] * self.si_obj.der_file.NP_VA_MAX - self.si_obj.q_out_kvar) < epsilon

        self.si_obj.update_der_input(v_pu=1,f=59.364) #step 8
        self.si_obj.run()
        assert abs(0.7 * self.si_obj.der_file.NP_P_MAX - self.si_obj.p_out_kw) < epsilon
        assert abs(input_list[9] * self.si_obj.der_file.NP_VA_MAX - self.si_obj.q_out_kvar) < epsilon
