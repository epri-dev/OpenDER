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


from opender.active_power_support_funcs import active_power_limit, frequency_droop, volt_watt as vw
from opender.active_power_support_funcs.p_funcs import DesiredActivePower


class DesiredActivePowerPV(DesiredActivePower):
    """
    Calculate desired active power according to volt-watt, frequency-droop, and active power limit functions
    EPRI Report Reference: Section 3.6 in Report #3002021694: IEEE 1547-2018 DER Model
    """

    def __init__(self, der_obj):

        super(DesiredActivePowerPV, self).__init__(der_obj)

        # self.aplimit = active_power_limit.ActivePowerLimit(self.der_file, self.exec_delay)
        # self.voltwatt = vw.VoltWatt(self.der_file, self.exec_delay, self.der_input)
