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


class WattVAR:
    """
    |  Active Power – Reactive Power (Watt-var) Function
    |  EPRI Report Reference: Section 3.9.3 in Report #3002021694: IEEE 1547-2018 DER Model
    """

    def __init__(self,der_file, exec_delay):
        self.der_file = der_file
        self.exec_delay = exec_delay
        self.qp_lpf = LowPassFilter()
        
    def calculate_q_qp_desired_kvar(self, p_desired_kw):
        """
        Calculates and returns output reactive power from Watt-VAR function

        Variable used in this function:
        
        :param qp_curve_p1_gen_exec:	P-Q Curve Point P1 Setting (QP_CURVE_P1_GEN) after execution delay
        :param qp_curve_q1_gen_exec:	P-Q Curve Point Q1 Setting (QP_CURVE_Q1_GEN) after execution delay
        :param qp_curve_p2_gen_exec:	P-Q Curve Point P2 Setting (QP_CURVE_P2_GEN) after execution delay
        :param qp_curve_q2_gen_exec:	P-Q Curve Point Q2 Setting (QP_CURVE_Q2_GEN) after execution delay
        :param qp_curve_p3_gen_exec:	P-Q Curve Point P3 Setting (QP_CURVE_P3_GEN) after execution delay
        :param qp_curve_q3_gen_exec:	P-Q Curve Point Q3 Setting (QP_CURVE_Q3_GEN) after execution delay
        :param qp_curve_p1_load_exec:	P-Q Curve Point P'1 Setting (QP_CURVE_P1_LOAD) after execution delay
        :param qp_curve_q1_load_exec:	P-Q Curve Point Q'1 Setting (QP_CURVE_Q1_LOAD) after execution delay
        :param qp_curve_p2_load_exec:	P-Q Curve Point P'2 Setting (QP_CURVE_P2_LOAD) after execution delay
        :param qp_curve_q2_load_exec:	P-Q Curve Point Q'2 Setting (QP_CURVE_Q2_LOAD) after execution delay
        :param qp_curve_p3_load_exec:	P-Q Curve Point P'3 Setting (QP_CURVE_P3_LOAD) after execution delay
        :param qp_curve_q3_gen_exec:	P-Q Curve Point Q'3 Setting (QP_CURVE_Q3_LOAD) after execution delay
        :param QP_RT:	Active Power Reactive Power Mode Response Time
        :param p_desired_kw:	Desired output active power considering DER enter service performance
        :param NP_P_MAX:	Active power rating at unity power factor

        Internal variables:
        
        :param q_qp_desired_ref_pu:	Watt-var function reactive power reference value in per unit.
        :param q_qp_desired_ref_kvar:	Watt-var function reactive power reference before response time
        :param p_desired_pu:	Desired output active power in per unit considering DER enter service performance

        Output:
        
        :param q_qp_desired_kvar:	Output reactive power from watt-var function

        """

        # Eq. 3.9.1-12, Calculate desired active power in per unit
        p_desired_pu = p_desired_kw / (self.der_file.NP_P_MAX if p_desired_kw > 0 else self.der_file.NP_P_MAX_CHARGE)

        # Eq. 3.9.1-13, calculate reactive power reference in per unit according to watt-var curve
        if p_desired_pu <= self.exec_delay.qp_curve_p3_load_exec:
            q_qp_desired_ref_pu = self.exec_delay.qp_curve_q3_load_exec

        if (p_desired_pu <= self.exec_delay.qp_curve_p2_load_exec) and (p_desired_pu > self.exec_delay.qp_curve_p3_load_exec):
            q_qp_desired_ref_pu = self.exec_delay.qp_curve_q3_load_exec - ((p_desired_pu - self.exec_delay.qp_curve_p3_load_exec)
                                  / (self.exec_delay.qp_curve_p2_load_exec - self.exec_delay.qp_curve_p3_load_exec)) \
                                  * (self.exec_delay.qp_curve_q3_load_exec - self.exec_delay.qp_curve_q2_load_exec)

        if (p_desired_pu <= self.exec_delay.qp_curve_p1_load_exec) and (p_desired_pu > self.exec_delay.qp_curve_p2_load_exec):
            q_qp_desired_ref_pu = self.exec_delay.qp_curve_q2_load_exec - ((p_desired_pu - self.exec_delay.qp_curve_p2_load_exec)
                                  / (self.exec_delay.qp_curve_p1_load_exec - self.exec_delay.qp_curve_p2_load_exec)) \
                                  * (self.exec_delay.qp_curve_q2_load_exec - self.exec_delay.qp_curve_q1_load_exec)

        if (p_desired_pu <= self.exec_delay.qp_curve_p1_gen_exec) and (p_desired_pu > self.exec_delay.qp_curve_p1_load_exec):
            q_qp_desired_ref_pu = self.exec_delay.qp_curve_q1_load_exec - ((p_desired_pu - self.exec_delay.qp_curve_p1_load_exec)
                                  / (self.exec_delay.qp_curve_p1_gen_exec - self.exec_delay.qp_curve_p1_load_exec)) \
                                  * (self.exec_delay.qp_curve_q1_load_exec - self.exec_delay.qp_curve_q1_gen_exec)

        if (p_desired_pu <= self.exec_delay.qp_curve_p2_gen_exec) and (p_desired_pu > self.exec_delay.qp_curve_p1_gen_exec):
            q_qp_desired_ref_pu = self.exec_delay.qp_curve_q1_gen_exec - ((p_desired_pu - self.exec_delay.qp_curve_p1_gen_exec)
                                  / (self.exec_delay.qp_curve_p2_gen_exec - self.exec_delay.qp_curve_p1_gen_exec)) \
                                  * (self.exec_delay.qp_curve_q1_gen_exec - self.exec_delay.qp_curve_q2_gen_exec)
            
        if (p_desired_pu <= self.exec_delay.qp_curve_p3_gen_exec) and (p_desired_pu > self.exec_delay.qp_curve_p2_gen_exec):
            q_qp_desired_ref_pu = self.exec_delay.qp_curve_q2_gen_exec - ((p_desired_pu - self.exec_delay.qp_curve_p2_gen_exec)
                                  / (self.exec_delay.qp_curve_p3_gen_exec - self.exec_delay.qp_curve_p2_gen_exec)) \
                                  * (self.exec_delay.qp_curve_q2_gen_exec - self.exec_delay.qp_curve_q3_gen_exec)
            
        if p_desired_pu > self.exec_delay.qp_curve_p3_gen_exec:
            q_qp_desired_ref_pu = self.exec_delay.qp_curve_q3_gen_exec

        # Eq. 3.9.1-14, calculate actual value of reactive power reference
        q_qp_desired_ref_kvar = q_qp_desired_ref_pu * self.der_file.NP_VA_MAX

        # Eq. 3.9.1-15, apply the low pass filter. Note that there can be multiple different ways to implement this
        # behavior in actual DER. The model may be updated in a future version, according to the lab test results.
        q_qp_desired_kvar = self.qp_lpf.low_pass_filter(q_qp_desired_ref_kvar, self.der_file.QP_RT)
        
        return q_qp_desired_kvar
