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


from opender.auxiliary_funcs.low_pass_filter import LowPassFilter


class ConstantVARs:
    """
    Constant Reactive Power (var) Function
    EPRI Report Reference: Section 3.9.4 in Report #3002021694: IEEE 1547-2018 DER Model
    """

    def __init__(self, der_file, exec_delay):
        self.der_file = der_file
        self.exec_delay = exec_delay

        self.const_q_lpf = LowPassFilter()

    def calculate_const_q_desired_kvar(self):
        """
        Calculates and returns output reactive power from Constant Power Factor function

        Variable used in this function:
        
        :param const_q_exec:	Constant Reactive Power Setting (CONST_Q) after execution delay
        :param CONST_Q_RT:	Constant Reactive Power Mode Response Time
        :param NP_VA_MAX:	Apparent power maximum rating

        Internal variable:
        
        :param q_const_q_desired_ref_kvar:	Constant reactive power reactive power reference before response time

        Output:
        
        :param q_const_q_desired_kvar"	Output reactive power from constant reactive power function
        """

        # Eq. 3.9.1-16, calculate desired reactive power in unit of kvar
        const_q_desired_ref_kvar = self.exec_delay.const_q_exec * self.der_file.NP_VA_MAX

        # Eq. 3.9.1-17, apply the low pass filter to the reference reactive power. Note that there can be multiple
        # different ways to implement this behavior in an actual DER. The model may be updated in a future version,
        # according to the lab test results.
        const_q_desired_kvar = self.const_q_lpf.low_pass_filter(const_q_desired_ref_kvar, self.der_file.CONST_Q_RT)

        return const_q_desired_kvar
