import pytest
import opender

input_list = [  # p_dc, p_expected, q_expected

    (-10, -10, 0),
    (-30, -30, 0),
    (-50, -50, 11),
    (-70, -70, 33),
    (-90, -71.9, 35.09),
    (-100, -71.9, 35.09),
    (10, 10, 0),
    (30, 30, 0),
    (50, 50, 0),
    (70, 70, -17.6),
    (90, 90, -35.2),
    (100, 92.68, -37.56)

]


class TestWVBESS2:


    @pytest.mark.parametrize("p_dc, p_expected, q_expected", input_list,
                             )
    def test_watt_var_bess_2(self, p_dc, p_expected, q_expected):
        self.si_obj = opender.DER_BESS()
        self.si_obj.der_file.QP_MODE_ENABLE = True

        self.si_obj.der_file.NP_P_MAX_CHARGE = 80000
        self.si_obj.der_file.NP_APPARENT_POWER_CHARGE_MAX = 80000

        self.si_obj.update_der_input(p_dem_kw=p_dc, v_pu=1, f=60)
        self.si_obj.run()

        assert abs(p_expected - self.si_obj.p_out_kw)<0.1
        assert abs(q_expected - self.si_obj.q_out_kvar)<0.1