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


from opender.auxiliary_funcs.low_pass_filter import LowPassFilter
from opender.auxiliary_funcs.time_delay import TimeDelay


class VoltVAR:
    """
    |  Voltage–Reactive Power (Volt-var) Function
    |  EPRI Report Reference: Section 3.9.2 in Report #3002026631: IEEE 1547-2018 OpenDER Model
    """
    def __init__(self, der_obj):

        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay
        self.der_input = der_obj.der_input

        self.qv_lpf = LowPassFilter()
        self.qv_delay = TimeDelay()
        self.qv_curve_v1_appl = None        # Applied V1 setting with volt-var curve shifting when VRef changes
        self.qv_curve_v2_appl = None        # Applied V2 setting with volt-var curve shifting when VRef changes
        self.qv_curve_v3_appl = None        # Applied V3 setting with volt-var curve shifting when VRef changes
        self.qv_curve_v4_appl = None        # Applied V4 setting with volt-var curve shifting when VRef changes
        self.q_qv_desired_ref_pu = None     # Volt-var function reactive power reference value in per unit

        self.qv_vref_appl = None            # Applied VRef setting to determine the applied voltage settings
        self.qv_vref_lpf = None             # Low pass filtered measurement voltage for volt-var VRef tracking mode

        self.q_qv_lpf_pu = None             # Volt-var function reactive power reference after first order lag
        self.q_qv_desired_pu = None         # Output reactive power from volt-var function

        self.v_meas_qv_vref_lpf_pu = LowPassFilter()
        
    def calculate_q_qv_desired_var(self):
        
        """
        Calculates and returns output reactive power from Volt-VAR function

        Variable used in this function:
        :param qv_vref_auto_mode_exec: Autonomous Vref Adjustment Enable(QV_VREF_AUTO_MODE_ENABLE) after execution delay
        :param qv_vref_exec: V/Q Curve VRefSetting(QV_VREF) after execution delay
        :param v_meas_pu: Applicable voltage for volt-var and volt-watt calculation
        :param qv_vref_time_exec: Vref adjustment time Constant (QV_VREF_TIME) after execution delay
        :param qv_curve_v1_exec: V/Q Curve Point V1 Setting (QV_CURVE_V1)after execution delay
        :param qv_curve_v2_exec: V/Q Curve Point V1 Setting (QV_CURVE_V1)after execution delay
        :param qv_curve_v3_exec: V/Q Curve Point V1 Setting (QV_CURVE_V1)after execution delay
        :param qv_curve_v4_exec: V/Q Curve Point V1 Setting (QV_CURVE_V1)after execution delay
        :param qv_curve_q1_exec: V/Q Curve Point Q1 Setting (QV_CURVE_Q1) after execution delay
        :param qv_curve_q2_exec: V/Q Curve Point Q1 Setting (QV_CURVE_Q1) after execution delay
        :param qv_curve_q3_exec: V/Q Curve Point Q1 Setting (QV_CURVE_Q1) after execution delay
        :param qv_curve_q4_exec: V/Q Curve Point Q1 Setting (QV_CURVE_Q1) after execution delay
        :param NP_REACT_TIME:   DER grid support function reaction time
        :param qv_olrt_exec: Volt-var open loop response time after execution delay


        Output variables:
        :param q_qv_desired_pu: Output reactive power from volt-var function
        """

        # Eq 3.8.1-3, The applied VRef is determined by either the VRef control setpoint or low pass filtered
        # applicable voltage, depending on the enable signal
        self.qv_vref_lpf = max(0.95, min(self.v_meas_qv_vref_lpf_pu.low_pass_filter(self.der_input.v_meas_pu, self.exec_delay.qv_vref_time_exec),1.05))
        if self.exec_delay.qv_vref_auto_mode_exec == 0:
            self.qv_vref_appl = self.exec_delay.qv_vref_exec
        else:
            self.qv_vref_appl = self.qv_vref_lpf

        # Eq 3.8.1-4, The applied volt-var curve voltage settings should shift according to the changes of the applied
        # VRef.
        self.qv_curve_v1_appl = self.exec_delay.qv_curve_v1_exec + self.qv_vref_appl - 1
        self.qv_curve_v2_appl = self.exec_delay.qv_curve_v2_exec + self.qv_vref_appl - 1
        self.qv_curve_v3_appl = self.exec_delay.qv_curve_v3_exec + self.qv_vref_appl - 1
        self.qv_curve_v4_appl = self.exec_delay.qv_curve_v4_exec + self.qv_vref_appl - 1

        # Eq. 3.8.1-5, Volt-VAR Reactive power reference calculation in p.u
        if self.der_input.v_meas_pu < self.qv_curve_v1_appl:
            self.q_qv_desired_ref_pu = self.exec_delay.qv_curve_q1_exec
            
        if self.qv_curve_v2_appl >= self.der_input.v_meas_pu >= self.qv_curve_v1_appl:
            self.q_qv_desired_ref_pu = self.exec_delay.qv_curve_q1_exec - ((self.der_input.v_meas_pu - self.qv_curve_v1_appl)/(self.qv_curve_v2_appl - self.qv_curve_v1_appl)) * (self.exec_delay.qv_curve_q1_exec - self.exec_delay.qv_curve_q2_exec)
            
        if self.qv_curve_v3_appl > self.der_input.v_meas_pu > self.qv_curve_v2_appl:
            self.q_qv_desired_ref_pu = self.exec_delay.qv_curve_q2_exec - ((self.der_input.v_meas_pu - self.qv_curve_v2_appl)/(self.qv_curve_v3_appl - self.qv_curve_v2_appl)) * (self.exec_delay.qv_curve_q2_exec - self.exec_delay.qv_curve_q3_exec)
            
        if self.qv_curve_v4_appl >= self.der_input.v_meas_pu >= self.qv_curve_v3_appl:
            self.q_qv_desired_ref_pu = self.exec_delay.qv_curve_q3_exec - ((self.der_input.v_meas_pu - self.qv_curve_v3_appl)/(self.qv_curve_v4_appl - self.qv_curve_v3_appl)) * (self.exec_delay.qv_curve_q3_exec - self.exec_delay.qv_curve_q4_exec)
        
        if self.der_input.v_meas_pu > self.qv_curve_v4_appl:
            self.q_qv_desired_ref_pu = self.exec_delay.qv_curve_q4_exec

        # Eq. 3.9.1-6, OLRT using LPF followed by a time delay to represent a reaction delay
        self.q_qv_lpf_pu = self.qv_lpf.low_pass_filter(self.q_qv_desired_ref_pu, self.exec_delay.qv_olrt_exec - self.der_file.NP_REACT_TIME)
        self.q_qv_desired_pu = self.qv_delay.tdelay(self.q_qv_lpf_pu, self.der_file.NP_REACT_TIME)

            
        return self.q_qv_desired_pu
            