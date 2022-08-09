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
        self.si_obj.der_file.NP_P_MAX_CHARGE = 80
        self.si_obj.der_file.NP_APPARENT_POWER_CHARGE_MAX = 80

        self.si_obj.update_der_input(p_dem_kw = p_kw, v_pu=v_pu, f=60)
        self.si_obj.run()

        assert abs(p_expected - self.si_obj.p_out_kw)<0.1