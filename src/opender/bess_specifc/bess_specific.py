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

from opender.der import DER
from opender.bess_specifc.soc import StateOfCharge
from opender.auxiliary_funcs.ramping import Ramping

class BESSspecific:
    """
    State of Charge related Models for Battery Energy Storage System (BESS) DERs
    EPRI Report Reference: Section 3.6 in Report #3002030962: IEEE 1547-2018 OpenDER Model
    """
    def __init__(self, der_obj):

        self.der_obj = der_obj
        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay
        self.der_input = der_obj.der_input

        self.soc_calc = StateOfCharge(self.der_file)
        self.p_dem_ramp_pu = None       # Active power demand considering BESS ramp rate constraint

        self.p_dem_ramp = Ramping()

    def run(self):

        if DER.t_s <= 7200 and self.der_file.NP_BESS_CAPACITY is not None:
            # For time series simulation
            # Calculate SoC
            self.soc_calc.calculate_soc(self.der_obj.p_out_w)

            # Calculate P limits
            self.soc_calc.calculate_p_max_by_soc()
        else:
            # For snapshot analysis
            self.soc_calc.snapshot_limits()


        if self.der_obj.der_status != 'Trip':
            # 3.6.2-6, ramp rate limits considering battery operational constraints.
            self.p_dem_ramp_pu = self.p_dem_ramp.ramp(self.der_input.p_dem_pu, self.der_file.NP_BESS_P_RAMP_TIME, self.der_file.NP_BESS_P_RAMP_TIME)
        else:
            # 3.6.2-6, reset ramp rate limit when DER is tripped.
            self.p_dem_ramp_pu = self.p_dem_ramp.ramp(0 ,0 ,0)