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
# @Time    : 5/6/2021 12:25 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : test_power_factor_322.py
# @Software: PyCharm

import pytest

error = 0.2
# Constant power factor function if DER has larger apparent power nameplate setting than active power rating
input_list = [  # p_dc, pf, p_expected, q_expected
    (1, 10, 10, -4.8),
    (1, 20, 20, -9.7),
    (1, 30, 30, -14.5),
    (1, 40, 40, -19.4),
    (1, 50, 50, -24.2),
    (1, 60, 60, -29.1),
    (1, 70, 70, -33.9),
    (1, 80, 80, -38.8),
    (1, 90, 90, -43.6),
    (1, 100, 100, -48.2),
    (1, 110, 100, -48.2),
    (1.05, 50, 50, -24.2),
    (0.95, 50, 50, -24.2)
]


class TestConstantPowerFactor322:

    @pytest.fixture(autouse=True)
    def _request(self, si_obj_creation):
        self.si_obj = si_obj_creation

    @pytest.mark.parametrize("v_pu, p_dc, p_expected, q_expected", input_list,
                             ids=[f"Power Factor v_pu={i[0]}, p_dc={i[1]}, p_expected={i[2]}, q_expected={i[3]}"
                                  for i in input_list])
    def test_pf_with_ap(self, v_pu, p_dc, p_expected, q_expected):

        p_limit = 1

        self.si_obj.der_file.NP_VA_MAX = 111e3

        self.si_obj.der_file.CONST_PF_MODE_ENABLE = "ENABLED"
        self.si_obj.der_file.CONST_PF = 0.9
        self.si_obj.der_file.CONST_PF_EXCITATION = "ABS"
        self.si_obj.der_file.AP_LIMIT_ENABLE = "DISABLED"
        self.si_obj.der_file.AP_LIMIT = p_limit
        self.si_obj.der_file.NP_Q_MAX_INJ = 49e3
        self.si_obj.der_file.NP_Q_MAX_ABS = 49e3

 #       self.si_obj.der_file.update_smart_function()  # Need to update the smart function selected
        self.si_obj.update_der_input(p_dc_kw=p_dc, v_pu=v_pu)
        self.si_obj.run()

        # Check inputs
        assert 111 * 1000 == self.si_obj.der_file.NP_VA_MAX
        assert True == self.si_obj.der_file.CONST_PF_MODE_ENABLE
        assert p_dc * 1000 == self.si_obj.der_input.p_dc_w
        assert 0.9 == self.si_obj.der_file.CONST_PF
        assert "ABS" == self.si_obj.der_file.CONST_PF_EXCITATION
        assert False == self.si_obj.der_file.AP_LIMIT_ENABLE
        assert p_limit == self.si_obj.der_file.AP_LIMIT
        assert 49 * 1000 == self.si_obj.der_file.NP_Q_MAX_INJ
        assert 49 * 1000 == self.si_obj.der_file.NP_Q_MAX_ABS

        # Check Results
        p_actual = round(self.si_obj.p_out_kw, 1)
        q_actual = round(self.si_obj.q_out_kvar, 1)

        p_message = (f"It should be {p_expected} instead it is {p_actual}")
        assert abs(p_expected - p_actual) <= error, p_message
        q_message = (f"It should be {q_expected} instead it is {q_actual}")
        assert abs(q_expected - q_actual) <= error, q_message