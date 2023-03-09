# Copyright © 2023 Electric Power Research Institute, Inc. All rights reserved.

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
input_list = [  # v_pu, theta, p, q, v_expected
    (1.01, 0, 1, 0, [1.0302003796700554], [0.19341857582238936]),
    (1.01, 0.5, 1, 0, [1.0302003796700554] , [0.6934185758223894]),
    (0.99, 0, 1, 0, [1.0113917056849604] , [0.2010974330582972]),
    (0.99, 0.5, 1, 0,[1.0113917056849604] , [0.7010974330582972]),
    (1.01, 0, -1, 0, [1.0282571771071312] , [-0.1937887394976974]),
    (1.01, 0, 0.5, 0.5, [1.1138700153681143] , [0.08855947262031855]),
    (1.01, 0, 0.5, -0.5, [0.9169004368720538] , [0.10873733419472296]),
    (0.99, 0, -0.5, -0.5, [0.8941513245330271] , [-0.11264077625157796]),
    (0.99, 0.5, -0.5, -0.5, [0.8941513245330271] , [0.38735922374842197]),
]


class TestVSource:

    @pytest.fixture(autouse=True)
    def _request(self, bess_obj_creation):
        self.si_obj = bess_obj_creation

    @pytest.mark.parametrize("v_pu, theta, p, q, v_expected, theta_expected", input_list,
                             ids=[f"V Source - v_pu={i[0]}, theta={i[1]}, p={i[2]}, q={i[3]}, v_expected={i[4]}, "
                                  f"theta_expected={i[5]}" for i in input_list])
    def test_i_source(self, v_pu, theta, p, q, v_expected, theta_expected):

        self.si_obj.der_file.NP_Q_MAX_INJ = 100000
        self.si_obj.der_file.NP_Q_MAX_ABS = 100000
        self.si_obj.der_file.initialize_NP_Q_CAPABILTY_BY_P_CURVE()

        self.si_obj.der_file.NP_PHASE = "SINGLE"
        self.si_obj.der_file.CONST_Q_MODE_ENABLE = "ENABLED"
        self.si_obj.der_file.CONST_Q = q

        self.si_obj.update_der_input(p_dem_pu=p, v_pu=v_pu, theta=theta)
        self.si_obj.run()
        v_model, theta_model = self.si_obj.get_der_output(output='V_pu')
        # print(v_model,',',theta_model)
        assert abs(v_model[0] - v_expected[0]) < 0.001
        assert abs(theta_model[0] - theta_expected[0]) < 0.001
