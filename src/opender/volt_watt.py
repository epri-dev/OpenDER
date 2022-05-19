"""
Copyright © 2022 Electric Power Research Institute, Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met: 
· Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
· Redistributions in binary form must reproduce the above copyright notice, 
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
· Neither the name of the EPRI nor the names of its contributors may be used 
  to endorse or promote products derived from this software without specific
  prior written permission.
"""


# -*- coding: utf-8 -*-
"""

@author: Jithendar Anandan
@email: janandan@epri.com
"""
from .low_pass_filter import LowPassFilter

class VoltWatt:
    """
    Voltage – Active Power (Volt-watt) Function
    EPRI Report Reference: Section 3.6.1 in Report #3002021694: IEEE 1547-2018 DER Model
    """

    def __init__(self):
        self.pv_olrt = LowPassFilter()
        
    def calculate_p_pv_limit_pu(self, der_file, exec_delay, der_input, p_out_kw):
        """
        Calculate active power limits by volt-watt function in per unit

        Variable used in this function:
        :v_meas_pu:	Applicable voltage for volt-var and volt-watt calculation
        :pv_curve_p1_exec:	Volt-watt Curve Point P1 Setting (PV_CURVE_P1) signal after execution delay
        :pv_curve_v1_exec:	Volt-watt Curve Point V1 Setting (PV_CURVE_V1) signal after execution delay
        :pv_curve_p2_exec:	Volt-watt Curve Point P2 Setting (PV_CURVE_P2) signal after execution delay
        :pv_curve_v2_exec:	Volt-watt Curve Point V2 Setting (PV_CURVE_V2) signal after execution delay
        :pv_olrt_exec:	Volt-watt open loop response time setting (PV_OLRT) signal after execution delay

        Internal variable:
        :p_pv_limit_ref_pu:	Volt-watt power limit reference before open loop response time

        Output:
        :p_pv_limit_pu:	Volt-watt power limit
        """
        
        #Eq 19, calculate active power limit according to volt-watt curve
        if(der_input.v_meas_pu <= exec_delay.pv_curve_v1_exec):
            p_pv_limit_ref_pu = exec_delay.pv_curve_p1_exec
        if(der_input.v_meas_pu >= exec_delay.pv_curve_v2_exec):
            p_pv_limit_ref_pu = exec_delay.pv_curve_p2_exec
        if(der_input.v_meas_pu > exec_delay.pv_curve_v1_exec and der_input.v_meas_pu < exec_delay.pv_curve_v2_exec):
            p_pv_limit_ref_pu = exec_delay.pv_curve_p1_exec - (der_input.v_meas_pu - exec_delay.pv_curve_v1_exec)/(exec_delay.pv_curve_v2_exec-exec_delay.pv_curve_v1_exec) * (exec_delay.pv_curve_p1_exec - exec_delay.pv_curve_p2_exec)



        #Eq 20, apply the low pass filter
        if exec_delay.pv_mode_enable_exec:
            p_pv_limit_pu = self.pv_olrt.low_pass_filter(p_pv_limit_ref_pu, exec_delay.pv_olrt_exec)
        else:
            p_pv_limit_pu = self.pv_olrt.low_pass_filter(1, 0)

        return p_pv_limit_pu