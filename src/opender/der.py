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

# -*- coding: utf-8 -*-

# Created on Mon Sep 20 15:22:44 2021

# @author: Jithendar Anandan
# @email: janandan@epri.com

from . import common_file_format
from . import active_power_support_functions
from . import reactive_power_support_functions
from . import rem_ctrl
from . import enter_service_and_trip
from . import enter_service_perf
from . import capability_and_priority
from . import operating_condition_input_processing as ocip
from . import setting_execution_delay
from typing import Union, List, Tuple
import numpy as np



class DER:
    # Global Variables
    t_s = 100000        # Simulation time step, default for snapshot analysis

    def __init__(self, der_file_obj=None):
        """
        Creating a DER Object
        :param der_file_obj: DER common file format object created from common_file_format.py
        """

        if der_file_obj is None:
            der_file_obj = common_file_format.DERCommonFileFormat()

        self.der_file = der_file_obj

        self.time = 0       # Elapsed time from start of simulation
        self.name = 'DER1'  # Identification if multiple DERs are defined
        self.bus = None     # Bus which DER is connected to

        # Intermediate variables
        self.p_act_supp_kw = None
        self.p_desired_kw = None
        self.q_desired_kvar = None
        self.p_limited_kw = None
        self.q_limited_kvar = None

        self.der_status = self.der_file.STATUS_INIT

        self.p_out_kw = None
        self.q_out_kvar = None

        # DER model modules
        self.enterservicetrip = enter_service_and_trip.EnterServiceTrip(self.der_file.STATUS_INIT)
        self.enterserviceperf = enter_service_perf.EnterServicePerformance()
        self.reactivepowerfunc = reactive_power_support_functions.DesiredReactivePower()
        self.limited_p_q = capability_and_priority.CapabilityPriority()
        self.executiondelay = setting_execution_delay.SettingExecutionDelay()
        self.activepowerfunc = active_power_support_functions.DesiredActivePower()
        self.der_input = ocip.DERInputs()

    def update_der_input(self, p_dc_kw: float = None, v: Union[List[float], float] = None, theta: List[float] = None,
                         f: float = None, v_pu: Union[List[float], float] = None, p_dc_pu: float = None) -> None:
        """
        Update DER inputs
        :param p_dc_kw:	Available DC power in kW
        :param p_dc_pu:	Available DC power in per unit
        :param v: DER RPA voltage in Volt: if receive a float for three phase DER, all three phases are updated
        :param v_pu: DER RPA voltage in per unit: if receive a float for three phase DER, all three phases are updated
        :param theta: DER RPA voltage angles
        :param f: DER RPA frequency in Hertz
        """

        if p_dc_kw is not None:
            self.der_input.p_dc_kw = p_dc_kw

        if p_dc_pu is not None:
            self.der_input.p_dc_kw = p_dc_pu * self.der_file.NP_P_MAX

        if f is not None:
            self.der_input.freq_hz = f

        if v is not None:
            if self.der_file.NP_PHASE == "THREE":
                if type(v) is float or type(v) is int:
                    v = [v, v, v]
                self.der_input.v_a = v[0]
                self.der_input.v_b = v[1]
                self.der_input.v_c = v[2]

            if self.der_file.NP_PHASE == "SINGLE":
                self.der_input.v = v

        if v_pu is not None:
            if self.der_file.NP_PHASE == "THREE":
                v_base = self.der_file.NP_AC_V_NOM / np.sqrt(3)
                if type(v_pu) is float or type(v_pu) is int:
                    v_pu = [v_pu * v_base, v_pu * v_base, v_pu * v_base]
                else:
                    v_pu = [v_pu[0] * v_base, v_pu[1] * v_base, v_pu[2] * v_base]

                self.der_input.v_a = v_pu[0]
                self.der_input.v_b = v_pu[1]
                self.der_input.v_c = v_pu[2]

            if self.der_file.NP_PHASE == "SINGLE":
                self.der_input.v = v_pu * self.der_file.NP_AC_V_NOM

        if theta is not None:
            self.der_input.theta_a = theta[0]
            self.der_input.theta_b = theta[1]
            self.der_input.theta_c = theta[2]

    def run(self) -> Tuple[float, float]:
        """
        Main calculation loop.
        Call this function once for power flow analysis, or call this function in each simulation time step in dynamic
        simulation.
        """

        # Elapsed time calculation
        self.time = self.time + self.__class__.t_s

        # Input processing
        self.der_input.operating_condition_input_processing(self.der_file)

        # Execution delay
        self.executiondelay.mode_and_execution_delay(self.der_file)

        # Enter service and trip decision making
        self.der_status = self.enterservicetrip.es_decision(self.der_file, self.executiondelay, self.der_input)

        # Calculate desired active power
        self.p_act_supp_kw = self.activepowerfunc.calculate_p_act_supp_kw(self.der_file, self.executiondelay, self.der_input, self.p_out_kw)

        # Enter service ramp
        self.p_desired_kw = self.enterserviceperf.es_performance(self.der_file, self.executiondelay, self.p_act_supp_kw, self.der_status)

        # Calculate desired reactive power
        self.q_desired_kvar = self.reactivepowerfunc.calculate_reactive_funcs(self.der_file, self.executiondelay, self.der_input, self.p_desired_kw, self.der_status)

        # Limit DER output based on kVA rating and DER capability curve
        self.p_limited_kw, self.q_limited_kvar = self.limited_p_q.calculate_limited_pq(self.der_file, self.executiondelay, p_desired_kw=self.p_desired_kw,q_desired_kvar=self.q_desired_kvar)

        # Determine DER model output value
        self.p_out_kw, self.q_out_kvar = rem_ctrl.RemainingControl(self.p_limited_kw, self.q_limited_kvar)

        return self.p_out_kw,self.q_out_kvar

    def reinitialize(self):
        # only used when need to reset DER model
        self.der_status=self.der_file.STATUS_INIT
        self.time = 0
        self.enterservicetrip = enter_service_and_trip.EnterServiceTrip(self.der_file.STATUS_INIT)
        self.enterserviceperf = enter_service_perf.EnterServicePerformance()
        self.reactivepowerfunc = reactive_power_support_functions.DesiredReactivePower()
        self.limited_p_q = capability_and_priority.CapabilityPriority()
        self.executiondelay = setting_execution_delay.SettingExecutionDelay()
        self.activepowerfunc = active_power_support_functions.DesiredActivePower()

        self.p_out_kw = None
        self.q_out_kvar = None

    def __str__(self):
        # for debug, generate a string
        # E.g. can be used when print(DER_obj)
        return f"{self.time:.1f}: {self.name} - v_meas_pu={self.der_input.v_meas_pu:.5f}, " \
               f"p_act_supp_kw={self.p_act_supp_kw:.2f}, q_desired_kvar={self.q_desired_kvar:.2f}, " \
               f"p_out_kw={self.p_out_kw:.2f}, q_out_kvar={self.q_out_kvar:.2f}"


