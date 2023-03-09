# Copyright © 2022 Electric Power Research Institute, Inc. All rights reserved.

# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met: 
# · Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# · Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# · Neither the name of the EPRI nor the names of its contributors may be used 
#   to endorse or promote products derived from this software without specific
#   prior written permission.


import pytest

# volt-watt function
input_list = [  # v_pu, theta, p, q, i_expected
    ([1.01,1.01,1.01], [0.0, -2.0943951023931953, 2.0943951023931953], 1, 0, [0.9900990099009901, 0.9900990099009901, 0.9900990099009901], [0.0, -2.0943951023931953, 2.0943951023931953]),
    (0.99, [0.5, -1.5943951023931953, 2.5943951023931953], 1, 0, [1.0101010101010102, 1.0101010101010102, 1.0101010101010102], [0.5, -1.5943951023931953, 2.5943951023931953]),
    ([1.01,1.01,1.01], [0.0, -2.0943951023931953, 2.0943951023931953], -1, 0, [0.9900990099009901, 0.9900990099009901, 0.9900990099009901], [3.141592653589793, 1.047197551196598, -1.047197551196598]),
    ([1,1,1], [0.0, -2.0943951023931953, 2.0943951023931953], 0.5, 0.5, [0.7071067811865476, 0.7071067811865475, 0.7071067811865475],[-0.7853981633974483, -2.8797932657906435, 1.308996938995747]),
    ([1,1,1], [0.0, -2.0943951023931953, 2.0943951023931953], -0.5, -0.5, [0.7071067811865476, 0.7071067811865475, 0.7071067811865475],[2.356194490192345, 0.2617993877991497, -1.8325957145940464]),
    ([1.02,1,1], [0.0, -2.0943951023931953, 2.0943951023931953], 0,1, [0.9933774834437085, 0.9933774834437084, 0.9933774834437084],[-1.5707963267948966, 2.6179938779914944, 0.5235987755982987]),

]


class TestISource:

    @pytest.fixture(autouse=True)
    def _request(self, bess_obj_creation):
        self.si_obj = bess_obj_creation

    @pytest.mark.parametrize("v_pu, theta, p, q, i_expected, theta_expected", input_list,
                             ids=[f"I Source - v_pu={i[0]}, theta={i[1]}, p={i[2]}, q={i[3]}, i_expected={i[4]}, "
                                  f"theta_expected={i[5]}" for i in input_list])
    def test_i_source(self, v_pu, theta, p, q, i_expected, theta_expected):

        self.si_obj.der_file.NP_Q_MAX_INJ = 100000
        self.si_obj.der_file.NP_Q_MAX_ABS = 100000
        self.si_obj.der_file.initialize_NP_Q_CAPABILTY_BY_P_CURVE()

        self.si_obj.der_file.NP_PHASE = "THREE"
        self.si_obj.der_file.CONST_Q_MODE_ENABLE = "ENABLED"
        self.si_obj.der_file.CONST_Q = q


        self.si_obj.update_der_input(p_dem_pu=p, v_pu=v_pu, theta=theta)
        self.si_obj.run()
        i_model, theta_model = self.si_obj.get_der_output(output='I_pu')
        # print(i_model,theta_model)
        for i in range(3):
            assert abs(i_model[i] - i_expected[i]) < 0.001
            assert abs(theta_model[i] - theta_expected[i]) < 0.001
