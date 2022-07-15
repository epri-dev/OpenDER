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
from opender import der
class Ramping:
    """
    |  Ramp rate limit function
    |  EPRI Report Reference: Section 3.11.2 in Report #3002021694: IEEE 1547-2018 DER Model
    """
    
    def __init__(self):
        self.ramp_out_prev = None
        
    def ramp(self, ramp_in, ramp_up_time, ramp_down_time):
        """
        Calculate ramp rate limit with ramp-up and ramp-down time settings
        
        :param ramp_in: Ramp rate limit input
        :param ramp_up_time: Ramp up time from 0 to 1
        :param ramp_down_time: Ramp down time from 0 to 1
        :param t_s:   Simulation timestep

        Output:
        
        :param ramp_out: Ramp rate limited result
        """

        if(self.ramp_out_prev is None):
            self.ramp_out_prev = ramp_in
        ramp_out = None

        # Eq. 73 and 74, apply ramp rate limit
        if(ramp_up_time != 0):
            ramp_up_limit = der.DER.t_s / ramp_up_time
            if ((self.ramp_out_prev + ramp_up_limit) < ramp_in):
                ramp_out = self.ramp_out_prev + ramp_up_limit

        if(ramp_down_time != 0):
            ramp_down_limit = der.DER.t_s / ramp_down_time
            if ((self.ramp_out_prev - ramp_down_limit) > ramp_in):
                ramp_out = self.ramp_out_prev - ramp_down_limit

        if ramp_out is None:
            ramp_out = ramp_in

        self.ramp_out_prev = ramp_out

        return ramp_out
        
        
