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


class WattVAR:
    """
    |  Active Power – Reactive Power (Watt-var) Function
    |  EPRI Report Reference: Section 3.9.3 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_obj):
        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay
        self.qp_lpf = LowPassFilter()
        self.qp_delay = TimeDelay()

        self.p_desired_qp_pu = None     # Desired output active power in per unit for BESS considering the different
                                        # nameplate ratings for charging and discharging
        self.q_qp_desired_ref_pu = None     # Watt-var function reactive power reference before response time
        self.q_qp_lpf_pu = None         # Watt-var function reactive power reference after first order lag
        self.q_qp_desired_pu = None     # Output reactive power from watt-var function
        
    def calculate_q_qp_desired_var(self, p_desired_pu):
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
        :param NP_REACT_TIME:   DER grid support function reaction time
        :param p_desired_pu:	Desired output active power considering DER enter service performance
        :param NP_P_MAX:	Active power rating at unity power factor
        :param NP_P_MAX_CHARGE:	DER active power charge rating
        :param NP_VA_MAX:	Apparent power maximum rating

        Output:
        :param q_qp_desired_pu:	Output reactive power from watt-var function

        """

        # Eq. 3.8.1-7, Calculate desired active power in per unit
        self.p_desired_qp_pu = p_desired_pu * (1 if p_desired_pu > 0 else self.der_file.NP_P_MAX/self.der_file.NP_P_MAX_CHARGE)

        # Eq. 3.8.1-8, calculate reactive power reference in per unit according to watt-var curve
        if self.p_desired_qp_pu <= self.exec_delay.qp_curve_p3_load_exec:
            self.q_qp_desired_ref_pu = self.exec_delay.qp_curve_q3_load_exec

        if (self.p_desired_qp_pu <= self.exec_delay.qp_curve_p2_load_exec) and (self.p_desired_qp_pu > self.exec_delay.qp_curve_p3_load_exec):
            self.q_qp_desired_ref_pu = self.exec_delay.qp_curve_q3_load_exec - ((self.p_desired_qp_pu - self.exec_delay.qp_curve_p3_load_exec)
                                  / (self.exec_delay.qp_curve_p2_load_exec - self.exec_delay.qp_curve_p3_load_exec)) \
                                  * (self.exec_delay.qp_curve_q3_load_exec - self.exec_delay.qp_curve_q2_load_exec)

        if (self.p_desired_qp_pu <= self.exec_delay.qp_curve_p1_load_exec) and (self.p_desired_qp_pu > self.exec_delay.qp_curve_p2_load_exec):
            self.q_qp_desired_ref_pu = self.exec_delay.qp_curve_q2_load_exec - ((self.p_desired_qp_pu - self.exec_delay.qp_curve_p2_load_exec)
                                  / (self.exec_delay.qp_curve_p1_load_exec - self.exec_delay.qp_curve_p2_load_exec)) \
                                  * (self.exec_delay.qp_curve_q2_load_exec - self.exec_delay.qp_curve_q1_load_exec)

        if (self.p_desired_qp_pu <= self.exec_delay.qp_curve_p1_gen_exec) and (self.p_desired_qp_pu > self.exec_delay.qp_curve_p1_load_exec):
            self.q_qp_desired_ref_pu = self.exec_delay.qp_curve_q1_load_exec - ((self.p_desired_qp_pu - self.exec_delay.qp_curve_p1_load_exec)
                                  / (self.exec_delay.qp_curve_p1_gen_exec - self.exec_delay.qp_curve_p1_load_exec)) \
                                  * (self.exec_delay.qp_curve_q1_load_exec - self.exec_delay.qp_curve_q1_gen_exec)

        if (self.p_desired_qp_pu <= self.exec_delay.qp_curve_p2_gen_exec) and (self.p_desired_qp_pu > self.exec_delay.qp_curve_p1_gen_exec):
            self.q_qp_desired_ref_pu = self.exec_delay.qp_curve_q1_gen_exec - ((self.p_desired_qp_pu - self.exec_delay.qp_curve_p1_gen_exec)
                                  / (self.exec_delay.qp_curve_p2_gen_exec - self.exec_delay.qp_curve_p1_gen_exec)) \
                                  * (self.exec_delay.qp_curve_q1_gen_exec - self.exec_delay.qp_curve_q2_gen_exec)
            
        if (self.p_desired_qp_pu <= self.exec_delay.qp_curve_p3_gen_exec) and (self.p_desired_qp_pu > self.exec_delay.qp_curve_p2_gen_exec):
            self.q_qp_desired_ref_pu = self.exec_delay.qp_curve_q2_gen_exec - ((self.p_desired_qp_pu - self.exec_delay.qp_curve_p2_gen_exec)
                                  / (self.exec_delay.qp_curve_p3_gen_exec - self.exec_delay.qp_curve_p2_gen_exec)) \
                                  * (self.exec_delay.qp_curve_q2_gen_exec - self.exec_delay.qp_curve_q3_gen_exec)
            
        if self.p_desired_qp_pu > self.exec_delay.qp_curve_p3_gen_exec:
            self.q_qp_desired_ref_pu = self.exec_delay.qp_curve_q3_gen_exec

        # Eq. 3.8.1-9, apply a low pass filter and time delay to represent a possible time response of watt-var
        # function. Note that there can be multiple different ways to implement this behavior in actual DER.
        # The model may be updated in a future version, according to the lab test results.
        self.q_qp_lpf_pu = self.qp_lpf.low_pass_filter(self.q_qp_desired_ref_pu, self.der_file.QP_RT - self.der_file.NP_REACT_TIME)
        self.q_qp_desired_pu = self.qp_delay.tdelay(self.q_qp_lpf_pu, self.der_file.NP_REACT_TIME)

        return self.q_qp_desired_pu
