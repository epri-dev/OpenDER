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

import numpy as np


#%%
def intercep_piecewise_circle(mag, xp, yp, k = 0.9, err = 1.e-3, ):
    """
    Find out the interception point of piece-wise function defined by xp and yp at given magnitude

    Input argument:
    
    :param xp: list or array on x axis (increasing from left to right)
    :param yp: list or array on y axis
    :param mag: magnitude of (x, y) that will intercept on the right side of xp and yp
    :param k: convergence factor (<1 slows convergence with increased robustness)
    :param err: error threshold

    Output:
    
    :param x: interception point on x axis
    :param y: interception point on y axis
    """
    # # step 1: extend the list/array to the right to at least cover the requested mag
    # xn = max(mag, xp[-1]+mag)
    # yn = (yp[-1]-yp[-2])/(xp[-1]-xp[-2])*(xn-xp[-2])+yp[-2]
    # xnew = np.append(xp, xn)
    # ynew = np.append(yp, yn)
    # step 2: iterate until an intersection point is found
    x = mag
    imax = 500
    for ii in range(imax):
        y = np.interp(x, xp, yp)
        m = np.sign(x) * np.sqrt(x**2+y**2)
        if abs(m-mag) < err:
            break
        else:
            x = x+k*(mag/m*x-x)

    return x, y

# def piecewise_intercept(xp1, yp1, xp2, yp2, x, step:float=0.01):
#     """
#     Find out the intercept point of two piecewise curve defined by (xp1, yp1) and (xp2, yp2), which is smaller than x
#     If there is no intercept point, return x and y point defined by (xp2, yp2).
#     For volt-var or constant Q - (xp2, yp2) should be horizontal.
#     For const PF - (xp2, yp2) should be defined by const PF setpoint.
#     For watt-var - (xp2, yp2) should be the watt-var curve.
#
#     xp1,2: list or array on x axis
#     yp1,2: list or array on y axis
#     x: starting point
#     step: step size to search intercept point
#     """
#     if step < 1.e-5:
#         return x, np.interp(x,xp2, yp2)
#     else:
#         x_iter = x-step
#         while np.interp(x_iter, xp1, yp1)<np.interp(x_iter,xp2,yp2) and x_iter>0:
#             x_iter = x_iter - step
#         if x_iter <= 0:
#             return x, np.interp(x,xp1, yp1)
#         else:
#             x_intercept, y = piecewise_intercept(xp1, yp1,xp2, yp2, x_iter+step, step/10)
#
#     return x_intercept, np.interp(x_intercept,xp2, yp2)


