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

from opender.auxiliary_funcs.ramping import Ramping


class EnterServicePerformance:
    """
    Calculate desired active power output in Enter service ramp condition
    EPRI Report Reference: Section 3.7.1.3 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_obj):

        self.der_obj = der_obj
        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay

        self.rrl = Ramping()
        self.p_es_pu = None         # DER enter service ramp reference

    def es_performance(self):
        """
        Determine the ramp reference when entering service

        Variable used in this function:
        :param der_status:	Status of DER (Trip, Entering Service, etc)
        :param es_ramp_rate_exec:	Enter service soft-start duration (ES_RAMP_RATE) signal after execution delay

        Output:
        :param p_es_pu:	DER enter service ramp reference
        """

        if self.der_obj.der_status == "Entering Service":
            # Eq 3.7.1-7, if DER is entering service, enter service ramp reference linearly ramp to a value slightly
            # greater than 1. The purpose is to identify if enter service process is completed
            self.p_es_pu = self.rrl.ramp(1.1, self.exec_delay.es_ramp_rate_exec, 0)
        elif self.der_obj.der_status == "Trip":
            # Eq 3.7.1-8, if DER is tripped, the reference should be reset to 0
            self.p_es_pu = self.rrl.ramp(0, 0, 0)
        else:
            # Eq 3.7.1-9, if DER is not tripped and enter service process is completed, the reference is set to high,
            # so that it will not impact output active power
            self.p_es_pu = self.rrl.ramp(1.1, 0, 0)

        return self.p_es_pu
