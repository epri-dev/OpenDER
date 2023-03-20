# Copyright © 2023 Electric Power Research Institute, Inc. All rights reserved.
import cmath

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


from .der import DER
from .operation_status.enter_service_crit import EnterServiceCritPV
from .active_power_support_funcs.p_funcs_pv import DesiredActivePowerPV


class DER_PV(DER):
    def __init__(self, der_file_obj=None):
        super(DER_PV, self).__init__(der_file_obj)
        # Replace enter service module to include cut-in and cut-out behavior

        self.enterservicetrip = EnterServiceCritPV(self)
        self.activepowerfunc = DesiredActivePowerPV(self)


