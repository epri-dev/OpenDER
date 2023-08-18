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


from opender.auxiliary_funcs import low_pass_filter
from opender.auxiliary_funcs.flipflop import FlipFlop
from opender.auxiliary_funcs.time_delay import TimeDelay
from .frequency_droop import FreqDroop


class FreqDroopBESS(FreqDroop):
    """
    Frequency-droop Function for BESS DER
    EPRI Report Reference: Section 3.7.3.2 in Report #3002026631: IEEE 1547-2018 OpenDER Model
    """
    
    def __init__(self, der_obj):
        super(FreqDroopBESS, self).__init__(der_obj)

    def p_pf_normal_pu(self):
        # Eq 3.7.3-1, frequency-droop active power if no grid-support functions (freq-droop, volt-watt and active power
        # limit) are enabled is determined by the active power demand, rather than available active power
        if self.der_obj.der_status == 'Entering Service':
            return self.der_obj.p_out_w/self.der_file.NP_P_MAX
        else:
            return self.der_input.p_dem_pu

    def get_p_pu(self):
        # For initialization of p_pf_pre_pu_prev and p_out_w_prev (reference Table 3-21)
        return self.der_input.p_dem_pu
