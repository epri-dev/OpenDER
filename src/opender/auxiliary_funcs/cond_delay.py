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


class ConditionalDelay:
    """
    Conditional Delayed Enable can also be referred as On Delay.
    Output is true only when input stays true for a time period
    EPRI Report Reference: Section 3.11.4 in Report #3002021694: IEEE 1547-2018 DER Model
    """

    def __init__(self):
        self.con_del_enable_int = 0  # initialize timer
        self.con_del_enable_out = 0  # initialize output

    def con_del_enable(self, con_del_enable_in, con_del_enable_time):
        """
        Generate output when con_del_enable_in stays True for a period of con_del_enable_time

        Input argument:
        
        :param con_del_enable_in: Input Conditional Enable Boolean
        :param con_del_enable_time: Conditional delay time

        Internal state variable:
        
        :param con_del_enable_int: Elapsed time when Input Boolean con_del_enable_in stays True

        Output:
        
        :param con_del_enable_out: Conditional Delayed Enable Output
        """

        self.con_del_enable_int = min(con_del_enable_time, self.con_del_enable_int + der.DER.t_s)
        if con_del_enable_in == 0:
            self.con_del_enable_int = 0
            self.con_del_enable_out = 0
        elif self.con_del_enable_int >= con_del_enable_time:
            self.con_del_enable_out = 1
        return self.con_del_enable_out
