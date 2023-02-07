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
    Determine Overall DER operating status in terms of Trip, Entering Service, Continuous Operation, etc.
    EPRI Report Reference: Section 3.5.1.4 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_obj):

        self.der_obj = der_obj
        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay
        self.der_input = der_obj.der_input

        # Initiating DER operation status, which could be Trip, Entering Service, Continuous Operation,
        # Momentary Cessation, Mandatory Operation, Permissive Operation, Cease to Energize,
        # and Not Defined (for frequency ride-through)
        # For value initiation, it is assumed to be either in service (continuous operation) or not in service (trip)
        # Ride-through status may be determined after running through the voltage and frequency ride-through criteria.
        if der_obj.der_file.STATUS_INIT:
            self.der_status = 'Continuous Operation'
        else:
            self.der_status = 'Trip'

        self.ridethroughcrit = RideThroughCrit(der_obj)
        self.enterservicecrit = EnterServiceCrit(der_obj)
        self.tripcrit = TripCrit(der_obj)

    def determine_der_status(self):
        """
        Determine DER operating status by considering enter service, trip criteria and ride-though modes

        Variable used in this function:
        :param rt_mode_v:	DER voltage ride-through performance mode.
        :param rt_mode_f:	DER frequency ride-through performance mode.
        :param es_crit:	Enter service criteria met
        :param trip_crit:	Trip criteria met
        :param t_s:	Simulation time step
        :param es_ramp_rate_exec:	Enter service ramp time duration (ES_RAMP_RATE) after execution delay
        :param es_completed:	Enter service ramp completed in the previous time step
        """

        # Enter service criteria (Section 3.5.1.1 in Report #3002025583: IEEE 1547-2018 OpenDER Model)
        es_crit = self.enterservicecrit.es_decision()

        # Trip criteria (Section 3.5.1.2 in Report #3002025583: IEEE 1547-2018 OpenDER Model)
        trip_crit = self.tripcrit.trip_decision()

        # Ride-through criteria (Section 3.5.1.3 in Report #3002025583: IEEE 1547-2018 OpenDER Model)
        self.ridethroughcrit.determine_ride_through_mode()

        # Eq 3.5.1-51,52, If DER is in Trip condition, and enter service criteria is met, depending on whether
        # simulation time step is greater than the ramp time, DER goes to "Entering Service" or "Continuous Operation"
        if self.der_status == 'Trip':
            if es_crit:
                if opender.der.DER.t_s <= self.exec_delay.es_ramp_rate_exec:
                    self.der_status = 'Entering Service'
                else:
                    self.der_status = 'Continuous Operation'

        # Eq 3.5.1-53, If DER was Entering Service, and the enter service process has completed, DER goes to
        # "Continuous Operation"
        if self.der_status == 'Entering Service':
            if self.der_obj.activepowerfunc.es_completed:
                self.der_status = 'Continuous Operation'

        # Eq 3.5.1-54~58, If DER is not Tripped (Entering Service, Continuous Operation, or all other Ride-through
        # modes), DER status depends on ride-through modes, in the priority of: Not Defined (frequency ride-through),
        # Other ride-through modes, and Continuous Operation.
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
                # Eq 3.5.1-57, If DER is in continuous operation, reset the flag that indicates required
                # ride-through time has passed
                self.ridethroughcrit.reset_rt_pass_time_req()

        # Eq. 3.5.1-59, if trip criteria is met, DER goes to Trip mode
        if trip_crit:
            self.der_status = 'Trip'

        return self.der_status

