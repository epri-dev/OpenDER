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



# -*- coding: utf-8 -*-

import math
from opender.auxiliary_funcs.low_pass_filter import LowPassFilter
from opender.auxiliary_funcs.time_delay import TimeDelay


class ConstantPowerFactor:
    """
    Constant Power Factor Function
    EPRI Report Reference: Section 3.8.1 in Report #3002026631: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_obj):

        self.der_obj = der_obj
        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay
        self.pf_lpf = LowPassFilter()
        self.pf_delay = TimeDelay()

        self.q_const_pf_desired_ref_pu = 0  # Constant power factor reactive power reference before response time
        self.q_const_pf_lpf_pu = 0          # Constant power factor reactive power reference after first order lag
        self.q_const_pf_desired_pu = 0      # Output reactive power from constant power factor function

    def calculate_q_const_pf_desired_var(self, p_desired_pu):
        """
        Calculates and returns output reactive power from Constant Power Factor function

        Variable used in this function:
        :param p_desired_pu:  Desired output active power considering DER enter service performance
        :param const_pf_exec:  Constant Power Factor Setting (CONST_PF) after execution delay
        :param const_pf_excitation_exec:  Constant Power Factor Excitation (CONST_PF_EXCITATION) after execution delay
        :param CONST_PF_RT:   Constant Power Factor Mode Response Time
        :param NP_REACT_TIME:   DER grid support function reaction time

        Output:
        :param q_const_pf_desired_pu:	Output reactive power from constant power factor function
        """

        # Eq 3.8.1-1, calculate reactive power reference according to active power and constant power factor setting
        if self.exec_delay.const_pf_excitation_exec == "INJ":
            self.q_const_pf_desired_ref_pu = p_desired_pu * self.der_file.NP_P_MAX \
                                 * (math.sqrt(1 - (self.exec_delay.const_pf_exec ** 2))/self.exec_delay.const_pf_exec) \
                                 / self.der_file.NP_VA_MAX
        elif self.exec_delay.const_pf_excitation_exec == "ABS":
            self.q_const_pf_desired_ref_pu = -p_desired_pu * self.der_file.NP_P_MAX \
                                 * (math.sqrt(1 - (self.exec_delay.const_pf_exec ** 2))/self.exec_delay.const_pf_exec) \
                                 / self.der_file.NP_VA_MAX

        # Eq 3.8.1-2, apply the low pass filter and time delay (to model reaction time) to the reference reactive
        # power. Note that there can be multiple  different ways to implement this behavior in an actual DER.
        # The model may be updated in a future version, according to the lab test results.
        self.q_const_pf_lpf_pu = self.pf_lpf.low_pass_filter(self.q_const_pf_desired_ref_pu, self.der_file.CONST_PF_RT - self.der_file.NP_REACT_TIME)
        self.q_const_pf_desired_pu = self.pf_delay.tdelay(self.q_const_pf_lpf_pu, self.der_file.NP_REACT_TIME)

        return self.q_const_pf_desired_pu
