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


from opender.active_power_support_funcs.p_funcs import DesiredActivePower

from .frequency_droop_bess import FreqDroopBESS
from opender import DER


class DesiredActivePowerBESS(DesiredActivePower):
    """
    Desired active power calculation from active power support functions for BESS DER
    EPRI Report Reference: Section 3.7.3 in Report #3002030962: IEEE 1547-2018 OpenDER Model
    """
    def __init__(self, der_obj):
        super(DesiredActivePowerBESS, self).__init__(der_obj)

        self.freqdroop = FreqDroopBESS(self.der_obj)

        self.p_act_supp_bess_pu = None      # Desired output active power from active power support functions in per
                                            # unit without considering the BESS related constraints
        self.p_es_dem_pu = None             # Active power demand considering enter service ramp

    def calculate_p_desired_pu(self, p_out_w):
        """
        Based on the calculated values from volt-watt, frequency-droop, active power limit, and enter service ramp,
        their enabling signal, and DER operating status, generate the DER desired active power output. Specifically
        for BESS DER, the State of Charge (SoC) and limitation of output active power due to SoC is considered.
        EPRI Report Reference: Section 3.7.3.3 in Report #3002030962: IEEE 1547-2018 OpenDER Model

        Variable used in this function:
        :param ap_limit_enable_exec:	Active power limit enable (AP_LIMIT_ENABLE) signal after execution delay
        :param pv_mode_enable_exec:	    Volt-watt enable (PV_MODE_ENABLE) signal after execution delay
        :param der_status:	Status of DER (Trip, Entering Service, etc)
        :param NP_P_MAX_CHARGE:	DER active power charge rating
        :param NP_P_MAX:	    Active power rating at unity power factor
        :param p_dem_pu:        BESS DER active power demand in pu
        """

        #TODO reordered logic to allow: enter service ramp has higher priority
        # Eq 3.7.3-7, calculate desired active power without considering BESS SoC related constraints
        if self.exec_delay.ap_limit_enable_exec == False and self.exec_delay.pv_mode_enable_exec == False \
                and self.pf_uf_active == False and self.pf_of_active == False:
            self.p_act_supp_bess_pu = min(self.der_obj.bessspecific.p_dem_ramp_pu, 1)
        if self.exec_delay.ap_limit_enable_exec == True and self.exec_delay.pv_mode_enable_exec == False \
                and self.pf_uf_active == False and self.pf_of_active == False:
            self.p_act_supp_bess_pu = min(self.der_obj.bessspecific.p_dem_ramp_pu, self.ap_limit_rt, 1)
        if self.exec_delay.ap_limit_enable_exec == False and self.exec_delay.pv_mode_enable_exec == True \
                and self.pf_uf_active == False and self.pf_of_active == False:
            self.p_act_supp_bess_pu = min(self.der_obj.bessspecific.p_dem_ramp_pu, self.p_pv_limit_pu, 1)
        if self.exec_delay.ap_limit_enable_exec == True and self.exec_delay.pv_mode_enable_exec == True \
                and self.pf_uf_active == False and self.pf_of_active == False:
            self.p_act_supp_bess_pu = min(self.ap_limit_rt, self.p_pv_limit_pu, 1)
        if self.exec_delay.pv_mode_enable_exec == False and self.pf_of_active == True:
            self.p_act_supp_bess_pu = min(self.der_input.p_dem_pu, self.p_pf_pu, 1)
        if self.exec_delay.pv_mode_enable_exec == True and self.pf_of_active == True:
            self.p_act_supp_bess_pu = min(self.der_input.p_dem_pu, self.p_pv_limit_pu, self.p_pf_pu, 1)
        if self.exec_delay.pv_mode_enable_exec == False and self.pf_uf_active == True:
            self.p_act_supp_bess_pu = min(self.p_pf_pu, 1)
        if self.exec_delay.pv_mode_enable_exec == True and self.pf_uf_active == True:
            self.p_act_supp_bess_pu = min(self.p_pv_limit_pu, self.p_pf_pu, 1)


        # Eq 3.7.3-6, calculate active power demand considering enter service ramp
        self.p_es_dem_pu = max(min(self.p_act_supp_bess_pu , self.p_es_pu), -self.p_es_pu)

        # Eq. 3.7.3-8, calculate desired active power, considering maximum limits by SOC, DER nameplate active
        # power charge rating, and active power demand from system operator or higher level grid support functions
        #TODO double check logic - grid support functions should already been addressed earlier.
        self.p_desired_pu = max(-self.der_obj.bessspecific.soc_calc.p_max_charge_pu,
                                -self.der_file.NP_P_MAX_CHARGE / self.der_file.NP_P_MAX,
                                min(self.der_obj.bessspecific.soc_calc.p_max_discharge_pu, self.p_es_dem_pu))


        return self.p_desired_pu

