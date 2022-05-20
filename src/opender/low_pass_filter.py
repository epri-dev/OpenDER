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

from . import der
class LowPassFilter:
    """
    |  Low pass filter for modeling DER open loop response behavior and other related responses
    |  EPRI Report Reference: Section 3.11.1 in Report #3002021694: IEEE 1547-2018 DER Model
    """
    
    def __init__(self):
        self.lpf_in_prev = None
        self.lpf_out_prev = None
    
    def low_pass_filter(self, lpf_in, t_olrt):
        """
        Calculate low pass filtered result of lpt_in with Open Loop Response Time of t_olrt
        
        Input:
        
        :param lpf_in:    Input of Low pass filter
        :param t_olrt:    Open loop response time
        :param t_s:       Simulation time step

        Output:
        
        :param lpf_out:   Low pass filtered result
        """
        if self.lpf_in_prev == None:
            self.lpf_in_prev = lpf_in

        if self.lpf_out_prev == None:
            self.lpf_out_prev = lpf_in

        if(t_olrt < (1.15 * der.DER.t_s)):
            lpf_out = lpf_in
        else:
            # Eq. 71, apply first order lag
            t_olrt_t = t_olrt/1.15
            lpf_out = ((der.DER.t_s / (der.DER.t_s + t_olrt_t)) * (lpf_in + self.lpf_in_prev)) + ((t_olrt_t - der.DER.t_s) / (
                        der.DER.t_s + t_olrt_t) * self.lpf_out_prev)
        self.lpf_in_prev = lpf_in
        self.lpf_out_prev = lpf_out
        return lpf_out
        

