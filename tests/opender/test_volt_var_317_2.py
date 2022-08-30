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
# @Time    : 5/6/2021 4:51 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : test_volt_var_317_2.py
# @Software: PyCharm

import pytest

# Volt-var function with unbalanced voltage input (positive sequence)
input_list = [  # v_pu, p_dc, p_expected, q_expected, calculated_v
    ((1.09, 1.03, 1.03, 0, -2.0944, 2.0944),    80, 80, -22, 1.05),
    ((1.03, 1.09, 1.03, 0, -2.0944, 2.0944),    80, 80, -22, 1.05),
    ((1.03, 1.03, 1.09, 0, -2.0944, 2.0944),    80, 80, -22, 1.05),
    ((0.91, 0.97, 0.97, 0, -2.0944, 2.0944),    80, 80, 22, 0.95),
    ((0.97, 0.91, 0.97, 0, -2.0944, 2.0944),    80, 80, 22, 0.95),
    ((0.97, 0.97, 0.91, 0, -2.0944, 2.0944),    80, 80, 22, 0.95),
    ((1, 1, 1, 0, -1.9, 1.9),                   80, 80, 0, 0.9874),
    ((1, 1, 1, 0, -2.2, 2.2),                   80, 80, 0, 0.9963),
    ((1.09, 1.03, 1.03, 0, -1.9, 1.9),          80, 80, -12.5, 1.0371),
    ((1.09, 1.03, 1.03, 0, -2.2, 2.2),           80, 80, -19.2, 1.0462),
    ((0.91, 0.97, 0.97, 0, -1.9, 1.9),          80, 80, 30.9, 0.9378),
    ((0.91, 0.97, 0.97, 0, -2.2, 2.2),          80, 80, 24.6, 0.9464)
]


class TestVoltVar3172:

    @pytest.fixture(autouse=True)
    def _request(self, si_obj_creation):
        self.si_obj = si_obj_creation

    @pytest.mark.parametrize("v_pu, p_dc, p_expected, q_expected, calculated_v", input_list,
                             ids=[f"VoltVar - Qpriority v_pu={i[0]}, p_dc={i[1]}, p_expected={i[2]}, q_expected={i[3]}, calculated_v={i[4]}"
                                  for i in input_list])
    def test_volt_var_q_priority(self, v_pu, p_dc, p_expected, q_expected, calculated_v):


        self.si_obj.der_file.QV_MODE_ENABLE = "ENABLED"
        self.si_obj.der_file.QV_CURVE_V1 = 0.92
        self.si_obj.der_file.QV_CURVE_V2 = 0.98
        self.si_obj.der_file.QV_CURVE_V3 = 1.02
        self.si_obj.der_file.QV_CURVE_V4 = 1.08
        self.si_obj.der_file.QV_CURVE_Q1 = 0.44
        self.si_obj.der_file.QV_CURVE_Q2 = 0
        self.si_obj.der_file.QV_CURVE_Q3 = 0
        self.si_obj.der_file.QV_CURVE_Q4 = -0.44
        self.si_obj.der_file.NP_Q_MAX_INJ = 44
        self.si_obj.der_file.NP_Q_MAX_ABS = 44
        self.si_obj.der_file.NP_V_MEAS_UNBALANCE = "POS"
        self.si_obj.der_file.OV1_TRIP_V = 1.2
        self.si_obj.der_file.OV2_TRIP_V = 1.2

 #       self.si_obj.der_file.update_smart_function()  # Need to update the smart function selected
        self.si_obj.update_der_input(p_dc_kw=p_dc, v_pu=v_pu[0:3], theta=v_pu[3:6])
        self.si_obj.run()

        # Check inputs
        assert p_dc * 1000 == self.si_obj.der_input.p_dc_w
 #       assert "Reactive Power" == self.si_obj.der_file.power_priority
        assert True == self.si_obj.der_file.QV_MODE_ENABLE
        assert 0.92 == self.si_obj.der_file.QV_CURVE_V1
        assert 0.98 == self.si_obj.der_file.QV_CURVE_V2
        assert 1.02 == self.si_obj.der_file.QV_CURVE_V3
        assert 1.08 == self.si_obj.der_file.QV_CURVE_V4
        assert 0.44 == self.si_obj.der_file.QV_CURVE_Q1
        assert 0 == self.si_obj.der_file.QV_CURVE_Q2
        assert 0 == self.si_obj.der_file.QV_CURVE_Q3
        assert -0.44 == self.si_obj.der_file.QV_CURVE_Q4
        assert 44 == self.si_obj.der_file.NP_Q_MAX_INJ
        assert 44 == self.si_obj.der_file.NP_Q_MAX_ABS
        assert "POS" == self.si_obj.der_file.NP_V_MEAS_UNBALANCE

        # Check Results
        v_actual = round(self.si_obj.der_input.v_meas_pu, 3)
        p_actual = round(self.si_obj.p_out_kw, 1)
        q_actual = round(self.si_obj.q_out_kvar, 1)

        v_message = (f"V should be {calculated_v} instead it is {v_actual}")
        assert round(calculated_v, 3) == v_actual, v_message
        p_message = (f"P should be {p_expected} instead it is {p_actual}")
        assert p_expected == p_actual, p_message
        q_message = (f"Q should be {q_expected} instead it is {q_actual}")
        assert q_expected == q_actual, q_message