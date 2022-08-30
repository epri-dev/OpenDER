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
# @Time    : 5/6/2021 8:30 AM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : test_volt_var_313.py
# @Software: PyCharm

import pytest

# Volt-var function if DER has greater apparent power nameplate rating than active power rating
input_list = [  # v_pu, p_dc, p_expected, q_expected
    (0.915, 120, 94.3, 46.2),
    (0.925, 120, 96.1, 42.4),
    (0.95, 120, 100, 23.1),
    (0.975, 120, 100, 3.9),
    (0.985, 120, 100, 0),
    (1.015, 120, 100, 0),
    (1.025, 120, 100, -3.8),
    (1.05, 120, 100, -23.1),
    (1.075, 120, 96.1, -42.3),
    (1.085, 120, 94.3, -46.2)
]


class TestVoltVar313:

    @pytest.fixture(autouse=True)
    def _request(self, si_obj_creation):
        self.si_obj = si_obj_creation

    @pytest.mark.parametrize("v_pu, p_dc, p_expected, q_expected", input_list,
                             ids=[f"VoltVar - Qpriority v_pu={i[0]}, p_dc={i[1]}, p_expected={i[2]}, q_expected={i[3]}"
                                  for i in input_list])
    def test_volt_var_q_priority(self, v_pu, p_dc, p_expected, q_expected):

        self.si_obj.der_file.NP_VA_MAX = 105e3

        self.si_obj.der_file.QV_MODE_ENABLE = "ENABLED"
        self.si_obj.der_file.QV_CURVE_V1 = 0.92
        self.si_obj.der_file.QV_CURVE_V2 = 0.98
        self.si_obj.der_file.QV_CURVE_V3 = 1.02
        self.si_obj.der_file.QV_CURVE_V4 = 1.08
        self.si_obj.der_file.QV_CURVE_Q1 = 0.44
        self.si_obj.der_file.QV_CURVE_Q2 = 0
        self.si_obj.der_file.QV_CURVE_Q3 = 0
        self.si_obj.der_file.QV_CURVE_Q4 = -0.44
        self.si_obj.der_file.NP_Q_MAX_INJ = 46.2e3
        self.si_obj.der_file.NP_Q_MAX_ABS = 46.2e3

 #       self.si_obj.der_file.update_smart_function()  # Need to update the smart function selected
        self.si_obj.update_der_input(p_dc_kw=p_dc, v_pu=v_pu)
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
        assert 46.2 * 1000 == self.si_obj.der_file.NP_Q_MAX_INJ
        assert 46.2 * 1000 == self.si_obj.der_file.NP_Q_MAX_ABS

        # Check Results


        p_message = (f"It should be {p_expected} instead it is {self.si_obj.p_out_kw }")
        assert abs(self.si_obj.p_out_kw - p_expected)<0.1, p_message
        q_message = (f"It should be {q_expected} instead it is {self.si_obj.q_out_kvar}")
        assert abs(self.si_obj.q_out_kvar - q_expected)<0.1, q_message