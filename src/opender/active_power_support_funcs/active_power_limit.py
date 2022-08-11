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

from opender.auxiliary_funcs.ramping import Ramping


class ActivePowerLimit:
    """
    Active Power Limit Function

    EPRI Report Reference: Section 3.6.2 in Report #3002021694: IEEE 1547-2018 DER Model
    """
    def __init__(self, der_file, exec_delay):
        self.der_file = der_file
        self.exec_delay = exec_delay
        self.ap_limit_ramp = Ramping()

    def calculate_ap_limit_pu(self):
        """
        Calculates and returns output active power limit in per unit

        Variable used in this function:

        :param ap_limit_exec:  Active power limit (AP_LIMIT) signal after execution delay
        :param AP_RT:	Active power limit response time

        |  Output:
        :param ap_limit_pu:	Active power limit
        """

        # Eq: 3.6.1-5, The final power limitation is subjected to the response time. In this model a ramp rate limit
        # is applied. Note that there can be multiple different ways to implement this behavior in an actual DER.
        # The model may be updated in a future version according to the lab test results.
        # If active power limit function is not enabled, the "limited active power" value is set to 1
        if self.exec_delay.ap_limit_enable_exec:
            ap_limit_pu = self.ap_limit_ramp.ramp(self.exec_delay.ap_limit_exec,self.der_file.AP_RT, self.der_file.AP_RT)
        else:
            ap_limit_pu = self.ap_limit_ramp.ramp(1, 0, 0)

        # ap_limit_pu = self.ap_limit_ramp.ramp(exec_delay.ap_limit_exec, der_file.AP_RT, der_file.AP_RT)

        return ap_limit_pu
            
