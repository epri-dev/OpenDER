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

import math
from opender.auxiliary_funcs.low_pass_filter import LowPassFilter


class ConstantPowerFactor:
    """
    |  Constant Power Factor Function
    |  EPRI Report Reference: Section 3.9.1 in Report #3002021694: IEEE 1547-2018 DER Model
    """

    def __init__(self, der_file, exec_delay):
        self.der_file = der_file
        self.exec_delay = exec_delay
        self.pf_lpf = LowPassFilter()

    def calculate_q_const_pf_desired_kvar(self, p_desired_kw):
        """
        Calculates and returns output reactive power from Constant Power Factor function

        Variable used in this function:

        :param p_desired_kw:  Desired output active power considering DER enter service performance
        :param const_pf_exec:  Constant Power Factor Setting (CONST_PF) after execution delay
        :param const_pf_excitation_exec:  Constant Power Factor Excitation (CONST_PF_EXCITATION) after execution delay
        :param CONST_PF_RT:   Constant Power Factor Mode Response Time

        Internal Variables:
        
        :param q_const_pf_desired_ref_kvar:	Constant power factor reactive power reference before response time

        Output:
        
        :param q_const_pf_desired_kvar:	Output reactive power from constant power factor function
        """

        # Eq. 3.9.1-1, calculate reactive power reference according to  active power and constant power factor setting
        if self.exec_delay.const_pf_excitation_exec == "INJ":
            q_const_pf_desired_ref_kvar = p_desired_kw * \
                                          (math.sqrt(1 - (self.exec_delay.const_pf_exec ** 2))/self.exec_delay.const_pf_exec)
        elif self.exec_delay.const_pf_excitation_exec == "ABS":
            q_const_pf_desired_ref_kvar = -p_desired_kw * \
                                          (math.sqrt(1 - (self.exec_delay.const_pf_exec ** 2))/self.exec_delay.const_pf_exec)
        else:
            print(f'CONST_PF_EXCITATION value unexpected:{self.exec_delay.const_pf_excitation_exec}')
            q_const_pf_desired_ref_kvar = 0

        # Eq. 3.9.1-2, apply the low pass filter to the reference reactive power. Note that there can be multiple
        # different ways to implement this behavior in an actual DER. The model may be updated in a future version,
        # according to the lab test results.
        q_const_pf_desired_kvar = self.pf_lpf.low_pass_filter(q_const_pf_desired_ref_kvar, self.der_file.CONST_PF_RT)

        return q_const_pf_desired_kvar
