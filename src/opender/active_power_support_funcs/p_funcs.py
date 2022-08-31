# Copyright © 2022 Electric Power Research Institute, Inc. All rights reserved.

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


from opender.active_power_support_funcs import active_power_limit, frequency_droop, volt_watt as vw


class DesiredActivePower:
    """
    Calculate desired active power according to volt-watt, frequency-droop, and active power limit functions
    EPRI Report Reference: Section 3.6 in Report #3002021694: IEEE 1547-2018 DER Model
    """

    def __init__(self, der_file, exec_delay, der_input):

        self.der_file = der_file
        self.exec_delay = exec_delay
        self.der_input = der_input

        # Intermediate variables (Active power)
        self.pf_uf_active = None
        self.pf_of_active = None
        self.p_pf_pu = None
        self.p_act_supp_pu = None
        self.p_act_supp_w = None
        self.p_desired_w = None
        self.ap_limit_rt = None
        self.p_pv_limit_pu = None

        self.aplimit = active_power_limit.ActivePowerLimit(self.der_file, self.exec_delay)
        self.voltwatt = vw.VoltWatt(self.der_file, self.exec_delay, self.der_input)
        self.freqwatt = frequency_droop.FreqDroop(self.der_file, self.exec_delay, self.der_input)

    def calculate_p_funcs(self, p_out_w):
        """
        :param ap_limit_rt:	Active power limit
        :param p_pv_limit_pu:	Volt-watt power limit
        :param p_pf_pu:	Frequency-droop power command
        :param ap_limit_enable_exec:	Active power limit enable (AP_LIMIT_ENABLE) signal after execution delay
        :param pv_mode_enable_exec:	Volt-watt enable (PV_MODE_ENABLE) signal after execution delay
        :param pf_of_active:	Frequency-droop over-frequency active
        :param pf_uf_active:	Frequency-droop under-frequency active
        :param p_dc_pu:	DER available DC power in pu
        :param NP_EFFICIENCY:	DER system efficiency for DC/AC power conversion

        Internal variable:
        
        :param p_act_supp_pu:	Desired output active power from active power support functions in per unit

        Output
        
        :param p_act_supp_w:	Desired output active power from active power support functions in kW
        """

        # Active power limit function
        self.ap_limit_rt = self.aplimit.calculate_ap_limit_rt()

        # Volt-watt function
        self.p_pv_limit_pu = self.voltwatt.calculate_p_pv_limit_pu(p_out_w)

        # Frequency-droop function
        self.p_pf_pu, self.pf_uf_active, self.pf_of_active = self.freqwatt.calculate_p_pf_pu(p_out_w, self.ap_limit_rt,
                                                                                             self.p_pv_limit_pu)

        self.calculate_p_act_supp_pu(p_out_w)

        return self.p_act_supp_pu

    def calculate_p_act_supp_pu(self, p_out_w):
        """
        Calculate desired active power according to volt-watt, frequency-droop, and active power limit functions
        EPRI Report Reference: Section 3.6.4 in Report #3002021694: IEEE 1547-2018 DER Model
        """
        # Calculate active power based on grid-support functions

        # Eq. 3.7.1-14 calculate desired active power in per unit
        if self.exec_delay.ap_limit_enable_exec == False and self.exec_delay.pv_mode_enable_exec == False \
                and self.pf_uf_active == False and self.pf_of_active == False:
            self.p_act_supp_pu = min(self.der_input.p_avl_pu, 1)

        if self.exec_delay.ap_limit_enable_exec == True and self.exec_delay.pv_mode_enable_exec == False \
                and self.pf_uf_active == False and self.pf_of_active == False:
            self.p_act_supp_pu = min(self.der_input.p_avl_pu, self.ap_limit_rt, 1)

        if self.exec_delay.ap_limit_enable_exec == False and self.exec_delay.pv_mode_enable_exec == True \
                and self.pf_uf_active == False and self.pf_of_active == False:
            self.p_act_supp_pu = min(self.der_input.p_avl_pu, self.p_pv_limit_pu, 1)

        if (self.exec_delay.ap_limit_enable_exec == True and self.exec_delay.pv_mode_enable_exec == True
                and self.pf_uf_active == False and self.pf_of_active == False):
            self.p_act_supp_pu = min(self.der_input.p_avl_pu, self.ap_limit_rt, self.p_pv_limit_pu, 1)

        if self.exec_delay.pv_mode_enable_exec == False and self.pf_of_active == True:
            self.p_act_supp_pu = min(self.der_input.p_avl_pu, self.p_pf_pu, 1)

        if self.exec_delay.pv_mode_enable_exec == True and self.pf_of_active == True:
            self.p_act_supp_pu = min(self.der_input.p_avl_pu, self.p_pv_limit_pu, self.p_pf_pu, 1)

        if self.exec_delay.pv_mode_enable_exec == False and self.pf_uf_active == True:
            self.p_act_supp_pu = min(self.der_input.p_avl_pu, self.p_pf_pu, 1)

        if self.exec_delay.pv_mode_enable_exec == True and self.pf_uf_active == True:
            self.p_act_supp_pu = min(self.der_input.p_avl_pu, self.p_pv_limit_pu, self.p_pf_pu, 1)

        return self.p_act_supp_pu

    def __str__(self):
        return f"ap_limit_rt = {self.ap_limit_rt}, p_pv_limit_pu = {self.p_pv_limit_pu}, p_pf_pu = {self.p_pf_pu}, p_act_supp_pu = {self.p_act_supp_pu}"
