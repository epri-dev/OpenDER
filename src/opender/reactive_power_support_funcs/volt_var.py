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


from opender.auxiliary_funcs.low_pass_filter import LowPassFilter


class VoltVAR:
    """
    |  Voltage–Reactive Power (Volt-var) Function
    |  EPRI Report Reference: Section 3.9.2 in Report #3002021694: IEEE 1547-2018 DER Model
    """
    def __init__(self, der_file, exec_delay, der_input):

        self.der_file = der_file
        self.exec_delay = exec_delay
        self.der_input = der_input

        self.qv_lpf = LowPassFilter()
        self.qv_curve_v1_exec_prev = None   # Value of variable qv_curve_v1_exec in the previous time step (initialized by the first value of QV_CURVE_V1)
        self.qv_curve_v2_exec_prev = None   # Value of variable qv_curve_v2_exec in the previous time step (initialized by the first value of QV_CURVE_V2)
        self.qv_curve_v3_exec_prev = None   # Value of variable qv_curve_v3_exec in the previous time step (initialized by the first value of QV_CURVE_V3)
        self.qv_curve_v4_exec_prev = None   # Value of variable qv_curve_v4_exec in the previous time step (initialized by the first value of QV_CURVE_V4)
        self.qv_curve_v1_appl_prev = None   # Value of variable qv_curve_v1_appl in the previous time step (if the first value of QV_VREF_AUTO_MODE is TRUE, initialized by  the first value of QV_CURVE_V1, initialized by the first value of v_meas_pu – QV_VREF + QV_CURVE_V1)
        self.qv_curve_v2_appl_prev = None   # Value of variable qv_curve_v2_appl in the previous time step (if the first value of QV_VREF_AUTO_MODE is TRUE, initialized by  the first value of QV_CURVE_V2, initialized by the first value of v_meas_pu – QV_VREF + QV_CURVE_V2)
        self.qv_curve_v3_appl_prev = None   # Value of variable qv_curve_v3_appl in the previous time step (if the first value of QV_VREF_AUTO_MODE is TRUE, initialized by  the first value of QV_CURVE_V3, initialized by the first value of v_meas_pu – QV_VREF + QV_CURVE_V3)
        self.qv_curve_v4_appl_prev = None   # Value of variable qv_curve_v4_appl in the previous time step (if the first value of QV_VREF_AUTO_MODE is TRUE, initialized by  the first value of QV_CURVE_V4, initialized by the first value of v_meas_pu – QV_VREF + QV_CURVE_V4)
        self.qv_vref_appl_prev = None       # Value of variable qv_vref_appl in the previous time step (if the first value of QV_VREF_AUTO_MODE is TRUE, initialized by  the first value of QV_VREF, initialized by the first value of v_meas_pu)

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
        :param NP_VA_MAX: Apparent power maximum rating
        :param qv_olrt_exec: Volt-var open loop response time after execution delay
        
        Internal variables:

        :param q_qv_desired_ref_pu: Volt-var function reactive power reference value in per unit
        :param q_qv_desired_ref_var: Volt-var function reactive power reference before response time
        :param qv_vref_appl: Applied VRefsetting to determine the applied voltage settings
        :param qv_curve_v1_appl: Applied V1 setting with volt-var curve shifting when VRefchanges
        :param qv_curve_v2_appl: Applied V2 setting with volt-var curve shifting when VRefchanges
        :param qv_curve_v3_appl: Applied V3 setting with volt-var curve shifting when VRefchanges
        :param qv_curve_v4_appl: Applied V4 setting with volt-var curve shifting when VRefchanges

        Output variables:

        :param q_qv_desired_var: Output reactive power from volt-var function
        """

        # Eq. 3.9.1-3, The applied VRef is determined by either the VRef control setpoint or low pass filtered
        # applicable voltage, depending on the enable signal
        if(self.exec_delay.qv_vref_auto_mode_exec == 0):
            qv_vref_appl = self.exec_delay.qv_vref_exec
        else:
            qv_vref_appl = self.v_meas_qv_vref_lpf_pu.low_pass_filter(self.der_input.v_meas_pu, self.exec_delay.qv_vref_time_exec)
        
        # Initializing Internal state variables. Executes only the first time the function is called
        if self.qv_curve_v1_appl_prev is None:
            if self.exec_delay.qv_vref_auto_mode_exec == 0:
                self.qv_curve_v1_appl_prev = self.exec_delay.qv_curve_v1_exec
            else:
                self.qv_curve_v1_appl_prev = self.exec_delay.qv_curve_v1_exec - self.exec_delay.qv_vref_exec + self.der_input.v_meas_pu

        if self.qv_curve_v2_appl_prev is None:
            if self.exec_delay.qv_vref_auto_mode_exec == 0:
                self.qv_curve_v2_appl_prev = self.exec_delay.qv_curve_v2_exec
            else:
                self.qv_curve_v2_appl_prev = self.exec_delay.qv_curve_v2_exec - self.exec_delay.qv_vref_exec + self.der_input.v_meas_pu

        if self.qv_curve_v3_appl_prev is None:
            if self.exec_delay.qv_vref_auto_mode_exec == 0:
                self.qv_curve_v3_appl_prev = self.exec_delay.qv_curve_v3_exec
            else:
                self.qv_curve_v3_appl_prev = self.exec_delay.qv_curve_v3_exec - self.exec_delay.qv_vref_exec + self.der_input.v_meas_pu

        if self.qv_curve_v4_appl_prev is None:
            if self.exec_delay.qv_vref_auto_mode_exec == 0:
                self.qv_curve_v4_appl_prev = self.exec_delay.qv_curve_v4_exec
            else:
                self.qv_curve_v4_appl_prev = self.exec_delay.qv_curve_v4_exec - self.exec_delay.qv_vref_exec + self.der_input.v_meas_pu

        if self.qv_vref_appl_prev is None:
            if self.exec_delay.qv_vref_auto_mode_exec == 0:
                self.qv_vref_appl_prev = self.exec_delay.qv_vref_exec
            else:
                self.qv_vref_appl_prev = self.der_input.v_meas_pu
            
        if self.qv_curve_v1_exec_prev is None:
            self.qv_curve_v1_exec_prev = self.exec_delay.qv_curve_v1_exec
            
        if self.qv_curve_v2_exec_prev is None:
            self.qv_curve_v2_exec_prev = self.exec_delay.qv_curve_v2_exec
            
        if self.qv_curve_v3_exec_prev is None:
            self.qv_curve_v3_exec_prev = self.exec_delay.qv_curve_v3_exec
            
        if self.qv_curve_v4_exec_prev is None:
            self.qv_curve_v4_exec_prev = self.exec_delay.qv_curve_v4_exec

        # Eq. 3.9.1-4, The applied volt-var curve voltage settings should shift according to the changes of applied
        # VRef. If applied VRef changes (qv_vref_appl ≠ qv_vref_appl_prev):
        if qv_vref_appl != self.qv_vref_appl_prev:
            qv_curve_v1_appl = self.qv_curve_v1_appl_prev + qv_vref_appl - self.qv_vref_appl_prev
            qv_curve_v2_appl = self.qv_curve_v2_appl_prev + qv_vref_appl - self.qv_vref_appl_prev
            qv_curve_v3_appl = self.qv_curve_v3_appl_prev + qv_vref_appl - self.qv_vref_appl_prev
            qv_curve_v4_appl = self.qv_curve_v4_appl_prev + qv_vref_appl - self.qv_vref_appl_prev
        else:
            qv_curve_v1_appl = self.qv_curve_v1_appl_prev
            qv_curve_v2_appl = self.qv_curve_v2_appl_prev
            qv_curve_v3_appl = self.qv_curve_v3_appl_prev
            qv_curve_v4_appl = self.qv_curve_v4_appl_prev

        # Eq. 3.9.1-5 ~ -8, if voltage settings change, the applied volt-var curve voltage settings should follow the
        # controlled settings change
        if self.exec_delay.qv_curve_v1_exec != self.qv_curve_v1_exec_prev:
            qv_curve_v1_appl = self.exec_delay.qv_curve_v1_exec
        
        if self.exec_delay.qv_curve_v2_exec != self.qv_curve_v2_exec_prev:
            qv_curve_v2_appl = self.exec_delay.qv_curve_v2_exec
            
        if self.exec_delay.qv_curve_v3_exec != self.qv_curve_v3_exec_prev:
            qv_curve_v3_appl = self.exec_delay.qv_curve_v3_exec
            
        if self.exec_delay.qv_curve_v4_exec != self.qv_curve_v4_exec_prev:
            qv_curve_v4_appl = self.exec_delay.qv_curve_v4_exec
        
        # Eq. 3.9.1-9, Volt-VAR Reactive power reference calculation in p.u
        if self.der_input.v_meas_pu < qv_curve_v1_appl:
            q_qv_desired_ref_pu = self.exec_delay.qv_curve_q1_exec
            
        if qv_curve_v2_appl >= self.der_input.v_meas_pu >= qv_curve_v1_appl:
            q_qv_desired_ref_pu = self.exec_delay.qv_curve_q1_exec - ((self.der_input.v_meas_pu - qv_curve_v1_appl)/(qv_curve_v2_appl - qv_curve_v1_appl)) * (self.exec_delay.qv_curve_q1_exec - self.exec_delay.qv_curve_q2_exec)
            
        if qv_curve_v3_appl > self.der_input.v_meas_pu > qv_curve_v2_appl:
            q_qv_desired_ref_pu = self.exec_delay.qv_curve_q2_exec - ((self.der_input.v_meas_pu - qv_curve_v2_appl)/(qv_curve_v3_appl - qv_curve_v2_appl)) * (self.exec_delay.qv_curve_q2_exec - self.exec_delay.qv_curve_q3_exec)
            
        if qv_curve_v4_appl >= self.der_input.v_meas_pu >= qv_curve_v3_appl:
            q_qv_desired_ref_pu = self.exec_delay.qv_curve_q3_exec - ((self.der_input.v_meas_pu - qv_curve_v3_appl)/(qv_curve_v4_appl - qv_curve_v3_appl)) * (self.exec_delay.qv_curve_q3_exec - self.exec_delay.qv_curve_q4_exec)
        
        if self.der_input.v_meas_pu > qv_curve_v4_appl:
            q_qv_desired_ref_pu = self.exec_delay.qv_curve_q4_exec
        
        # Eq. 3.9.1-10, Volt-VAR Reactive power reference calculation in kvar
        q_qv_desired_ref_var = q_qv_desired_ref_pu * self.der_file.NP_VA_MAX

        # Eq. 3.9.1-11, OLRT using LPF
        q_qv_desired_var = self.qv_lpf.low_pass_filter(q_qv_desired_ref_var, self.exec_delay.qv_olrt_exec)
        
        # Resetting internal state variables
        self.qv_curve_v1_exec_prev = self.exec_delay.qv_curve_v1_exec
        self.qv_curve_v2_exec_prev = self.exec_delay.qv_curve_v2_exec
        self.qv_curve_v3_exec_prev = self.exec_delay.qv_curve_v3_exec
        self.qv_curve_v4_exec_prev = self.exec_delay.qv_curve_v4_exec
        
        self.qv_curve_v1_appl_prev = qv_curve_v1_appl
        self.qv_curve_v2_appl_prev = qv_curve_v2_appl
        self.qv_curve_v3_appl_prev = qv_curve_v3_appl
        self.qv_curve_v4_appl_prev = qv_curve_v4_appl
        
        self.qv_vref_appl_prev = qv_vref_appl
            
        return q_qv_desired_var
            