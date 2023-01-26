from opender.active_power_support_funcs.p_funcs import DesiredActivePower
from opender.bess_specifc.soc import StateOfCharge
from .frequency_droop_bess import FreqDroopBESS
from .es_perf_bess import EnterServicePerformanceBESS
from opender import DER


class DesiredActivePowerBESS(DesiredActivePower):
    def __init__(self, der_obj):
        super(DesiredActivePowerBESS, self).__init__(der_obj)
        self.freqdroop = FreqDroopBESS(self.der_obj)
        self.soc_calc = StateOfCharge(self.der_file)
        self.enterserviceperf = EnterServicePerformanceBESS(der_obj)
        self.p_act_supp_bess_pu = None

    def calculate_p_desired_pu(self, p_out_w):
        """
        Calculate desired active power according to volt-watt, frequency-droop, and active power limit functions
        EPRI Report Reference: Section 3.6.4 in Report #3002025583: IEEE 1547-2018 OpenDER Model
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
        if self.der_obj.der_status != 'Trip':
            if self.der_input.p_dem_pu > 0:
                self.p_es_dem_pu = min(self.der_input.p_dem_pu, self.p_es_pu)
            else:
                self.p_es_dem_pu =  max(self.der_input.p_dem_pu, self.p_es_pu)

            if self.exec_delay.ap_limit_enable_exec == False and self.exec_delay.pv_mode_enable_exec == False \
                    and self.pf_uf_active == False and self.pf_of_active == False:
                self.p_act_supp_bess_pu = min(self.p_es_dem_pu, 1)

            if self.exec_delay.ap_limit_enable_exec == True and self.exec_delay.pv_mode_enable_exec == False \
                    and self.pf_uf_active == False and self.pf_of_active == False:
                self.p_act_supp_bess_pu = min(self.p_es_dem_pu, self.ap_limit_rt, 1)

            if self.exec_delay.ap_limit_enable_exec == False and self.exec_delay.pv_mode_enable_exec == True \
                    and self.pf_uf_active == False and self.pf_of_active == False:
                self.p_act_supp_bess_pu = min(self.p_es_dem_pu, self.p_pv_limit_pu, 1)

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
            self.p_desired_pu = max(-self.soc_calc.p_max_charge_pu,
                                    -self.der_file.NP_P_MAX_CHARGE / self.der_file.NP_P_MAX,
                                    min(self.p_act_supp_bess_pu, self.soc_calc.p_max_discharge_pu))

            if self.der_input.p_dem_pu > 0:
                if self.p_es_pu > self.p_desired_pu:
                    self.es_completed = True
            else:
                if self.p_es_pu < self.p_desired_pu:
                    self.es_completed = True
        else:
            self.p_desired_pu = 0
            self.es_completed = False

        return self.p_desired_pu
