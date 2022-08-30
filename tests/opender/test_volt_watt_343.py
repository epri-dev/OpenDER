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
# @Time    : 5/6/2021 12:52 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : test_volt_watt_343.py
# @Software: PyCharm


import pytest

# Constant Power Factor with Active Power Limit Verification
input_list = [  # v_pu, p_dc, p_expected, q_expected
    (1.01, 100, 50, 0),
    (1.03, 100, 50, 0),
    (1.05, 100, 50, 0),
    (1.07, 100, 50, 0),
    (1.09, 100, 25, 0),
    (1.1, 100, 0, 0),
    (1.01, 40, 40, 0),
    (1.03, 40, 40, 0),
    (1.05, 40, 40, 0),
    (1.07, 40, 40, 0),
    (1.09, 40, 25, 0),
    (1.1, 40, 0, 0)
]


class TestVoltWatt343:

    @pytest.fixture(autouse=True)
    def _request(self, si_obj_creation):
        self.si_obj = si_obj_creation

    @pytest.mark.parametrize("v_pu, p_dc, p_expected, q_expected", input_list,
                             ids=[f"VoltWatt - v_pu={i[0]}, p_dc={i[1]}, p_expected={i[2]}, q_expected={i[3]}"
                                  for i in input_list])
    def test_volt_watt(self, v_pu, p_dc, p_expected, q_expected):
        p_limit = 0.5


        self.si_obj.der_file.PV_MODE_ENABLE = "ENABLED"
        self.si_obj.der_file.PV_CURVE_V1 = 1.06
        self.si_obj.der_file.PV_CURVE_V2 = 1.1
        self.si_obj.der_file.PV_CURVE_P1 = 1
        self.si_obj.der_file.PV_CURVE_P2 = 0
        self.si_obj.der_file.AP_LIMIT = p_limit
        self.si_obj.der_file.AP_LIMIT_ENABLE = "ENABLED"

 #       self.si_obj.der_file.update_smart_function()  # Need to update the smart function selected
        self.si_obj.update_der_input(p_dc_kw=p_dc, v_pu=v_pu)
        self.si_obj.run()

        # Check inputs
        assert p_dc * 1000 == self.si_obj.der_input.p_dc_w
        assert self.si_obj.der_file.PV_MODE_ENABLE
        assert 1.06 == self.si_obj.der_file.PV_CURVE_V1
        assert 1.1 == self.si_obj.der_file.PV_CURVE_V2
        assert 1 == self.si_obj.der_file.PV_CURVE_P1
        assert 0 == self.si_obj.der_file.PV_CURVE_P2
        assert p_limit == self.si_obj.der_file.AP_LIMIT
        assert self.si_obj.der_file.AP_LIMIT_ENABLE

        # Check Results
        p_actual = round(self.si_obj.p_out_kw, 1)
        q_actual = round(self.si_obj.q_out_kvar, 1)

        p_message = (f"It should be {p_expected} instead it is {p_actual}")
        assert p_expected == p_actual, p_message
        q_message = (f"It should be {q_expected} instead it is {q_actual}")
        assert q_expected == q_actual, q_message