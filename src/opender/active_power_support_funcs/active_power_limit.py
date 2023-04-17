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

from opender.auxiliary_funcs.ramping import Ramping
from opender.auxiliary_funcs.time_delay import TimeDelay


class ActivePowerLimit:
    """
    Active Power Limit Function

    EPRI Report Reference: Section 3.7.1.2 in Report #3002026631: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_file, exec_delay):
        self.der_file = der_file
        self.exec_delay = exec_delay
        self.ap_limit_ramping = Ramping()
        self.ap_limit_delay = TimeDelay()

        self.ap_limit_pu = None     # Active power limit in per unit based on NP_P_MAX
        self.ap_limit_rt = None     # Actual active power limit for active power limit function, considering possible
                                    # ramp behavior and reaction time.

        self.ap_limit_ramp = None   # Active power limit function after ramp behavior before reaction time

    def calculate_ap_limit_rt(self):
        """
        Calculates and returns output active power limit in per unit

        Variable used in this function:
        :param ap_limit_exec:  Active power limit (AP_LIMIT) signal after execution delay
        :param AP_RT:	Active power limit response time
        :param NP_REACT_TIME:   DER grid support function reaction time

        Output:
        :param ap_limit_rt:	Active power limit
        """

        # Eq. 3.7.1-5, AP_LIMIT is based on NP_P_MAX if positive, and NP_P_MAX_CHARGE if negative. This is to
        # convert to a per-unit value based on NP_P_MAX.
        self.ap_limit_pu = self.exec_delay.ap_limit_exec if self.exec_delay.ap_limit_exec > 0 else \
                           self.exec_delay.ap_limit_exec * self.der_file.NP_P_MAX_CHARGE / self.der_file.NP_P_MAX

        # Eq. 3.7.1-6, The final power limitation is subjected to the response time. In this model a ramp rate limit
        # followed by a time delay (to model reaction time) is applied. Note that there can be multiple different ways
        # to implement this behavior in an actual DER.
        if self.exec_delay.ap_limit_enable_exec:
            self.ap_limit_ramp = self.ap_limit_ramping.ramp(self.ap_limit_pu, self.der_file.AP_RT - self.der_file.NP_REACT_TIME, self.der_file.AP_RT - self.der_file.NP_REACT_TIME)
        else:
            # If active power limit function is not enabled, the "limited active power" value is set to 1
            self.ap_limit_ramp = self.ap_limit_ramping.ramp(1, 0, 0)
        # Apply reaction time
        self.ap_limit_rt = self.ap_limit_delay.tdelay(self.ap_limit_ramp, self.der_file.NP_REACT_TIME)

        return self.ap_limit_rt
