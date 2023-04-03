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


# -*- coding: utf-8 -*-

import opender
from opender.operation_status.enter_service_crit import EnterServiceCritPV
from opender.operation_status.trip_crit import TripCritPV
from .operating_status import OperatingStatus


class OperatingStatusPV(OperatingStatus):
    """
    Determine Overall DER operating status for PV DER
    EPRI Report Reference: Section 3.5.2 in Report #3002026631: IEEE 1547-2018 OpenDER Model
    """
    def __init__(self, der_obj: opender.DER):
        super(OperatingStatusPV, self).__init__(der_obj)

        # Update enter service criteria and trip criteria based on available power.
        self.enterservicecrit = EnterServiceCritPV(der_obj)
        self.tripcrit = TripCritPV(der_obj)