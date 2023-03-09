"""
Copyright © 2023 Electric Power Research Institute, Inc. All rights reserved.

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
# @Time    : 4/16/2021 9:47 AM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : test_constant_power_factor_function.py
# @Software: PyCharm


import pytest
import numpy as np

# p_dc_list = [dc_power * 10 for dc_power in range(11)]
p_dc_list = [dc_power * 10 for dc_power in range(11)]
pf_list = [-0.9, -0.95, 1, 0.95, 0.9]

# Constant Power Factor with Active Power Limit Verification
input_list = [  # p_dc, pf, p_expected, q_expected
    (0, -0.9, 0, 0),
    (10, -0.9, 10, -4.84),
    (40, -0.9, 40, -19.37),
    (50, -0.9, 50, -24.22),
    (80, -0.9, 50, -24.22),
    (100, -0.9, 50, -24.22),
]


class TestConstantPowerFactor:

    @pytest.fixture(autouse=True)
    def _request(self, si_obj_creation):
        self.si_obj = si_obj_creation

    @pytest.mark.parametrize("p_dc", p_dc_list, ids=[f"C PF p_dc={p_dc}" for p_dc in p_dc_list])
    @pytest.mark.parametrize("pf", pf_list, ids=[f"C PF pf={pf}" for pf in pf_list])
    def test_pf_with_limit(self, p_dc, pf):

        self.si_obj.der_file.NP_VA_MAX = 1.2 * self.si_obj.der_file.NP_P_MAX  # To not limit
        self.si_obj.der_file.CONST_PF_MODE_ENABLE = "ENABLED"
        self.si_obj.der_file.CONST_PF = abs(pf)
        self.si_obj.der_file.CONST_PF_EXCITATION = "INJ" if pf >= 0 else "ABS"

 #       self.si_obj.der_file.update_smart_function()  # Need to update the smart function selected
        self.si_obj.update_der_input(v_pu=1, p_dc_kw=p_dc)
        self.si_obj.run()

        # Check inputs
        assert True == self.si_obj.der_file.CONST_PF_MODE_ENABLE
        assert p_dc * 1e3 == self.si_obj.der_input.p_dc_w
        assert abs(pf) == self.si_obj.der_file.CONST_PF
        assert "INJ" if pf >= 0 else "ABS" == self.si_obj.der_file.CONST_PF_EXCITATION

        # Check Results
        p_actual = round(self.si_obj.p_out_kw,3)
        q_actual = round(self.si_obj.q_out_kvar,3)

        # Efficiency is not considered here
        p_expected = round(p_dc,3)
        q_expected = round(np.sign(pf) * p_dc * np.tan(np.arccos(abs(pf))),3)

        p_message = (f"It should be {p_expected} instead it is {p_actual}")
        assert p_expected == p_actual, p_message
        q_message = (f"It should be {q_expected} instead it is {q_actual}")
        assert q_expected == q_actual, q_message

    @pytest.mark.parametrize("p_dc, pf, p_expected, q_expected", input_list,
                             ids=[f"CPF AP p_dc={i[0]}, pf={i[1]}, p_expected={i[2]}, q_expected={i[3]}"
                                  for i in input_list])
    def test_pf_with_ap(self, p_dc, pf, p_expected, q_expected):

        p_limit = 0.5

        self.si_obj.der_file.CONST_PF_MODE_ENABLE = "ENABLED"
        self.si_obj.der_file.CONST_PF = abs(pf)
        self.si_obj.der_file.CONST_PF_EXCITATION = "INJ" if pf >= 0 else "ABS"
        self.si_obj.der_file.AP_LIMIT_ENABLE = "ENABLED"
        self.si_obj.der_file.AP_LIMIT = p_limit

 #       self.si_obj.der_file.update_smart_function()  # Need to update the smart function selected
        self.si_obj.update_der_input(p_dc_kw=p_dc, v_pu=1)
        self.si_obj.run()

        # Check inputs
        assert True == self.si_obj.der_file.CONST_PF_MODE_ENABLE
        assert p_dc * 1e3 == self.si_obj.der_input.p_dc_w
        assert abs(pf) == self.si_obj.der_file.CONST_PF
        assert "INJ" if pf >= 0 else "ABS" == self.si_obj.der_file.CONST_PF_EXCITATION
        assert True == self.si_obj.der_file.AP_LIMIT_ENABLE
        assert p_limit == self.si_obj.der_file.AP_LIMIT

        # Check Results
        p_actual = round(self.si_obj.p_out_kw, 2)
        q_actual = round(self.si_obj.q_out_kvar, 2)

        p_message = (f"It should be {p_expected} instead it is {p_actual}")
        assert p_expected == p_actual, p_message
        q_message = (f"It should be {q_expected} instead it is {q_actual}")
        assert q_expected == q_actual, q_message

#python -m pytest -p no:warning