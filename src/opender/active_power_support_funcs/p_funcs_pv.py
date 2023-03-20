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


from opender.active_power_support_funcs.p_funcs import DesiredActivePower


class DesiredActivePowerPV(DesiredActivePower):
    """
    Desired active power calculation from active power support functions for PV DER
    EPRI Report Reference: Section 3.7.2 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_obj):
        # No additional changes needed for PV DER
        super(DesiredActivePowerPV, self).__init__(der_obj)
