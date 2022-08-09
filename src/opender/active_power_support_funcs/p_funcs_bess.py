from opender.active_power_support_funcs.p_funcs import DesiredActivePower
from opender.active_power_support_funcs.bess_specifc.soc import StateOfCharge

class DesiredActivePowerBESS(DesiredActivePower):
    def __init__(self, der_file, exec_delay, der_input):
        super(DesiredActivePowerBESS, self).__init__(der_file, exec_delay, der_input)
        self.soc_calc = StateOfCharge(der_file)

    def calculate_p_act_supp_kw(self, p_out_kw):
        """
        Calculate desired active power according to volt-watt, frequency-droop, and active power limit functions
        EPRI Report Reference: Section 3.6.4 in Report #3002021694: IEEE 1547-2018 DER Model
        """

        # Calculate SoC
        self.soc_calc.calculate_soc(p_out_kw)

        # Calculate P limits
        self.soc_calc.calculate_p_max_by_soc()

        # Calculate active power based on grid-support functions
        # Eq. 27 calculate desired active power in per unit
        if(self.exec_delay.ap_limit_enable_exec == False and self.exec_delay.pv_mode_enable_exec == False and self.pf_uf_active == False and self.pf_of_active == False):
            p_act_supp_pu = min(self.der_input.p_dem_pu, 1)

        if(self.exec_delay.ap_limit_enable_exec == True and self.exec_delay.pv_mode_enable_exec == False and self.pf_uf_active == False and self.pf_of_active == False):
            p_act_supp_pu = min(self.der_input.p_dem_pu, self.ap_limit_pu, 1)

        if(self.exec_delay.ap_limit_enable_exec == False and self.exec_delay.pv_mode_enable_exec == True and self.pf_uf_active == False and self.pf_of_active == False):
            p_act_supp_pu = min(self.der_input.p_dem_pu, self.p_pv_limit_pu, 1)

        if(self.exec_delay.ap_limit_enable_exec == True and self.exec_delay.pv_mode_enable_exec == True and self.pf_uf_active == False and self.pf_of_active == False):
            p_act_supp_pu = min(self.der_input.p_dem_pu, self.ap_limit_pu, self.p_pv_limit_pu, 1)

        if(self.exec_delay.pv_mode_enable_exec == False and self.pf_of_active == True):
            p_act_supp_pu = min(self.der_input.p_dem_pu, self.p_pf_pu, 1)

        if(self.exec_delay.pv_mode_enable_exec == True and self.pf_of_active == True):
            p_act_supp_pu = min(self.der_input.p_dem_pu, self.p_pv_limit_pu, self.p_pf_pu, 1)

        if(self.exec_delay.pv_mode_enable_exec == False and self.pf_uf_active == True):
            p_act_supp_pu = min(self.p_pf_pu, 1)

        if(self.exec_delay.pv_mode_enable_exec == True and self.pf_uf_active == True):
            p_act_supp_pu = min(self.p_pv_limit_pu, self.p_pf_pu, 1)

        # Eq. 28 calculate desired active power in kW
        self.p_act_supp_kw = max(-self.soc_calc.p_max_charge_pu, min(p_act_supp_pu, self.soc_calc.p_max_discharge_pu)) * self.der_file.NP_P_MAX



        return self.p_act_supp_kw
