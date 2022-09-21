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
# @Time    : 5/6/2021 2:30 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : test_volt_watt_332_2.py
# @Software: PyCharm

# -*- coding: utf-8 -*-
# @Time    : 5/6/2021 1:44 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : test_volt_watt_332.py
# @Software: PyCharm

import pytest

error = 0.2
# Constant Power Factor with Active Power Limit Verification
input_list = [  # v_pu, p_dc, p_expected, q_expected
    ((1.09, 1.09, 1.06, 0, -2.0944, 2.0944),    100, 50, 0, 1.08),
    ((1.06, 1.09, 1.09, 0, -2.0944, 2.0944),    100, 50, 0, 1.08),
    ((1.09, 1.06, 1.09, 0, -2.0944, 2.0944),    100, 50, 0, 1.08),
    ((1.09, 1.03, 1.03, 0, -2.0944, 2.0944),    100, 100, 0, 1.05),
    ((1.03, 1.09, 1.03, 0, -2.0944, 2.0944),    100, 100, 0, 1.05),
    ((1.03, 1.03, 1.09, 0, -2.0944, 2.0944),    100, 100, 0, 1.05),
    ((1.06, 1.09, 1.09, 0, -1.9, 1.9),          100, 84.25, 0, 1.0663),
    ((1.06, 1.09, 1.09, 0, -2.2, 2.2),          100, 60, 0, 1.0760),
    ((1.09, 1.09, 1.09, 0, -1.9, 1.9),          100, 59.25, 0, 1.0763),
    ((1.09, 1.09, 1.09, 0, -2.2, 2.2),          100, 35, 0, 1.0860)
]


class TestVoltWatt3322:

    @pytest.fixture(autouse=True)
    def _request(self, si_obj_creation):
        self.si_obj = si_obj_creation

    @pytest.mark.parametrize("v_pu, p_dc, p_expected, q_expected, calculated_v", input_list,
                             ids=[f"VoltWatt - Qpriority v_pu={i[0]}, p_dc={i[1]}, p_expected={i[2]}, q_expected={i[3]}, calculated_v={i[4]}"
                                  for i in input_list])

    def test_volt_watt(self, v_pu, p_dc, p_expected, q_expected, calculated_v):
        p_limit = 0.5


        self.si_obj.der_file.PV_MODE_ENABLE = "ENABLED"
        self.si_obj.der_file.PV_CURVE_V1 = 1.06
        self.si_obj.der_file.PV_CURVE_V2 = 1.1
        self.si_obj.der_file.PV_CURVE_P1 = 1
        self.si_obj.der_file.PV_CURVE_P2 = 0
        self.si_obj.der_file.AP_LIMIT = p_limit
        self.si_obj.der_file.AP_LIMIT_ENABLE = "DISABLED"
        self.si_obj.der_file.NP_V_MEAS_UNBALANCE = "POS"
        self.si_obj.der_file.OV1_TRIP_V = 1.2
        self.si_obj.der_file.OV2_TRIP_V = 1.2
        self.si_obj.der_file.NP_ABNORMAL_OP_CAT = 'CAT_II'

 #       self.si_obj.der_file.update_smart_function()  # Need to update the smart function selected
        self.si_obj.update_der_input(p_dc_kw=p_dc, v_pu=v_pu[0:3], theta=v_pu[3:6])

        self.si_obj.run()

        # Check inputs
        assert p_dc * 1000 == self.si_obj.der_input.p_dc_w
        assert self.si_obj.der_file.PV_MODE_ENABLE
        assert 1.06 == self.si_obj.der_file.PV_CURVE_V1
        assert 1.1 == self.si_obj.der_file.PV_CURVE_V2
        assert 1 == self.si_obj.der_file.PV_CURVE_P1
        assert 0 == self.si_obj.der_file.PV_CURVE_P2
        assert p_limit == self.si_obj.der_file.AP_LIMIT
        assert not self.si_obj.der_file.AP_LIMIT_ENABLE
        assert "POS" == self.si_obj.der_file.NP_V_MEAS_UNBALANCE

        # Check Results
        v_actual = round(self.si_obj.der_input.v_meas_pu, 3)
        p_actual = round(self.si_obj.p_out_kw, 1)
        q_actual = round(self.si_obj.q_out_kvar, 1)

        v_message = (f"V should be {calculated_v} instead it is {v_actual}")
        assert round(calculated_v, 3) == v_actual, v_message
        p_message = (f"It should be {p_expected} instead it is {p_actual}")
        assert abs(p_expected - p_actual) <= error, p_message
        q_message = (f"It should be {q_expected} instead it is {q_actual}")
        assert abs(q_expected - q_actual) <= error, q_message