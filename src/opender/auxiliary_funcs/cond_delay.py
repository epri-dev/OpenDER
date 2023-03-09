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

from opender import der


class ConditionalDelay:
    """
    Conditional Delayed Enable can also be referred as On Delay.
    Output is true only when input stays true for a time period
    EPRI Report Reference: Section 3.12.4 in Report #3002025583: IEEE 1547-2018 OpenDER Model
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

        if con_del_enable_in == 0:
            # Eq. 3.12.4-2 If input is False, output is False, and elapsed time does not integrate
            self.con_del_enable_int = 0
            self.con_del_enable_out = 0
        else:
            # Eq. 3.12.4-3 If input is True, elapsed time adds simulation time step in each time step
            self.con_del_enable_int = min(con_del_enable_time, self.con_del_enable_int + der.DER.t_s)
            if self.con_del_enable_int >= con_del_enable_time:
                # Eq. 3.12.4-4 If elapsed time passed the conditional delay time, the output turns True
                self.con_del_enable_out = 1

        return self.con_del_enable_out
