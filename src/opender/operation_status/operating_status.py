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

import opender
from opender.operation_status.rt_crit import RideThroughCrit
from opender.operation_status.enter_service_crit.es_crit import EnterServiceCrit
from opender.operation_status.trip_crit.trip_crit import TripCrit


class OperatingStatus:
    """
    Determine DER operating status in terms of Trip, Continuous Operation, Mandatory Operation, etc.
    EPRI Report Reference: Section 3.5 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_obj):

        self.der_obj = der_obj
        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay
        self.der_input = der_obj.der_input

        if der_obj.der_file.STATUS_INIT:
            self.der_status = 'Continuous Operation'
        else:
            self.der_status = 'Trip'

        # Defining flag indicating the minimum ride-through time has passed, and the DER is in the
        # “may ride-through and may trip” region
        self.rt_pass_time_req = False

        self.ridethroughcrit = RideThroughCrit(der_obj)
        self.enterservicecrit = EnterServiceCrit(der_obj)
        self.tripcrit = TripCrit(der_obj)


    def determine_der_status(self):
        """
        Determine DER operating status in terms of Trip, Continuous Operation, Mandatory Operation, etc.
        EPRI Report Reference: Section 3.5.4 in Report #3002025583: IEEE 1547-2018 OpenDER Model

        :NP_P_MIN_PU:	DER minimum active power output
        :ES_RANDOMIZED_DELAY_ACTUAL:	Specified value for enter service randomized delay for simulation purpose
        :NP_P_MAX:  Active power maximum rating
        :NP_VA_MAX: Apparent power maximum rating
        :STATUS_INIT:   Initial DER Status
        """


        # Enter service criteria
        es_crit = self.enterservicecrit.es_decision()

        # Trip criteria
        trip_crit = self.tripcrit.trip_decision()

        # Ride-through criteria
        self.ridethroughcrit.determine_ride_through_mode()

        if self.der_status == 'Trip':
            if es_crit:
                if opender.der.DER.t_s <= self.der_file.ES_RAMP_RATE:
                    self.der_status = 'Entering Service'
                else:
                    self.der_status = 'Continuous Operation'

        if self.der_status == 'Entering Service':
            if self.der_obj.activepowerfunc.es_completed:
                self.der_status = 'Continuous Operation'

        if self.der_status != 'Trip':

            if self.ridethroughcrit.rt_mode_f == 'Not Defined':
                self.der_status = 'Not Defined'
            elif self.ridethroughcrit.rt_mode_v in ['Cease to Energize', 'Permissive Operation', 'Momentary Cessation']:
                self.der_status = self.ridethroughcrit.rt_mode_v

            elif self.ridethroughcrit.rt_mode_v == 'Mandatory Operation' or self.ridethroughcrit.rt_mode_f == 'Mandatory Operation':
                self.der_status = 'Mandatory Operation'
            else:
                if self.der_status != 'Entering Service':
                    self.der_status = 'Continuous Operation'
                self.rt_pass_time_req = False

        if trip_crit:
            self.der_status = 'Trip'

        return self.der_status

