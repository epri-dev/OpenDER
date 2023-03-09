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
# @Time    : 2/23/2021 6:00 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : test_ap_function.py
# @Software: PyCharm

import pytest

input_list = [  # p_dem, p_limit, p_expected, q_expected
    (100, 0.5, 50, 0),
    (30, 0.5, 30, 0),
    (0, -0.5, -40, 0),
    (-50, -0.5, -50, 0),
]


class TestLimitP:

    @pytest.fixture(autouse=True)
    def _request(self, bess_obj_creation):
        self.si_obj = bess_obj_creation

    @pytest.mark.parametrize("p_dc, p_limit, p_expected, q_expected", input_list,
                             ids=[f"AP p_dc={i[0]}, p_per={i[1]}, p_expected={i[2]}, q_expected={i[3]}"
                                  for i in input_list])
    def test_ap_enabled(self, p_dc, p_limit, p_expected, q_expected):

        self.si_obj.der_file.AP_LIMIT_ENABLE = "ENABLED"
        self.si_obj.der_file.AP_LIMIT = p_limit
        self.si_obj.der_file.NP_P_MAX_CHARGE = 80000

        self.si_obj.update_der_input(v_pu=1, p_dem_kw=p_dc)
        self.si_obj.run()

        # Check inputs
        assert True == self.si_obj.der_file.AP_LIMIT_ENABLE
        assert p_limit == self.si_obj.der_file.AP_LIMIT
        assert p_dc * 1e3 == self.si_obj.der_input.p_dem_w

        # Check Results
        p_actual = self.si_obj.p_out_kw
        q_actual = self.si_obj.q_out_kvar

        p_message = (f"It should be {p_expected} instead it is {p_actual}")
        assert p_expected == p_actual, p_message
        q_message = (f"It should be {q_expected} instead it is {q_actual}")
        assert q_expected == q_actual, q_message

#python -m pytest -p no:warning