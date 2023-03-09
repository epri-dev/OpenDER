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
    (1.01, 0, 1, 0, [0.9900990099009901], [0]),
    (1.01, 0.5, 1, 0, [0.9900990099009901], [0.5]),
    (0.99, 0, 1, 0, [1.0101010101010102], [0]),
    (0.99, 0.5, 1, 0, [1.0101010101010102], [0.5]),
    (1.01, 0, -1, 0, [0.9900990099009901], [3.141592653589793]),
    (1.01, 0, 0.5, 0.5, [0.7001057239470767], [-0.7853981633974483]),
    (1.01, 0, 0.5, -0.5, [0.7001057239470767], [0.7853981633974483]),
    (0.99, 0, -0.5, -0.5, [0.7142492739258056], [2.356194490192345]),
    (0.99, 0.5, -0.5, -0.5, [0.7142492739258056], [2.856194490192345]),
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

        self.si_obj.der_file.NP_PHASE = "SINGLE"
        self.si_obj.der_file.CONST_Q_MODE_ENABLE = "ENABLED"
        self.si_obj.der_file.CONST_Q = q

        self.si_obj.update_der_input(p_dem_pu=p, v_pu=v_pu, theta=theta)
        self.si_obj.run()
        i_model, theta_model = self.si_obj.get_der_output(output='I_pu')
        # print(i_model,theta_model)
        assert abs(i_model[0] - i_expected[0]) < 0.001
        assert abs(theta_model[0] - theta_expected[0]) < 0.001
