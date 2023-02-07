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


"""
@author: Jithendar Anandan
@email: janandan@epri.com
"""
from opender.auxiliary_funcs import low_pass_filter
from opender.auxiliary_funcs.time_delay import TimeDelay


class VoltWatt:
    """
    Voltage – Active Power (Volt-watt) Function
    EPRI Report Reference: Section 3.7.1.1 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_file, exec_delay, der_input):
        self.der_file = der_file
        self.exec_delay = exec_delay
        self.der_input = der_input
        self.pv_lpf = low_pass_filter.LowPassFilter()
        self.pv_delay = TimeDelay()

        self.pv_curve_p1_w = None       # Volt-watt Curve Point P1 Setting in W
        self.pv_curve_p2_w = None       # Volt-watt Curve Point P2 Setting in W
        self.p_pv_limit_ref_w = None    # Volt-watt power limit reference in W before open loop response time
        self.p_pv_limit_ref_pu = None   # Volt-watt power limit reference in per-unit before open loop response time
        self.p_pv_limit_lpf_pu = None   # Volt-watt power limit reference in per unit after low pass filter, before reaction time

        self.p_pv_limit_pu = None       # Volt-watt power limit in per unit based on NP_P_MAX

    def calculate_p_pv_limit_pu(self):
        """
        Calculate active power limits by volt-watt function in per unit

        Variable used in this function:
        :param NP_P_MAX:            DER Active power discharge rating at unity power factor
        :param NP_P_MAX_CHARGE:     DER active power charge rating
        :param v_meas_pu:	        Applicable voltage for volt-var and volt-watt calculation
        :param pv_curve_p1_exec:	Volt-watt Curve Point P1 Setting (PV_CURVE_P1) signal after execution delay
        :param pv_curve_v1_exec:	Volt-watt Curve Point V1 Setting (PV_CURVE_V1) signal after execution delay
        :param pv_curve_p2_exec:	Volt-watt Curve Point P2 Setting (PV_CURVE_P2) signal after execution delay
        :param pv_curve_v2_exec:	Volt-watt Curve Point V2 Setting (PV_CURVE_V2) signal after execution delay
        :param pv_olrt_exec:	    Volt-watt open loop response time setting (PV_OLRT) signal after execution delay
        :param NP_REACT_TIME:       DER grid support function reaction time
        :param pv_mode_enable_exec:	Volt-watt enable (PV_MODE_ENABLE) signal after execution delay

        Output:
        :param p_pv_limit_pu:	Volt-watt power limit
        """

        # Eq. 3.7.1-1 calculate power references in W
        self.pv_curve_p1_w = self.exec_delay.pv_curve_p1_exec * self.der_file.NP_P_MAX
        self.pv_curve_p2_w = self.exec_delay.pv_curve_p2_exec * \
                    (self.der_file.NP_P_MAX if self.exec_delay.pv_curve_p2_exec > 0 else self.der_file.NP_P_MAX_CHARGE)

        # Eq. 3.7.1-2, calculate active power limit in kW according to volt-watt curve
        if self.der_input.v_meas_pu <= self.exec_delay.pv_curve_v1_exec:
            self.p_pv_limit_ref_w = self.pv_curve_p1_w
        if self.der_input.v_meas_pu >= self.exec_delay.pv_curve_v2_exec:
            self.p_pv_limit_ref_w = self.pv_curve_p2_w
        if self.exec_delay.pv_curve_v1_exec < self.der_input.v_meas_pu < self.exec_delay.pv_curve_v2_exec:
            self.p_pv_limit_ref_w = self.pv_curve_p1_w - (self.der_input.v_meas_pu - self.exec_delay.pv_curve_v1_exec) \
                                / (self.exec_delay.pv_curve_v2_exec-self.exec_delay.pv_curve_v1_exec) \
                                * (self.pv_curve_p1_w - self.pv_curve_p2_w)

        # Eq. 3.7.1-3, convert volt-watt limit to per-unit using NP_P_MAX as base
        self.p_pv_limit_ref_pu = self.p_pv_limit_ref_w / self.der_file.NP_P_MAX

        # Eq. 3.7.1-4, apply the low pass filter and reaction time delay,
        # if function disabled, reset limit to 1 immediately
        if self.exec_delay.pv_mode_enable_exec:
            self.p_pv_limit_lpf_pu = self.pv_lpf.low_pass_filter(self.p_pv_limit_ref_pu, self.exec_delay.pv_olrt_exec - self.der_file.NP_REACT_TIME)
        else:
            self.p_pv_limit_lpf_pu = self.pv_lpf.low_pass_filter(1, 0)
        self.p_pv_limit_pu = self.pv_delay.tdelay(self.p_pv_limit_lpf_pu, self.der_file.NP_REACT_TIME)

        return self.p_pv_limit_pu
