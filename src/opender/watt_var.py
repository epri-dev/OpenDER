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


# -*- coding: utf-8 -*-

from .low_pass_filter import LowPassFilter


class WattVAR:
    """
    Active Power – Reactive Power (Watt-var) Function
    EPRI Report Reference: Section 3.8.3 in Report #3002021694: IEEE 1547-2018 DER Model
    """

    def __init__(self):
        self.qp_olrt = LowPassFilter()
        
    def calculate_q_qp_desired_kvar(self, der_file, exec_delay, p_desired_kw):
        """
        Calculates and returns output reactive power from Watt-VAR function

        Variable used in this function:
        :qp_curve_p1_gen_exec:	P-Q Curve Point P1 Setting (QP_CURVE_P1_GEN) after execution delay
        :qp_curve_q1_gen_exec:	P-Q Curve Point Q1 Setting (QP_CURVE_Q1_GEN) after execution delay
        :qp_curve_p2_gen_exec:	P-Q Curve Point P2 Setting (QP_CURVE_P2_GEN) after execution delay
        :qp_curve_q2_gen_exec:	P-Q Curve Point Q2 Setting (QP_CURVE_Q2_GEN) after execution delay
        :qp_curve_p3_gen_exec:	P-Q Curve Point P3 Setting (QP_CURVE_P3_GEN) after execution delay
        :qp_curve_q3_gen_exec:	P-Q Curve Point Q3 Setting (QP_CURVE_Q3_GEN) after execution delay
        :QP_RT:	Active Power Reactive Power Mode Response Time
        :p_desired_kw:	Desired output active power considering DER enter service performance
        :NP_P_MAX:	Active power rating at unity power factor

        Internal variables:
        :q_qp_desired_ref_pu:	Watt-var function reactive power reference value in per unit.
        :q_qp_desired_ref_kvar:	Watt-var function reactive power reference before response time

        Output:
        :q_qp_desired_kvar:	Output reactive power from watt-var function

        """

        #calculate desired actve power in per unit
        p_desired_pu = p_desired_kw/der_file.NP_P_MAX
        #Eq. 46, calculate reactive power reference in per unit according to watt-var curve
        if( p_desired_pu <= exec_delay.qp_curve_p1_gen_exec):
            q_qp_desired_ref_pu = exec_delay.qp_curve_q1_gen_exec
            
        if((p_desired_pu <= exec_delay.qp_curve_p2_gen_exec) and (p_desired_pu > exec_delay.qp_curve_p1_gen_exec)):
            q_qp_desired_ref_pu = exec_delay.qp_curve_q1_gen_exec - ((p_desired_pu - exec_delay.qp_curve_p1_gen_exec) / (exec_delay.qp_curve_p2_gen_exec - exec_delay.qp_curve_p1_gen_exec)) * (exec_delay.qp_curve_q1_gen_exec - exec_delay.qp_curve_q2_gen_exec)
            
        if((p_desired_pu <= exec_delay.qp_curve_p3_gen_exec) and (p_desired_pu > exec_delay.qp_curve_p2_gen_exec)):
            q_qp_desired_ref_pu = exec_delay.qp_curve_q2_gen_exec - ((p_desired_pu - exec_delay.qp_curve_p2_gen_exec) / (exec_delay.qp_curve_p3_gen_exec - exec_delay.qp_curve_p2_gen_exec)) * (exec_delay.qp_curve_q2_gen_exec - exec_delay.qp_curve_q3_gen_exec)
            
        if( p_desired_pu > exec_delay.qp_curve_p3_gen_exec):
            q_qp_desired_ref_pu = exec_delay.qp_curve_q3_gen_exec

        #Eq. 47, calculate actual value of reactive power reference
        q_qp_desired_ref_kvar = q_qp_desired_ref_pu * der_file.NP_VA_MAX


        '''
        Eq. 48, apply the low pass filter. Note that there can be multiple different ways to implement this behavior 
        in actual DER. The model may be updated in a future version, according to the lab test results.
        '''
        q_qp_desired_kvar = self.qp_olrt.low_pass_filter(q_qp_desired_ref_kvar, der_file.QP_RT)
        
        return q_qp_desired_kvar