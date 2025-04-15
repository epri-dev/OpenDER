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

from opender.auxiliary_funcs.time_delay import TimeDelay
from opender.auxiliary_funcs.cond_delay import ConditionalDelay
import numpy as np


# %%
class EnterServiceCrit:
    """
    Enter Service criteria
    EPRI Report Reference: Section 3.5.1.1 in Report #3002030962: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_obj):

        self.der_obj = der_obj
        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay
        self.der_input = der_obj.der_input

        self.es_vf_crit = None      # Enter service voltage and frequency criteria met
        self.es_vft_crit = None     # Enter service voltage and frequency criteria met for the enter service delay
        self.es_vfto_crit = None    # Enter service voltage and frequency and other enter service criteria met
        self.es_crit = None         # Enter service criteria met

        self.es_randomized_delay_time = 0  # Enter service randomized delay time (initialized by 0)

        self.rand_delay = TimeDelay()
        self.vft_delay = ConditionalDelay()

    def es_decision(self):
        """
        Deciding Enter Service Criteria, if met, DER goes to "Entering Service" status.

        Variable used in this function:
        
        :param es_permit_service_exec: Permit service activated by request from the area EPS operator (ES_PERMIT_SERVICE) after execution delay
        :param v_low_pu: Minimum applicable voltage as enter service, over voltage trip criterion in per unit
        :param v_high_pu: Maximum applicable voltage as enter service, over voltage trip criterion in per unit
        :param freq_hz: Frequency at RPA
        :param es_v_low_exec: Minimum applicable voltage for enter service criteria (ES_V_LOW) signal after execution delay
        :param es_v_high_exec: Maximum applicable voltage for enter service criteria (ES_V_HIGH) signal after execution delay
        :param es_f_low_exec: Minimum frequency for enter service criteria (ES_F_LOW) signal after execution delay
        :param es_f_high_exec: Maximum frequency for enter service criteria (ES_F_HIGH) signal after execution delay
        :param es_delay_exec: Minimum intentional delay before initiating softstart (ES_DELAY) signal after execution delay
        :param es_randomized_delay_exec: Maximum time for enter service randomized delay (ES_RANDOMIZED_DELAY) signal after execution delay
        :param es_ramp_rate_exec: Enter service soft-start duration (ES_RAMP_RATE) signal after execution delay
        :param ES_RANDOMIZED_DELAY_ACTUAL: Specified value for enter service randomized delay for simulation purpose
        :param NP_VA_MAX: Apparent power maximum rating

        Output:
        :param es_crit:	Enter service criteria met
        """

        # Eq 3.5.1-1, enter service logic of voltage and frequency checks
        self.es_vf_crit = (self.der_input.v_low_pu >= self.exec_delay.es_v_low_exec) \
                      and (self.der_input.v_high_pu <= self.exec_delay.es_v_high_exec) \
                      and (self.der_input.freq_hz >= self.exec_delay.es_f_low_exec) \
                      and (self.der_input.freq_hz <= self.exec_delay.es_f_high_exec) \
                      and self.exec_delay.es_permit_service_exec

        # Eq 3.5.1-2, conditional delayed enable that voltage and frequency checks must be satisfied for a time delay
        # period
        self.es_vft_crit = self.vft_delay.con_del_enable(self.es_vf_crit, self.exec_delay.es_delay_exec)

        # Eq 3.5.1-3, allow including other enter service criteria
        self.es_vfto_crit = self.es_vft_crit and self.es_other_crit()

        # Eq 3.5.1-4, generate the enter service randomized delay. The value is 0 if enter service ramp is used.
        if self.der_obj.der_status != "Trip":
            # if DER is on, reset randomized delay to 0 for next time use.
            self.es_randomized_delay_time = 0
        else:
            if self.der_file.ES_RANDOMIZED_DELAY_ACTUAL > 0 and self.es_vfto_crit:
                # if ES_RANDOMIZED_DELAY_ACTUAL is provided by user, use this value
                self.es_randomized_delay_time = self.der_file.ES_RANDOMIZED_DELAY_ACTUAL
            elif (self.exec_delay.es_ramp_rate_exec == 0) and (self.exec_delay.es_randomized_delay_exec > 0) and (
                    self.der_file.NP_VA_MAX < 500e3):
                if self.es_randomized_delay_time == 0:
                    # If no value, create a new randomized delay when enter service criterion made
                    self.es_randomized_delay_time = np.random.random() * self.exec_delay.es_randomized_delay_exec
                # If delay time is not 0, keep the value in the previous time step
            else:
                # If not enabled or DER size is greater than 500kVA, no randomized delay
                self.es_randomized_delay_time = 0

        # Eq 3.5.1-5, apply the randomized delay
        self.es_crit = self.rand_delay.tdelay(self.es_vfto_crit, self.es_randomized_delay_time)

        return self.es_crit

    def es_other_crit(self):
        """
        Other criteria for enter service, used by Eq 3.5.1-3. Default is True.
        Overridden by es_crit_pv.py for PV DERs, where enter service criteria also considers available power.
        """
        return True
