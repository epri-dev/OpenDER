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
# @Time    : 4/23/2021 8:28 AM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : test_volt_watt.py
# @Software: PyCharm


import pytest

# Constant Power Factor with Active Power Limit Verification
input_list = [  # v_pu, p_dc, p_expected, q_expected
    (1.01, 100, 100, 0),
    (1.03, 100, 100, 0),
    (1.05, 100, 100, 0),
    (1.07, 100, 80, 0),
    (1.09, 100, 40, 0),
    # (1.11, 100, 20, 0),
    (1.01, 10, 10, 0),
    (1.03, 10, 10, 0),
    (1.05, 10, 10, 0),
    (1.07, 10, 10, 0),
    (1.09, 10, 10, 0),
    # (1.11, 10, 10, 0),
    (1.01, 50, 50, 0),
    (1.03, 50, 50, 0),
    (1.05, 50, 50, 0),
    (1.07, 50, 50, 0),
    (1.09, 50, 40, 0),
    # (1.11, 50, 20, 0)
]


class TestVoltWatt:

    @pytest.fixture(autouse=True)
    def _request(self, si_obj_creation):
        self.si_obj = si_obj_creation

    @pytest.mark.parametrize("v_pu, p_dc, p_expected, q_expected", input_list,
                             ids=[f"VoltWatt - v_pu={i[0]}, p_dc={i[1]}, p_expected={i[2]}, q_expected={i[3]}"
                                  for i in input_list])
    def test_volt_watt(self, v_pu, p_dc, p_expected, q_expected):

        self.si_obj.der_file.NP_P_MAX = 100
        self.si_obj.der_file.PV_MODE_ENABLE = "ENABLED"
        self.si_obj.der_file.PV_CURVE_V1 = 1.06
        self.si_obj.der_file.PV_CURVE_V2 = 1.1
        self.si_obj.der_file.PV_CURVE_P1 = 1
        self.si_obj.der_file.PV_CURVE_P2 = 0.2

 #       self.si_obj.der_file.update_smart_function()  # Need to update the smart function selected
        self.si_obj.der_input.p_dc_kw = p_dc
        self.si_obj.der_input.v_a, self.si_obj.der_input.v_b, self.si_obj.der_input.v_c= 277.128129 * v_pu, 277.128129 * v_pu, 277.128129 * v_pu
        self.si_obj.run()

        # Check inputs
        assert p_dc == self.si_obj.der_input.p_dc_kw
        assert True == self.si_obj.der_file.PV_MODE_ENABLE
        assert 1.06 == self.si_obj.der_file.PV_CURVE_V1
        assert 1.1 == self.si_obj.der_file.PV_CURVE_V2
        assert 1 == self.si_obj.der_file.PV_CURVE_P1
        assert 0.2 == self.si_obj.der_file.PV_CURVE_P2

        # Check Results
        p_actual = round(self.si_obj.p_out_kw, 1)
        q_actual = round(self.si_obj.q_out_kvar, 1)

        p_message = (f"It should be {p_expected} instead it is {p_actual}")
        assert p_expected == p_actual, p_message
        q_message = (f"It should be {q_expected} instead it is {q_actual}")
        assert q_expected == q_actual, q_message