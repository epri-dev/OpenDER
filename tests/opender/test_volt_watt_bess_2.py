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
import opender

input_list = [  # p_dc, p_expected, q_expected
    (1.05, 100, 100),
    (1.07, 100, 65),
    (1.09, 100, -5),
]


class TestVWBESS2:


    @pytest.mark.parametrize("v_pu, p_kw, p_expected", input_list,
                             )
    def test_volt_watt_bess_2(self, v_pu, p_kw, p_expected):
        self.si_obj = opender.DER_BESS()
        self.si_obj.der_file.PV_MODE_ENABLE = True

        self.si_obj.der_file.PV_CURVE_P2 = -0.5
        self.si_obj.der_file.NP_P_MAX_CHARGE = 80000
        self.si_obj.der_file.NP_APPARENT_POWER_CHARGE_MAX = 80000

        self.si_obj.update_der_input(p_dem_kw = p_kw, v_pu=v_pu, f=60)
        self.si_obj.run()

        assert abs(p_expected - self.si_obj.p_out_kw)<0.1