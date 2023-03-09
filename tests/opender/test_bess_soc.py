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
from opender.der_bess import DER_BESS
import opender

P_MAX_CURVE={
    'P_DISCHARGE_MAX_PU': [0.2, 1],
    'SOC_P_DISCHARGE_MAX': [0, 0.5],
    'P_CHARGE_MAX_PU': [1, 0.2],
    'SOC_P_CHARGE_MAX': [0.5, 1]
}

input_list = [  # p_dc, p_limit, p_expected, q_expected
    (10, None, 1, 0, 0, False),
    (10, None, -1, 0, 0, False),
    (10, P_MAX_CURVE, 1, 0, 0, False),
    (10, P_MAX_CURVE, -1, 0, 0, False),
    (900, None, 1, 0, 0, False),
    (900, None, -1, 0, 0, False),
    (900, P_MAX_CURVE, 1, 0, 0, False),
    (900, P_MAX_CURVE, -1, 0, 0, False),
    (10, None, 1, 100, 100, False),
    (10, None, -1, 100, 100, False),
    (10, P_MAX_CURVE, 1, 100, 100, False),
    (10, P_MAX_CURVE, -1, 100, 100, False),
    (900, None, 1, 100, 100, False),
    (900, None, -1, 100, 100, False),
    (900, P_MAX_CURVE, 1, 100, 100, False),
    (900, P_MAX_CURVE, -1, 100, 100, False),
    (10, None, -1, 0, 0, True),
    (10, P_MAX_CURVE, 1, 0, 0, True),
]

class TestSoC:

    @pytest.mark.parametrize("t_s, NP_BESS_P_MAX_BY_SOC, p_dem_pu, NP_BESS_SELF_DISCHARGE, NP_BESS_SELF_DISCHARGE_SOC, PV_ENABLE", input_list)
    def test_soc(self, t_s, NP_BESS_P_MAX_BY_SOC, p_dem_pu, NP_BESS_SELF_DISCHARGE, NP_BESS_SELF_DISCHARGE_SOC, PV_ENABLE):

        opender.der.DER.t_s = t_s
        der_obj = DER_BESS()
        der_obj.der_file.NP_BESS_CAPACITY = 25000
        if NP_BESS_P_MAX_BY_SOC is not None:
            der_obj.der_file.NP_BESS_P_MAX_BY_SOC = NP_BESS_P_MAX_BY_SOC
        der_obj.der_file.NP_BESS_SELF_DISCHARGE = NP_BESS_SELF_DISCHARGE
        der_obj.der_file.NP_BESS_SELF_DISCHARGE_SOC = NP_BESS_SELF_DISCHARGE_SOC

        der_obj.der_file.PV_MODE_ENABLE = PV_ENABLE
        der_obj.der_file.PV_CURVE_P2 = -1

        der_obj.update_der_input(f=60, p_dem_pu=p_dem_pu)
        der_obj.update_der_input(v_pu=1.09)
        t = 0
        while t < 2000:
            der_obj.run()
            t = t + t_s
            # print(der_obj.activepowerfunc.soc_calc)
            # print(der_obj)
        assert 0 <= der_obj.activepowerfunc.soc_calc.bess_soc <= 1

        opender.der.DER.t_s = 1000000

#python -m pytest -p no:warning