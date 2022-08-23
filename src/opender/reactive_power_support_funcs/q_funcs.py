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


# -*- coding: utf-8 -*-

from opender.auxiliary_funcs.ramping import Ramping
from opender.auxiliary_funcs.flipflop import FlipFlop
from opender.reactive_power_support_funcs import volt_var, watt_var, constant_vars, constant_pf


class DesiredReactivePower:
    """
    |  Desired Reactive Power Calculation
    |  EPRI Report Reference: Section 3.8 in Report #3002021694: IEEE 1547-2018 DER Model
    """

    def __init__(self, der_file, exec_delay, der_input):

        self.der_file = der_file
        self.exec_delay = exec_delay
        self.der_input = der_input

        # Enable conditions in previous values to detect mode changes
        self.const_pf_mode_enable_exec_prev = None      # Value of variable const_pf_mode_enable_exec in the previous time step  (initialized by the first value of CONST_PF_MODE_ENABLE)
        self.qv_mode_enable_exec_prev = None            # Value of variable qv_mode_enable_exec in the previous time step (initialized by the first value of QV_MODE_ENABLE)
        self.qp_mode_enable_exec_prev = None            # Value of variable qp_mode_enable_exec in the previous time step (initialized by the first value of QP_MODE_ENABLE)
        self.const_q_mode_enable_exec_prev = None       # Value of variable const_q_mode_enable_exec in the previous time step (initialized by the first value of CONST_Q_MODE_ENABLE)

        # Intermediate variables (Reactive power)
        self.q_qp_desired_kvar = None           # Output reactive power from watt-var function
        self.q_qv_desired_kvar = None           # Output reactive power from volt-var function
        self.q_const_q_desired_kvar = None      # Output reactive power from constant reactive power function
        self.q_const_pf_desired_kvar = None     # Output reactive power from constant power factor function

        self.q_mode_ramp_flag = 0

        self.constpf = constant_pf.ConstantPowerFactor(der_file, exec_delay)
        self.constq = constant_vars.ConstantVARs(der_file, exec_delay)
        self.voltvar = volt_var.VoltVAR(der_file, exec_delay, der_input)
        self.wattvar = watt_var.WattVAR(der_file, exec_delay)
        self.desired_kvar_ramp = Ramping()
        self.desired_kvar_ff = FlipFlop(0)


    def calculate_reactive_funcs(self, p_desired_kw, der_status):
        """
        Calculate desired reactive power for all 4 reactive power control modes defined in IEEE 1547-2018
        """

        # Constant power factor function
        self.q_const_pf_desired_kvar = self.constpf.calculate_q_const_pf_desired_kvar(p_desired_kw)

        # Constant reactive power function
        self.q_const_q_desired_kvar = self.constq.calculate_const_q_desired_kvar()

        # Volt-var function
        self.q_qv_desired_kvar = self.voltvar.calculate_q_qv_desired_kvar()

        # Watt-var function
        self.q_qp_desired_kvar = self.wattvar.calculate_q_qp_desired_kvar(p_desired_kw)

        # Calculate reactive power based on grid-support functions
        self.q_desired_kvar = self.calculate_desired_kvar(der_status)

        return self.q_desired_kvar


    def calculate_desired_kvar(self, der_status):
        """
        Calculate Desired reactive power considering the transition requirements defined by IEEE 1547-2018

        Other variables used in this function:
        
        :param const_pf_mode_enable_exec:	Constant Power Factor Mode Enable (CONST_PF_MODE_ENABLE) after execution delay
        :param qv_mode_enable_exec:	Voltage-Reactive Power Mode Enable (QV_MODE_ENABLE) after execution delay
        :param qp_mode_enable_exec:	Active Power Reactive Power Mode Enable (QP_MODE_ENABLE) after execution delay
        :param const_q_mode_enable_exec:	Constant Reactive Power Mode Enable (CONST_Q_MODE_ENABLE) after execution delay
        :param der_status:	Status of DER (ON or OFF)
        :param NP_VA_MAX:	Apparent power maximum rating
        :param P_MODE_TRANSITION_TIME:	Time for DER to smoothly transition between reactive power support modes

        Internal variables:
        
        :param q_desired_ref_kvar:	Desired output reactive power reference from reactive power support functions before ramp rate limit for mode transitions
        :param q_desired_ramp_kvar:	Desired output reactive power reference from reactive power support functions after ramp rate limit for mode transitions
        :param q_mode_ramp_flag:	Flag to determine pass through ramp rate limited reactive power during mode transition or not ramp rate limited value
        :param q_mode_ramp_flag_set:	Set value to create flipflop logic of variable q_mode_ramp_flag
        :param q_mode_ramp_flag_reset:	Reset value to create flipflop logic of variable q_mode_ramp_flag

        Output:
        
        :param q_desired_kvar:	Desired output reactive power from reactive power support functions
        """

        # Eq. 3.9.1-18, calculate desired reactive power reference, without smooth mode transition
        if(der_status == 1 and self.exec_delay.const_pf_mode_enable_exec == 1):
            q_desired_ref_kvar = self.q_const_pf_desired_kvar
        elif(der_status == 1 and self.exec_delay.qv_mode_enable_exec == 1):
            q_desired_ref_kvar = self.q_qv_desired_kvar
        elif(der_status == 1 and self.exec_delay.qp_mode_enable_exec == 1):
            q_desired_ref_kvar = self.q_qp_desired_kvar
        elif(der_status == 1 and self.exec_delay.const_q_mode_enable_exec == 1):
            q_desired_ref_kvar = self.q_const_q_desired_kvar
        else:
            q_desired_ref_kvar = 0

        # Eq. 3.9.1-19, the ramp rate limit only applies when there is a mode change.
        if self.exec_delay.const_pf_mode_enable_exec != self.const_pf_mode_enable_exec_prev or \
                self.exec_delay.qv_mode_enable_exec != self.qv_mode_enable_exec_prev or \
                self.exec_delay.qp_mode_enable_exec != self.qp_mode_enable_exec_prev or \
                self.exec_delay.const_q_mode_enable_exec != self.const_q_mode_enable_exec_prev:
            q_mode_ramp_flag_set = 1
        else:
            q_mode_ramp_flag_set = 0

        if q_mode_ramp_flag_set or self.q_mode_ramp_flag == 1:
            # Eq. 3.9.1-20, apply the ramp rate limit
            q_desired_ramp_kvar = self.der_file.NP_VA_MAX * \
                                  self.desired_kvar_ramp.ramp(q_desired_ref_kvar/self.der_file.NP_VA_MAX,
                                                              self.der_file.NP_MODE_TRANSITION_TIME,
                                                              self.der_file.NP_MODE_TRANSITION_TIME)
        else:
            # Eq. 3.9.1-21, if not in mode transition, ramp time of 0 is used to allow q_desired_ramp_kvar follow the
            # desired reactive power
            q_desired_ramp_kvar = self.der_file.NP_VA_MAX * \
                                  self.desired_kvar_ramp.ramp(q_desired_ref_kvar/self.der_file.NP_VA_MAX, 0, 0)

        # Eq. 3.9.1-22, the ramp rate limit stops to apply when the mode transition is completed (value before and
        # after ramp rate limit is the same
        if q_desired_ref_kvar == q_desired_ramp_kvar or der_status == 0:
            q_mode_ramp_flag_reset = 1
        else:
            q_mode_ramp_flag_reset = 0

        # Eq. 3.9.1-23, apply the flipflop logic to decide if in mode transition
        self.q_mode_ramp_flag = self.desired_kvar_ff.flipflop(q_mode_ramp_flag_set, q_mode_ramp_flag_reset)

        # Eq. 3.9.1-24, if in mode transition, pass ramp rate limited value as output. If not, pass original value.
        if self.q_mode_ramp_flag == 1:
            q_desired_kvar = q_desired_ramp_kvar
        else:
            q_desired_kvar = q_desired_ref_kvar

        # Save the values in for calculation in next time step
        self.const_pf_mode_enable_exec_prev = self.exec_delay.const_pf_mode_enable_exec
        self.qv_mode_enable_exec_prev = self.exec_delay.qv_mode_enable_exec
        self.qp_mode_enable_exec_prev = self.exec_delay.qp_mode_enable_exec
        self.const_q_mode_enable_exec_prev = self.exec_delay.const_q_mode_enable_exec

        return q_desired_kvar

    def __str__(self):
        return f"q_qv = {self.q_qv_desired_kvar}, q_const_pf = {self.q_const_pf_desired_kvar}, " \
               f"q_qp = {self.q_qp_desired_kvar}, q_const_q = {self.q_const_q_desired_kvar}"




