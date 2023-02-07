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

from .es_perf import EnterServicePerformance



class EnterServicePerformanceBESS(EnterServicePerformance):
    """
    Calculate desired active power output in Enter service ramp condition for BESS DER
    EPRI Report Reference: Section 3.7.3.1 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_obj):
        super(EnterServicePerformanceBESS, self).__init__(der_obj)

    def es_performance(self):
        """
        Determine the ramp reference when entering service

        Variable used in this function:
        
        :param der_status:	Status of DER (Trip, Entering Service, etc)
        :param es_ramp_rate_exec:	Enter service soft-start duration (ES_RAMP_RATE) signal after execution delay
        :param p_act_supp_w:	Desired output active power from active power support functions in kW
        :param NP_P_MAX:	Active power rating at unity power factor

        Internal Variable:
        
        :param es_flag:	Flag to indicate whether DER is in start-up process
        :param p_es_w:	Desired output active power considering DER status
        :param p_es_ramp_w:	Desired output active power during enter service ramp
        :param es_flag_set:	Set value for es_flag flipflop logic
        :param es_flag_reset:	Reset value for es_flag flipflop logic

        Output:
        
        :param p_desired_w:	Desired output active power considering DER enter service performance
        """

        if self.der_obj.der_status == "Entering Service":
            # Eq 3.7.3-1,2, If power demand is positive (discharging), ramp reference is set to a value higher than 1,
            # If power demand is negative (charging), ramp reference is set to a value smaller than -1. Purpose is to
            # identify completion of enter service ramp
            if self.der_obj.der_input.p_dem_pu > 0:
                self.p_es_pu = self.rrl.ramp(1.1, self.exec_delay.es_ramp_rate_exec, 0)
            else:
                self.p_es_pu = self.rrl.ramp(-1.1, 0, self.exec_delay.es_ramp_rate_exec)

        elif self.der_obj.der_status == "Trip":
            # Eq 3.7.3-3, if DER is tripped, the reference should be reset to 0
            self.p_es_pu = self.rrl.ramp(0, 0, 0)
        else:
            # Eq 3.7.3-4, if DER is not tripped and enter service process is completed, the reference is set to a
            # constant value with magnitude greater than 1, and sign depending on the sign of power demand.
            if self.der_obj.der_input.p_dem_pu > 0:
                self.p_es_pu = self.rrl.ramp(1.1, 0, 0)
            else:
                self.p_es_pu = self.rrl.ramp(-1.1, 0, 0)

        return self.p_es_pu
