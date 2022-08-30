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
# @Time    : 5/6/2021 12:36 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : test_power_factor_342.py
# @Software: PyCharm

import pytest

error = 0.2
# Constant power factor function if DER has larger apparent power nameplate setting than
# active power rating
input_list = [  # p_dc, pf, p_expected, q_expected
    (1, 10, 10, 3.3),
    (1, 20, 20, 6.6),
    (1, 30, 30, 9.9),
    (1, 40, 40, 13.1),
    (1, 50, 50, 16.4),
    (1, 60, 50, 16.4),
    (1, 70, 50, 16.4),
    (1, 80, 50, 16.4),
    (1, 90, 50, 16.4),
    (1, 100, 50, 16.4)
]


class TestConstantPowerFactor342:

    @pytest.fixture(autouse=True)
    def _request(self, si_obj_creation):
        self.si_obj = si_obj_creation

    @pytest.mark.parametrize("v_pu, p_dc, p_expected, q_expected", input_list,
                             ids=[f"Power Factor v_pu={i[0]}, p_dc={i[1]}, p_expected={i[2]}, q_expected={i[3]}"
                                  for i in input_list])
    def test_pf_with_ap(self, v_pu, p_dc, p_expected, q_expected):

        p_limit = 0.5
        const_pf = 0.95




        self.si_obj.der_file.CONST_PF_MODE_ENABLE = "ENABLED"
        self.si_obj.der_file.CONST_PF = const_pf
        self.si_obj.der_file.CONST_PF_EXCITATION = "INJ"
        self.si_obj.der_file.AP_LIMIT_ENABLE = "ENABLED"
        self.si_obj.der_file.AP_LIMIT = p_limit
        self.si_obj.der_file.NP_Q_MAX_INJ = 44e3
        self.si_obj.der_file.NP_Q_MAX_ABS = 44e3

 #       self.si_obj.der_file.update_smart_function()  # Need to update the smart function selected
        self.si_obj.update_der_input(p_dc_kw=p_dc, v_pu=v_pu)
        self.si_obj.run()

        # Check inputs
        assert 100 * 1000 == self.si_obj.der_file.NP_VA_MAX
        assert self.si_obj.der_file.CONST_PF_MODE_ENABLE
        assert p_dc * 1000 == self.si_obj.der_input.p_dc_w
        assert const_pf == self.si_obj.der_file.CONST_PF
        assert "INJ" == self.si_obj.der_file.CONST_PF_EXCITATION
        assert self.si_obj.der_file.AP_LIMIT_ENABLE
        assert p_limit == self.si_obj.der_file.AP_LIMIT
        assert 44 * 1000 == self.si_obj.der_file.NP_Q_MAX_INJ
        assert 44 * 1000  == self.si_obj.der_file.NP_Q_MAX_ABS

        # Check Results
        p_actual = round(self.si_obj.p_out_kw, 1)
        q_actual = round(self.si_obj.q_out_kvar, 1)

        p_message = (f"It should be {p_expected} instead it is {p_actual}")
        assert abs(p_expected - p_actual) <= error, p_message
        q_message = (f"It should be {q_expected} instead it is {q_actual}")
        assert abs(q_expected - q_actual) <= error, q_message