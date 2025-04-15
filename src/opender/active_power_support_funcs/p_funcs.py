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


from opender.active_power_support_funcs import active_power_limit, frequency_droop, volt_watt, es_perf


class DesiredActivePower:
    """
    Desired active power calculation from active power support functions
    EPRI Report Reference: Section 3.7 in Report #3002030962: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_obj):

        self.der_obj = der_obj
        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay
        self.der_input = der_obj.der_input

        # Intermediate variables
        self.pf_uf_active = None        # Frequency-droop under-frequency condition active
        self.pf_of_active = None        # Frequency-droop over-frequency condition active
        self.p_pf_pu = None             # Active power from frequency droop function
        self.ap_limit_rt = None         # Active power limit from active power limit function
        self.p_pv_limit_pu = None       # Active power limit from volt-watt function
        self.p_es_pu = None             # Active power reference from enter service ramp requirements
        if self.der_file.STATUS_INIT:
            self.es_completed = True    # Flag to indicate enter service has completed
        else:
            self.es_completed = False
        self.p_desired_pu = None        # Desired active power from all active power support functions

        self.aplimit = active_power_limit.ActivePowerLimit(self.der_file, self.exec_delay)
        self.voltwatt = volt_watt.VoltWatt(self.der_file, self.exec_delay, self.der_input)
        self.freqdroop = frequency_droop.FreqDroop(self.der_obj)
        self.enterserviceperf = es_perf.EnterServicePerformance(der_obj)

    def calculate_p_funcs(self, p_out_w):
        """
        Call active power support functions and based on the results, generate desired active power output

        Output:
        :param p_desired_pu:	Desired output active power from active power support functions in per unit
        """

        if self.der_obj.der_status != 'Trip':

            # Active power limit function
            self.ap_limit_rt = self.aplimit.calculate_ap_limit_rt()

            # Volt-watt function
            self.p_pv_limit_pu = self.voltwatt.calculate_p_pv_limit_pu()

            # Frequency-droop function
            self.p_pf_pu, self.pf_uf_active, self.pf_of_active = self.freqdroop.calculate_p_pf_pu(p_out_w,
                                                                                                  self.ap_limit_rt,
                                                                                                  self.p_pv_limit_pu)
            # Enter service ramp performance
            self.p_es_pu = self.enterserviceperf.es_performance()

            # Calculate final desired active power based on other functions
            self.p_desired_pu = self.calculate_p_desired_pu(p_out_w)

            # Eq 3.7.1-19, if the enter service ramp reference is greater than 1,
            # it is considered that the DER enter service is completed.
            if self.p_es_pu > 1:
                self.es_completed = True

        else:
            # Eq 3.7.1-20, if DER is not in service, the desired active power should be 0, and it is not considered
            # that enter service is completed
            self.p_desired_pu = 0
            self.es_completed = False
            self.freqdroop.reset()
            self.voltwatt.reset()
            self.enterserviceperf.reset()
            self.aplimit.reset()

        return self.p_desired_pu

    def calculate_p_desired_pu(self, p_out_w):
        """
        Based on the calculated values from volt-watt, frequency-droop, active power limit, and enter service ramp,
        their enabling signal, and DER operating status, generate the DER desired active power output
        EPRI Report Reference: Section 3.7.1.5 in Report #3002030962: IEEE 1547-2018 OpenDER Model

        Variable used in this function:
        :param ap_limit_enable_exec:	Active power limit enable (AP_LIMIT_ENABLE) signal after execution delay
        :param pv_mode_enable_exec:	    Volt-watt enable (PV_MODE_ENABLE) signal after execution delay
        :param der_status:	Status of DER (Trip, Entering Service, etc)
        :param p_avl_pu:    DER available active power in per unit considering efficiency
        """

        # Eq 3.7.1-18, calculate desired active power in per unit based on the enabling signals from the
        # grid-support functions
        if self.exec_delay.ap_limit_enable_exec == False and self.exec_delay.pv_mode_enable_exec == False \
                and self.pf_uf_active == False and self.pf_of_active == False:
            self.p_desired_pu = min(self.der_input.p_avl_pu, self.p_es_pu, 1)

        if self.exec_delay.ap_limit_enable_exec == True and self.exec_delay.pv_mode_enable_exec == False \
                and self.pf_uf_active == False and self.pf_of_active == False:
            self.p_desired_pu = min(self.der_input.p_avl_pu, self.p_es_pu, self.ap_limit_rt, 1)

        if self.exec_delay.ap_limit_enable_exec == False and self.exec_delay.pv_mode_enable_exec == True \
                and self.pf_uf_active == False and self.pf_of_active == False:
            self.p_desired_pu = min(self.der_input.p_avl_pu, self.p_es_pu, self.p_pv_limit_pu, 1)

        if (self.exec_delay.ap_limit_enable_exec == True and self.exec_delay.pv_mode_enable_exec == True
                and self.pf_uf_active == False and self.pf_of_active == False):
            self.p_desired_pu = min(self.der_input.p_avl_pu, self.ap_limit_rt, self.p_pv_limit_pu, 1)

        if self.exec_delay.pv_mode_enable_exec == False and self.pf_of_active == True:
            self.p_desired_pu = min(self.der_input.p_avl_pu, self.p_pf_pu, 1)

        if self.exec_delay.pv_mode_enable_exec == True and self.pf_of_active == True:
            self.p_desired_pu = min(self.der_input.p_avl_pu, self.p_pv_limit_pu, self.p_pf_pu, 1)

        if self.exec_delay.pv_mode_enable_exec == False and self.pf_uf_active == True:
            self.p_desired_pu = min(self.der_input.p_avl_pu, self.p_pf_pu, 1)

        if self.exec_delay.pv_mode_enable_exec == True and self.pf_uf_active == True:
            self.p_desired_pu = min(self.der_input.p_avl_pu, self.p_pv_limit_pu, self.p_pf_pu, 1)

        return self.p_desired_pu

    def __str__(self):
        return f"ap_limit_rt = {self.ap_limit_rt}, p_pv_limit_pu = {self.p_pv_limit_pu}, p_pf_pu = {self.p_pf_pu}, p_desired_pu = {self.p_desired_pu}"

    def bess_specific(self):
        pass