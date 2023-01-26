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
    |  Voltage – Active Power (Volt-watt) Function
    |  EPRI Report Reference: Section 3.6.1 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_file, exec_delay, der_input):
        self.der_file = der_file
        self.exec_delay = exec_delay
        self.der_input = der_input
        self.pv_lpf = low_pass_filter.LowPassFilter()
        self.pv_delay = TimeDelay()

        self.p_pv_limit_ref_pu = None
        
    def calculate_p_pv_limit_pu(self, p_out_w):
        """
        Calculate active power limits by volt-watt function in per unit

        Variable used in this function:

        :param NP_P_MAX:    DER Active power discharge rating at unity power factor
        :param NP_P_MAX_CHARGE: DER active power charge rating
        :param v_meas_pu:	Applicable voltage for volt-var and volt-watt calculation
        :param pv_curve_p1_exec:	Volt-watt Curve Point P1 Setting (PV_CURVE_P1) signal after execution delay
        :param pv_curve_v1_exec:	Volt-watt Curve Point V1 Setting (PV_CURVE_V1) signal after execution delay
        :param pv_curve_p2_exec:	Volt-watt Curve Point P2 Setting (PV_CURVE_P2) signal after execution delay
        :param pv_curve_v2_exec:	Volt-watt Curve Point V2 Setting (PV_CURVE_V2) signal after execution delay
        :param pv_olrt_exec:	Volt-watt open loop response time setting (PV_OLRT) signal after execution delay

        Internal variable:
        
        :param p_pv_limit_ref_pu:	Volt-watt power limit reference in per-unit before open loop response time
        :param p_pv_limit_ref_w:   Volt-watt power limit reference in kW before open loop response time
        :param pv_curve_p1_w:  Volt-watt Curve Point P1 Setting in kW
        :param pv_curve_p2_w:  Volt-watt Curve Point P2 Setting in kW

        Output:
        
        :param p_pv_limit_pu:	Volt-watt power limit
        """

        # Eq. 3.7.1-1 calculate power references in W
        pv_curve_p1_w = self.exec_delay.pv_curve_p1_exec * self.der_file.NP_P_MAX
        pv_curve_p2_w = self.exec_delay.pv_curve_p2_exec * \
                    (self.der_file.NP_P_MAX if self.exec_delay.pv_curve_p2_exec > 0 else self.der_file.NP_P_MAX_CHARGE)

        # Eq. 3.7.1-2, calculate active power limit in kW according to volt-watt curve
        if self.der_input.v_meas_pu <= self.exec_delay.pv_curve_v1_exec:
            p_pv_limit_ref_w = pv_curve_p1_w
        if self.der_input.v_meas_pu >= self.exec_delay.pv_curve_v2_exec:
            p_pv_limit_ref_w = pv_curve_p2_w
        if self.exec_delay.pv_curve_v1_exec < self.der_input.v_meas_pu < self.exec_delay.pv_curve_v2_exec:
            p_pv_limit_ref_w = pv_curve_p1_w - (self.der_input.v_meas_pu - self.exec_delay.pv_curve_v1_exec) \
                                / (self.exec_delay.pv_curve_v2_exec-self.exec_delay.pv_curve_v1_exec) \
                                * (pv_curve_p1_w - pv_curve_p2_w)

        # Eq. 3.7.1-3, convert volt-watt limit to per-unit using NP_P_MAX as base
        self.p_pv_limit_ref_pu = p_pv_limit_ref_w / self.der_file.NP_P_MAX

        # Eq. 3.7.1-4, apply the low pass filter, if function disabled, reset limit to 1 immediately
        if self.exec_delay.pv_mode_enable_exec:
            p_pv_limit_lpf_pu = self.pv_lpf.low_pass_filter(self.p_pv_limit_ref_pu, self.exec_delay.pv_olrt_exec - self.der_file.NP_REACT_TIME)
        else:
            p_pv_limit_lpf_pu = self.pv_lpf.low_pass_filter(1, 0)

        p_pv_limit_pu = self.pv_delay.tdelay(p_pv_limit_lpf_pu, self.der_file.NP_REACT_TIME)

        return p_pv_limit_pu
