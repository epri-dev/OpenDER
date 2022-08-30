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
# @Time    : 5/6/2021 4:15 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : test_volt_var_316.py
# @Software: PyCharm


import pytest

# volt-var function if DER at low active power (reduced)
input_list = [  # v_pu, p_dc, p_expected, q_expected
    (1.085, 0, 0, 0),
    (1.085, 4, 4, 0),
    (1.085, 8, 8, -17.6),
    (1.085, 12, 12, -26.4),
    (1.085, 16, 16, -35.2),
    (1.085, 20, 20, -44),
    (1.085, 24, 24, -44),
    (0.95, 0, 0, 0),
    (0.95, 4, 4, 0),
    (0.95, 8, 8, 17.6),
    (0.95, 12, 12, 22),
    (0.95, 16, 16, 22),
    (0.95, 20, 20, 22),
    (0.95, 24, 24, 22)
]


class TestVoltVar316:

    @pytest.fixture(autouse=True)
    def _request(self, si_obj_creation):
        self.si_obj = si_obj_creation

    @pytest.mark.parametrize("v_pu, p_dc, p_expected, q_expected", input_list,
                             ids=[f"VoltVar - Qpriority v_pu={i[0]}, p_dc={i[1]}, p_expected={i[2]}, q_expected={i[3]}"
                                  for i in input_list])
    def test_volt_var_q_priority(self, v_pu, p_dc, p_expected, q_expected):


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
        self.si_obj.der_file.NP_Q_CAPABILITY_BY_P_CURVE = {
            'P_Q_INJ_PU': [-1, 0.04999, 0.05, 0.2, 1],
            'P_Q_ABS_PU': [-1, 0.04999, 0.05, 0.2, 1],
            'Q_MAX_INJ_PU': [0, 0, 0.11, 0.44, 0.44],
            'Q_MAX_ABS_PU': [0, 0, 0.11, 0.44, 0.44],
        }

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
        assert 44 == self.si_obj.der_file.NP_Q_MAX_INJ
        assert 44 == self.si_obj.der_file.NP_Q_MAX_ABS
        self.si_obj.der_file.initialize_NP_Q_CAPABILTY_BY_P_CURVE()

        # Check Results
        p_actual = round(self.si_obj.p_out_kw, 1)
        q_actual = round(self.si_obj.q_out_kvar, 1)

        p_message = (f"It should be {p_expected} instead it is {p_actual}")
        assert p_expected == p_actual, p_message
        q_message = (f"It should be {q_expected} instead it is {q_actual}")
        assert q_expected == q_actual, q_message