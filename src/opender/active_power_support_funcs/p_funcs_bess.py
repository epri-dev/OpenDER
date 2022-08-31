from opender.active_power_support_funcs.p_funcs import DesiredActivePower
from opender.bess_specifc.soc import StateOfCharge
from opender import DER


class DesiredActivePowerBESS(DesiredActivePower):
    def __init__(self, der_file, exec_delay, der_input):
        super(DesiredActivePowerBESS, self).__init__(der_file, exec_delay, der_input)
        self.soc_calc = StateOfCharge(der_file)
        self.p_act_supp_bess_pu = None

    def calculate_p_act_supp_pu(self, p_out_w):
        """
        Calculate desired active power according to volt-watt, frequency-droop, and active power limit functions
        EPRI Report Reference: Section 3.6.4 in Report #3002021694: IEEE 1547-2018 DER Model
        """

        if DER.t_s <= 7200 and self.der_file.NP_BESS_CAPACITY is not None:
            # For time series simulation
            # Calculate SoC
            self.soc_calc.calculate_soc(p_out_w)

            # Calculate P limits
            self.soc_calc.calculate_p_max_by_soc()
        else:
            # For snapshot analysis
            self.soc_calc.snapshot_limits()

        # Eq. 3.7.3-1 calculate desired active power in per unit
        if self.exec_delay.ap_limit_enable_exec == False and self.exec_delay.pv_mode_enable_exec == False \
                and self.pf_uf_active == False and self.pf_of_active == False:
            self.p_act_supp_bess_pu = min(self.der_input.p_dem_pu, 1)

        if self.exec_delay.ap_limit_enable_exec == True and self.exec_delay.pv_mode_enable_exec == False \
                and self.pf_uf_active == False and self.pf_of_active == False:
            self.p_act_supp_bess_pu = min(self.der_input.p_dem_pu, self.ap_limit_rt, 1)

        if self.exec_delay.ap_limit_enable_exec == False and self.exec_delay.pv_mode_enable_exec == True \
                and self.pf_uf_active == False and self.pf_of_active == False:
            self.p_act_supp_bess_pu = min(self.der_input.p_dem_pu, self.p_pv_limit_pu, 1)

        if self.exec_delay.ap_limit_enable_exec == True and self.exec_delay.pv_mode_enable_exec == True \
                and self.pf_uf_active == False and self.pf_of_active == False:
            self.p_act_supp_bess_pu = min(self.ap_limit_rt, self.p_pv_limit_pu, 1)

        if self.exec_delay.pv_mode_enable_exec == False and self.pf_of_active == True:
            self.p_act_supp_bess_pu = min(self.p_pf_pu, 1)

        if self.exec_delay.pv_mode_enable_exec == True and self.pf_of_active == True:
            self.p_act_supp_bess_pu = min(self.der_input.p_dem_pu, self.p_pv_limit_pu, self.p_pf_pu, 1)

        if self.exec_delay.pv_mode_enable_exec == False and self.pf_uf_active == True:
            self.p_act_supp_bess_pu = min(self.p_pf_pu, 1)

        if self.exec_delay.pv_mode_enable_exec == True and self.pf_uf_active == True:
            self.p_act_supp_bess_pu = min(self.p_pv_limit_pu, self.p_pf_pu, 1)

        # Eq. 3.7.3-2 calculate desired active power in kW, considering maximum limits by SOC, DER nameplate active
        # power charge rating, and active power demand from system operator or higher level grid support functions
        self.p_act_supp_pu = max(-self.soc_calc.p_max_charge_pu,
                                 -self.der_file.NP_P_MAX_CHARGE / self.der_file.NP_P_MAX,
                                 min(self.p_act_supp_bess_pu, self.soc_calc.p_max_discharge_pu))

        return self.p_act_supp_w
