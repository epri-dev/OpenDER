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
# @Time    : 5/6/2021 5:57 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : test_power_factor_352.py
# @Software: PyCharm


import pytest

error = 0.2

# const pf+eff
input_list = [  # p_dc, pf, p_expected, q_expected
    (1, 10, 9.7, 4.7),
    (1, 20, 19.4, 9.4),
    (1, 30, 29.1, 14.1),
    (1, 40, 38.8, 18.8),
    (1, 50, 48.5, 23.5),
    (1, 60, 58.2, 28.2),
    (1, 70, 67.9, 32.9),
    (1, 80, 77.6, 37.6),
    (1, 90, 87.3, 42.3),
    (1, 100, 90, 43.6),
    (1, 110, 90, 43.6),
    (1.05, 50, 48.5, 23.5),
    (0.95, 50, 48.5, 23.5)
]


class TestConstantPowerFactor352:

    @pytest.fixture(autouse=True)
    def _request(self, si_obj_creation):
        self.si_obj = si_obj_creation

    @pytest.mark.parametrize("v_pu, p_dc, p_expected, q_expected", input_list,
                             ids=[f"Power Factor v_pu={i[0]}, p_dc={i[1]}, p_expected={i[2]}, q_expected={i[3]}"
                                  for i in input_list])
    def test_pf_with_ap(self, v_pu, p_dc, p_expected, q_expected):

        p_limit = 1

        self.si_obj.der_file.NP_P_MAX = 100
        self.si_obj.der_file.CONST_PF_MODE_ENABLE = "ENABLED"
        self.si_obj.der_file.CONST_PF = 0.9
        self.si_obj.der_file.CONST_PF_EXCITATION = "INJ"
        self.si_obj.der_file.AP_LIMIT_ENABLE = "DISABLED"
        self.si_obj.der_file.AP_LIMIT = p_limit
        self.si_obj.der_file.NP_EFFICIENCY = 0.97

 #       self.si_obj.der_file.update_smart_function()  # Need to update the smart function selected
        self.si_obj.update_der_input(p_dc_kw=p_dc, v_pu=v_pu)
        self.si_obj.run()

        # Check inputs
        assert self.si_obj.der_file.CONST_PF_MODE_ENABLE
        assert p_dc == self.si_obj.der_input.p_dc_kw
        assert 0.9 == self.si_obj.der_file.CONST_PF
        assert "INJ" == self.si_obj.der_file.CONST_PF_EXCITATION
        assert not self.si_obj.der_file.AP_LIMIT_ENABLE
        assert p_limit == self.si_obj.der_file.AP_LIMIT
        assert 0.97 == self.si_obj.der_file.NP_EFFICIENCY

        # Check Results
        p_actual = round(self.si_obj.p_out_kw, 2)
        q_actual = round(self.si_obj.q_out_kvar, 2)

        p_message = (f"It should be {p_expected} instead it is {p_actual}")
        assert abs(p_expected - p_actual) <= error, p_message
        q_message = (f"It should be {q_expected} instead it is {q_actual}")
        assert abs(q_expected - q_actual) <= error, q_message