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
from .low_pass_filter import LowPassFilter


class ConstantPowerFactor:
    """
    |  Constant Power Factor Function
    |  EPRI Report Reference: Section 3.8.1 in Report #3002021694: IEEE 1547-2018 DER Model
    """

    def __init__(self):
        self.pf_olrt = LowPassFilter()

    def calculate_q_const_pf_desired_kvar(self,der_file, exec_delay, p_desired_kw):
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

        #Eq. 35, calculate reactive power reference according to desired active power and constant power factor setting
        if(exec_delay.const_pf_excitation_exec == "INJ"):
            q_const_pf_desired_ref_kvar = p_desired_kw * (math.sqrt(1 - (exec_delay.const_pf_exec * exec_delay.const_pf_exec))/exec_delay.const_pf_exec)

        if(exec_delay.const_pf_excitation_exec == "ABS"):
            q_const_pf_desired_ref_kvar = p_desired_kw * (math.sqrt(1 - (exec_delay.const_pf_exec * exec_delay.const_pf_exec))/exec_delay.const_pf_exec)
            q_const_pf_desired_ref_kvar = -q_const_pf_desired_ref_kvar

        '''
        Eq. 36, apply the low pass filter to the reference reactive power. Note that there can be multiple different 
        ways to implement this behavior in an actual DER. The model may be updated in a future version, according to the
        lab test results.
        '''
        q_const_pf_desired_kvar = self.pf_olrt.low_pass_filter(q_const_pf_desired_ref_kvar, der_file.CONST_PF_RT)

        return q_const_pf_desired_kvar