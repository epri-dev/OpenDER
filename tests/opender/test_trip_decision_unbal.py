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

import pytest

# const pf+eff
input_list = [  #v, theta, p_dc, expected p, expected q

    ([1.11, 1.03, 1.03], [0, -2.0944, 2.0944], 80, 0, 0),
    ([1.03, 1.11, 1.03], [0, -2.0944, 2.0944], 80, 0, 0),
    ([1.03, 1.03, 1.11], [0, -2.0944, 2.0944], 80, 0, 0),
    ([0.87, 0.97, 0.97], [0, -2.0944, 2.0944], 80, 0, 0),
    ([0.97, 0.87, 0.97], [0, -2.0944, 2.0944], 80, 0, 0),
    ([0.97, 0.97, 0.87], [0, -2.0944, 2.0944], 80, 0, 0),
    ([1.03, 1.07, 1.07], [0, -1.9, 1.9], 80, 0, 0),
    ([1.03, 1.07, 1.07], [0, -2.2, 2.2], 80, 80, 0),
    ([0.97, 0.92, 0.92], [0, -1.9, 1.9], 80, 80, 0),
    ([0.97, 0.92, 0.92], [0, -2.2, 2.2], 80, 0, 0),
    ]


class TestTripUnbalanced:

    @pytest.fixture(autouse=True)
    def _request(self, si_obj_creation):
        self.si_obj = si_obj_creation

    @pytest.mark.parametrize("v_pu, theta, p_dc, p_expected, q_expected", input_list,
                             ids=[f"trip v_pu={i[0]}, theta={i[1]}p_dc={i[2]}, p_expected={i[3]}, q_expected={i[4]}"
                                  for i in input_list])
    def test_trip_unb(self, v_pu, theta, p_dc, p_expected, q_expected):


        # self.si_obj.der_file.QV_MODE_ENABLE = "ENABLED"


 #       self.si_obj.der_file.update_smart_function()  # Need to update the smart function selected
        self.si_obj.update_der_input(v_pu=v_pu, theta=theta, p_dc_kw=p_dc)
        self.si_obj.run()

        # Check Results
        p_actual = round(self.si_obj.p_out_kw, 2)
        q_actual = round(self.si_obj.q_out_kvar, 2)

        assert abs(p_expected - p_actual) <= 0.2
        assert abs(q_expected - q_actual) <= 0.2