class CapabilityPriority:
    """
    Calculate active and reactive power power output limited by DER ratings, according to the priority of responses.
    EPRI Report Reference: Section 3.9 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """
    def __init__(self, der_obj):
        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay

        self.p_desired_w = None     # Desired active power from DER active power support functions in per unit
        self.q_desired_var = None   # Desired reactive power from DER reactive power support functions in per unit
        self.np_va_max_appl = None     # Applicable nameplate apparent power rating depending on inject or absorb P
        self.q_max_inj = None   # Maximum reactive power injection at the desired active power output, defined by the 
                                # capability curve NP_Q_CAPABILITY_BY_P_CURVE
        self.q_max_abs = None   # Maximum reactive power absorption at the desired active power output
        self.q_limited_by_p_var = None  # Desired output reactive power after considering DER reactive power capability 
                                        # curve in volt-var or constant reactive power mode
        self.q_limited_qp_var = None    # Desired output reactive power after considering DER apparent power capability
                                        # circle in watt-var mode
        self.q_limited_pf_var = None    # Desired output reactive power after considering DER apparent power capability
                                        # circle in constant power factor mode
        self.p_limited_pf_w = None      # Desired output active power after considering DER apparent power capability 
                                        # circle in constant power factor mode

        self.p_itcp_w = None        # Intercept point P of DER apparent power capability circle and a piecewise curve
        self.q_itcp_var = None      # Intercept point Q of DER apparent power capability circle and a piecewise curve

        self.p_limited_w = None     # DER output active power after considering DER apparent power limits
        self.q_limited_var = None   # DER output reactive power after considering DER apparent power limits


        # Eq 3.9.1-2, Calculate intermediate variables of reactive power injection and absorption capability by IEEE 
        # 1547-2018
        self.q_requirement_abs = (0.25 if self.der_file.NP_NORMAL_OP_CAT == 'CAT_A' else 0.44) * self.der_file.NP_VA_MAX
        self.q_requirement_inj = 0.44 * self.der_file.NP_VA_MAX

    def calculate_limited_pq(self, p_desired_pu, q_desired_pu):
        """
        Calculate limited DER output P and Q based on DER ratings and priority of responses.

        Variables used in this function:
        :param p_desired_pu:	Desired output active power considering DER enter service performance
        :param q_desired_pu:	Desired output reactive power from reactive power support functions
        :param const_pf_mode_enable_exec:	Constant Power Factor Mode Enable (CONST_PF_MODE_ENABLE) after execution delay
        :param qv_mode_enable_exec:	Voltage-Reactive Power Mode Enable (QV_MODE_ENABLE) after execution delay
        :param qp_mode_enable_exec:	Active Power Reactive Power Mode Enable (QP_MODE_ENABLE) after execution delay
        :param const_q_mode_enable_exec:	Constant Reactive Power Mode Enable (CONST_Q_MODE_ENABLE) after execution delay
        :param NP_PRIO_OUTSIDE_MIN_Q_REQ:	Priority outside minimum requirements
        :param NP_NORMAL_OP_CAT:	Normal operating performance category
        :param NP_Q_MAX_INJ:	Reactive power injected maximum rating
        :param NP_Q_MAX_ABS:	Reactive power absorbed maximum rating
        :param NP_P_MAX:	Active power rating at unity power factor
        :param NP_VA_MAX:	Apparent power maximum rating
        :param NP_Q_CAPABILITY_BY_P_CURVE: DER reactive power capability curves (P_Q_INJ_PU, Q_MAX_INJ_PU, P_Q_ABS_PU, Q_MAX_ABS_PU)

        Outputs:
        :param p_limited_w:	DER output active power after considering DER apparent power limits
        :param q_limited_var:	DER output reactive power after considering DER apparent power limits
        """

        # Eq. 3.9.1-1 Calculate desired P and Q in watts and vars
        self.p_desired_w = p_desired_pu * self.der_file.NP_P_MAX
        self.q_desired_var = q_desired_pu * self.der_file.NP_VA_MAX
        # Eq. 3.9.1-3 Calculate applicable apparent power rating
        self.np_va_max_appl = self.der_file.NP_VA_MAX if self.p_desired_w >= 0 else self.der_file.NP_APPARENT_POWER_CHARGE_MAX

        if self.exec_delay.const_q_mode_enable_exec or self.exec_delay.qv_mode_enable_exec:
            # Constant-Q or Volt-Var
            # Eq. 3.9.1-4, find the range of DER output Q with given desired P
            self.q_max_inj = self.der_file.NP_VA_MAX * np.interp(p_desired_pu,
                                                            self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_INJ_PU'],
                                                            self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_INJ_PU'])
            self.q_max_abs = self.der_file.NP_VA_MAX * np.interp(p_desired_pu,
                                                            self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_ABS_PU'],
                                                            self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_ABS_PU'])

            # Eq. 3.9.1-5, limit q_desired_var according to limit (+injection / -absorption)
            self.q_limited_by_p_var = min(self.q_max_inj, max(-self.q_max_abs, self.q_desired_var))

            if self.p_desired_w**2+self.q_limited_by_p_var**2 < self.np_va_max_appl**2:
                # Eq. 3.9.1-6, if within DER max apparent power rating, no changes need to be made
                self.p_limited_w = self.p_desired_w
                self.q_limited_var = self.q_limited_by_p_var
            elif self.der_file.NP_PRIO_OUTSIDE_MIN_Q_REQ == 'ACTIVE':
                # Eq. 3.9.1-7 reserve Q capability to the table 7 requirement and give the rest to P
                self.q_limited_var = min(self.q_requirement_inj, max(-self.q_requirement_abs, self.q_limited_by_p_var))
                self.p_limited_w = np.sqrt(self.np_va_max_appl**2-self.q_limited_var**2) * np.sign(self.p_desired_w)

            else:
                # Eq. 3.9.1-8, Reactive power priority, reduce P to match apparent power limit
                self.q_limited_var = self.q_limited_by_p_var
                self.p_limited_w = np.sqrt(self.np_va_max_appl**2-self.q_limited_by_p_var**2) * np.sign(self.p_desired_w)

        elif self.exec_delay.const_pf_mode_enable_exec:
            # Constant-PF
            if self.p_desired_w ** 2 + self.q_desired_var ** 2 < self.np_va_max_appl ** 2:
                # Eq. 3.9.1-9, no changes to be made
                self.p_limited_pf_w = self.p_desired_w
                self.q_limited_pf_var = self.q_desired_var
            else:
                # Eq. 3.9.1-10, reduce P & Q proportionally to maintain constant power factor
                k = min(1., self.np_va_max_appl/max(1.e-9, np.sqrt(self.p_desired_w**2+self.q_desired_var**2)))
                self.p_limited_pf_w = self.p_desired_w*k
                self.q_limited_pf_var = self.q_desired_var*k

            # Find the intercept point between DER reactive power capability curve and DER apparent power capability
            # circuit, indicated as p_itcp_w and q_itcp_var
            if self.q_limited_pf_var > 0:
                # Find the capability curve for Q injection
                xp = [x*self.der_file.NP_P_MAX for x in self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_INJ_PU']]
                yp = [y*self.der_file.NP_VA_MAX for y in self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_INJ_PU']]
                # Find the intercept point
                self.p_itcp_w, self.q_itcp_var = intercep_piecewise_circle(self.np_va_max_appl if self.p_desired_w > 0 else
                                                                   -self.np_va_max_appl, xp, yp)
            else:
                # Find the capability curve for Q absorption
                xp = [x*self.der_file.NP_P_MAX for x in self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_ABS_PU']]
                yp = [y*self.der_file.NP_VA_MAX for y in self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_ABS_PU']]
                # Find the intercept point
                self.p_itcp_w, self.q_itcp_var = intercep_piecewise_circle(self.np_va_max_appl if self.p_desired_w > 0 else
                                                                   -self.np_va_max_appl, xp, yp)

            # Eq. 3.9.1-11, If DER offer capability to operate with a smaller power factor than 0.9, this model assumes
            # to reduce Q magnitude if outside of DER Q capability range. There could be other behaviors that may be
            # modeled in future version
            if abs(self.q_limited_pf_var) > self.q_itcp_var:
                # If P and Q are both beyond the intercept point, reduce P magnitude to the intercept point
                self.p_limited_w = min(abs(self.p_itcp_w), abs(self.p_desired_w)) * np.sign(self.p_desired_w)
            else:
                self.p_limited_w = self.p_limited_pf_w

            # Find the reactive power capability at P, which is already within the capability
            self.q_max_inj = self.der_file.NP_VA_MAX * np.interp(self.p_limited_w/self.der_file.NP_P_MAX,
                                                            self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_INJ_PU'],
                                                            self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_INJ_PU'])
            self.q_max_abs = self.der_file.NP_VA_MAX * np.interp(self.p_limited_w/self.der_file.NP_P_MAX,
                                                            self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_ABS_PU'],
                                                            self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_ABS_PU'])

            # Limit Q based on DER output P
            self.q_limited_var = min(self.q_max_inj, max(-self.q_max_abs, self.q_limited_pf_var))

        elif self.exec_delay.qp_mode_enable_exec:
            # Watt-Var
            if self.p_desired_w ** 2 + self.q_desired_var ** 2 < self.np_va_max_appl ** 2:
                # Eq. 3.9.1-12, no changes to be made
                self.p_limited_w = self.p_desired_w
                self.q_limited_qp_var = self.q_desired_var
            else:

                # Define watt-var curve
                qp_curve_p = [-self.der_file.NP_P_MAX_CHARGE,
                              self.exec_delay.qp_curve_p3_load_exec * self.der_file.NP_P_MAX_CHARGE,
                              self.exec_delay.qp_curve_p2_load_exec * self.der_file.NP_P_MAX_CHARGE,
                              self.exec_delay.qp_curve_p1_load_exec * self.der_file.NP_P_MAX_CHARGE,
                              self.exec_delay.qp_curve_p1_gen_exec * self.der_file.NP_P_MAX,
                              self.exec_delay.qp_curve_p2_gen_exec * self.der_file.NP_P_MAX,
                              self.exec_delay.qp_curve_p3_gen_exec * self.der_file.NP_P_MAX,
                              self.der_file.NP_P_MAX]
                qp_curve_q = [qp_curve_q * self.der_file.NP_VA_MAX for qp_curve_q in
                              [self.exec_delay.qp_curve_q3_load_exec, self.exec_delay.qp_curve_q3_load_exec,
                               self.exec_delay.qp_curve_q2_load_exec, self.exec_delay.qp_curve_q1_load_exec,
                               self.exec_delay.qp_curve_q1_gen_exec, self.exec_delay.qp_curve_q2_gen_exec,
                               self.exec_delay.qp_curve_q3_gen_exec, self.exec_delay.qp_curve_q3_gen_exec]]

                # Find intercept point of VA limit circle and watt-var curve, and assign
                # to self.p_limited_w and self.q_limited_qp_var
                if self.p_desired_w > 0:
                    self.p_itcp_w, self.q_itcp_var = intercep_piecewise_circle(self.np_va_max_appl, qp_curve_p, qp_curve_q)
                    self.p_limited_w = min(self.p_itcp_w, self.p_desired_w)
                else:
                    self.p_itcp_w, self.q_itcp_var = intercep_piecewise_circle(-self.np_va_max_appl, qp_curve_p, qp_curve_q)
                    self.p_limited_w = max(self.p_itcp_w, self.p_desired_w)
                self.q_limited_qp_var = min(abs(self.q_itcp_var), abs(self.q_desired_var))*np.sign(self.q_desired_var)

            # Eq. 3.9.1-13, reduce Q if outside of DER Q capability range
            self.q_max_inj = self.der_file.NP_VA_MAX * np.interp(self.p_desired_w/self.der_file.NP_P_MAX,
                                                            self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_INJ_PU'],
                                                            self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_INJ_PU'])
            self.q_max_abs = self.der_file.NP_VA_MAX * np.interp(self.p_desired_w/self.der_file.NP_P_MAX,
                                                            self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['P_Q_ABS_PU'],
                                                            self.der_file.NP_Q_CAPABILITY_BY_P_CURVE['Q_MAX_ABS_PU'])
            self.q_limited_var = min(self.q_max_inj, max(-self.q_max_abs, self.q_limited_qp_var))

        else:
            # undefined Q control mode
            self.p_limited_w = self.p_desired_w
            self.q_limited_var = 0

        return self.p_limited_w, self.q_limited_var




