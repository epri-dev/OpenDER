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
input_list = [  # v_pu, theta, p, q, i_expected
    ([1.01,1.01,1.01], [0.0, -2.0943951023931953, 2.0943951023931953], 1, 0, [1.0302003796700552, 1.0302003796700554, 1.0302003796700554] , [0.19341857582238942, -1.9009765265708056, 2.2878136782155845]),
    (0.99, [0.5, -1.5943951023931953, 2.5943951023931953], 1, 0, [1.0113917056849602, 1.0113917056849608, 1.0113917056849606] , [0.701097433058297, -1.393297669334898, 2.795492535451492]),
    ([1.01,1.01,1.01], [0.0, -2.0943951023931953, 2.0943951023931953], -1, 0, [1.028257177107131, 1.0282571771071312, 1.0282571771071314] , [-0.19378873949769743, -2.2881838418908926, 1.9006063628954977]),
    ([1,1,1], [0.0, -2.0943951023931953, 2.0943951023931953], 0.5, 0.5, [1.1049889139715383, 1.1049889139715388, 1.1049889139715385] , [0.09016828543780737, -2.004226816955388, 2.1845633878310022]),
    ([1,1,1], [0.0, -2.0943951023931953, 2.0943951023931953], -0.5, -0.5, [0.9049864639871689, 0.9049864639871693, 0.9049864639871692] , [-0.11016911871113287, -2.2045642211043277, 1.9842259836820622]),
    ([1.02,1,1], [0.0, -2.0943951023931953, 2.0943951023931953], 0,1, [1.2120092371142652, 1.2020278774297812, 1.2020183347387206] , [-0.0008196122308672668, -2.1000246855712787, 2.098371861873176]),

]


class TestVSource:

    @pytest.fixture(autouse=True)
    def _request(self, bess_obj_creation):
        self.si_obj = bess_obj_creation

    @pytest.mark.parametrize("v_pu, theta, p, q, v_expected, theta_expected", input_list,
                             ids=[f"I Source - v_pu={i[0]}, theta={i[1]}, p={i[2]}, q={i[3]}, v_expected={i[4]}, "
                                  f"theta_expected={i[5]}" for i in input_list])
    def test_v_source(self, v_pu, theta, p, q, v_expected, theta_expected):

        self.si_obj.der_file.NP_Q_MAX_INJ = 100000
        self.si_obj.der_file.NP_Q_MAX_ABS = 100000
        self.si_obj.der_file.initialize_NP_Q_CAPABILTY_BY_P_CURVE()

        self.si_obj.der_file.NP_PHASE = "THREE"
        self.si_obj.der_file.CONST_Q_MODE_ENABLE = "ENABLED"
        self.si_obj.der_file.CONST_Q = q


        self.si_obj.update_der_input(p_dem_pu=p, v_pu=v_pu, theta=theta)
        self.si_obj.run()
        v_model, theta_model = self.si_obj.get_der_output(output='V_pu')
        # print(v_model,',',theta_model)
        for i in range(3):
            assert abs(v_model[i] - v_expected[i]) < 0.001
            assert abs(theta_model[i] - theta_expected[i]) < 0.001
