"""
Copyright © 2022 Electric Power Research Institute, Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
· Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
· Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
· Neither the name of the EPRI nor the names of its contributors may be used
  to endorse or promote products derived from this software without specific
  prior written permission.
"""
from .time_delay import TimeDelay
from .ramping import Ramping
from . import der
from .flipflop import FlipFlop
from .cond_delay import ConditionalDelay
from . import operating_condition_input_processing
import numpy as np


# %%
class EdgeDetector:
    """
    Edge Detector
    """

    def __init__(self, up_edge=False, dn_edge=False):
        # x0: initial output value
        # up_edge: detect up edge
        # dn_edge: detect down edge
        self.x = None
        self.up_edge = up_edge
        self.dn_edge = dn_edge

    def run(self, x):
        """
        Return 1 if an up edge or down edge is detected.

        Input Argument:
        :x: Input signal for edge detection
        Output:
        :y: If up edge or down edge detected, return 1
        """
        if self.x is None:
            self.x = x
        if self.up_edge and (x - self.x > 0.1):
            y = 1
        elif self.dn_edge and (self.x - x > 0.1):
            y = 1
        else:
            y = 0
        self.x = x
        return y

class EnterServicePerformance:
    """
    Calculate desired active power output in Enter service ramp condition
    EPRI Report Reference: Section 3.7 in Report #3002021694: IEEE 1547-2018 DER Model
    """

    def __init__(self):
        self.rrl = Ramping()
        self.edge = EdgeDetector(
            up_edge = True,
            )

    def es_performance(self, der_file, exec_delay, p_act_supp_kw, der_status):
        """
        Variable used in this function:
        :der_status:	Status of DER (on or off)
        :es_ramp_rate_exec:	Enter service soft-start duration (ES_RAMP_RATE) signal after execution delay
        :p_act_supp_kw:	Desired output active power from active power support functions in kW
        :NP_P_MAX:	Active power rating at unity power factor

        Internal Variable:
        :es_flag:	Flag to indicate whether DER is in start-up process
        :p_es_kw:	Desired output active power considering DER status
        :p_es_ramp_kw:	Desired output active power during enter service ramp
        :es_flag_set:	Set value for es_flag flipflop logic
        :es_flag_reset:	Reset value for es_flag flipflop logic

        Output:
        :p_desired_kw:	Desired output active power considering DER enter service performance
        """
        # Eq 29, input available power
        if der_status:
            p_es_kw = p_act_supp_kw
        else:
            p_es_kw = 0
        # Eq. 30, ramp rate limiter
        if exec_delay.es_ramp_rate_exec>0:
            p_es_ramp_kw = der_file.NP_P_MAX * self.rrl.ramp(p_es_kw/der_file.NP_P_MAX, exec_delay.es_ramp_rate_exec, exec_delay.es_ramp_rate_exec)
        else:
            p_es_ramp_kw = p_es_kw
        # Eq. 31 Edge detector to identify Enter Service decision
        es_flag_set = self.edge.run(der_status)
        # Eq. 32 Enter service ramp complete
        es_flag_reset = (p_es_ramp_kw == p_es_kw) or not der_status
        # Eq. 33, flipflop logic to detemine if in enter service ramp
        if es_flag_reset:
            self.es_flag = 0
        elif es_flag_set:
            self.es_flag = 1
        # Eq. 34, output selector
        if self.es_flag:
            self.p_desired_kw = p_es_ramp_kw
        else:
            self.p_desired_kw = p_es_kw
        return self.p_desired_kw