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


from opender.auxiliary_funcs import low_pass_filter
from opender.auxiliary_funcs.flipflop import FlipFlop
from opender.auxiliary_funcs.time_delay import TimeDelay
from .frequency_droop import FreqDroop


class FreqDroopBESS(FreqDroop):
    """
    Frequency-droop Function
    EPRI Report Reference: Section 3.6.3 in Report #3002021694: IEEE 1547-2018 DER Model
    """
    
    def __init__(self, der_obj):
        super(FreqDroopBESS, self).__init__(der_obj)

    def active_power_without_droop(self):
        return self.der_input.p_dem_pu
