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


from opender import der


class TimeDelay:
    """
    |  Time delay function
    |  EPRI Report Reference: Section 3.12.3 in Report #3002021694: IEEE 1547-2018 DER Model
    """
    
    def __init__(self):
        self.tdelay_in_prev = None
        self.tdelay_out_hold = None
        self.tdelay_in_value = []
        self.tdelay_in_time = []
    
    def tdelay(self,tdelay_in, tdelay_time):
        """
        Time delay function

        Input:
        
        :param tdelay_in: Value to be time delayed
        :param tdelay_time: Time delay time

        Output:
        
        :param tdelay_out: Time delayed value
        """
        if self.tdelay_in_prev is None:
            self.tdelay_in_prev = tdelay_in
        if self.tdelay_out_hold is None:
            self.tdelay_out_hold = tdelay_in

        if tdelay_time < der.DER.t_s:
            tdelay_out = tdelay_in
            self.tdelay_out_hold = tdelay_in
            self.tdelay_in_value = []
            self.tdelay_in_time = []

        elif tdelay_time > 0 and tdelay_time >= der.DER.t_s:

            if self.tdelay_in_time:
                self.tdelay_in_time = [item - der.DER.t_s for item in self.tdelay_in_time]

                # If there is an element in the time array tdelay_in_time is less than 0,
                # it indicates the time delay has passed
                for x in self.tdelay_in_time:
                    if x <= 0:
                        # index - position of the first occurrence of the elapsed time
                        index = self.tdelay_in_time.index(x)
                        self.tdelay_out_hold = self.tdelay_in_value[index]
                        del self.tdelay_in_time[index]
                        del self.tdelay_in_value[index]
            
        if tdelay_in is not None:
            if tdelay_in != self.tdelay_in_prev:
                self.tdelay_in_value.append(tdelay_in)
                self.tdelay_in_time.append(tdelay_time)
                self.tdelay_in_prev = tdelay_in
            
        tdelay_out = self.tdelay_out_hold
        
        return tdelay_out
    

                
        
        