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
from opender.auxiliary_funcs.low_pass_filter import LowPassFilter
from opender.auxiliary_funcs.ramping import Ramping
from opender.auxiliary_funcs.cond_delay import ConditionalDelay
from opender.auxiliary_funcs import sym_component


class RideThroughPerf:
    """
    Abnormal Voltage and Frequency Ride-Through Performance and DER model output calculations
    EPRI Report Reference: Section 3.10 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_obj):

        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay
        self.der_input = der_obj.der_input

        self.rt_ctrl = None     # DER ride-through control modes

        self.i_pos_pu = 0       # DER output positive sequence current phasor as complex number in per unit
        self.i_neg_pu = 0       # DER output negative sequence current phasor as complex number in per unit

        self.i_pos_lpf = LowPassFilter()
        self.i_neg_lpf = LowPassFilter()
        self.i_pos_d_rrl = Ramping()


        self.i_pos_d_ref_pu = 0     # Active current magnitude in positive sequence
        self.i_pos_q_ref_pu = 0     # Reactive current magnitude in positive sequence
        self.i_neg_ref_pu = 0       # Current phasor as complex number in negative sequence

        self.i_pos_d_limited_ref_pu = 0     # Active current magnitude in positive sequence after limitation
        self.i_pos_q_limited_ref_pu = 0     # Reactive current magnitude in positive sequence after limitation
        self.i_pos_limited_ref_pu = 0       # Positive sequence current phasor as complex number after limitation and active current ramp up limit
        self.i_neg_limited_ref_pu = 0       # Negative sequence current phasor as complex number after limitation

        self.p_limited_pu = 0       # DER output active power in per unit after considering DER apparent power limits (per unit based on NP_VA_MAX)
        self.q_limited_pu = 0       # DER output reactive power in per unit after considering DER apparent power limits (per unit based on NP_VA_MAX)


        self.rt_mc_cond_delay = ConditionalDelay()
        self.rt_cte_cond_delay = ConditionalDelay()

    def determine_rt_ctrl(self, der_status):
        """
        Determine ride-through control modes, in terms of Normal Operation, Dynamic Voltage Support, Trip, and Cease to
        Energize. More modes may be identified through lab and field experience.

        Variables used in this function:
        :param der_status:	Status of DER (Trip, Entering Service, Continuous Operation, etc)
        :param NP_CTE_RESP_T:   Cease to Energize response time
        :param MC_RESP_T:       Momentary cessation response time

        Outputs:
        :param rt_ctrl: DER ride-through control mode
        """

        # Eq 3.10.1-1, Determine ride-through control mode depending on the DER operation status.
        if der_status in ['Continuous Operation', 'Not Defined', 'Entering Service']:
            self.rt_ctrl = 'Normal Operation'

        if der_status == 'Mandatory Operation':
            if self.der_file.DVS_MODE_ENABLE:
                self.rt_ctrl = 'Dynamic Voltage Support'
            else:
                self.rt_ctrl = 'Normal Operation'

        if der_status== 'Permissive Operation':
            if self.der_file.DVS_MODE_ENABLE:
                self.rt_ctrl = 'Dynamic Voltage Support'
            else:
                self.rt_ctrl = 'Normal Operation'

        if der_status == 'Trip':
            self.rt_ctrl = 'Trip'

        # The standard allows a maximum of 0.16 s response time to enter cease to energize.
        if self.rt_cte_cond_delay.con_del_enable(der_status == 'Cease to Energize', self.der_file.NP_CTE_RESP_T):
            self.rt_ctrl = 'Cease to Energize'

        # The standard allows a maximum of 0.083 s response time to enter momentary cessation
        if self.rt_mc_cond_delay.con_del_enable(der_status == 'Momentary Cessation', self.der_file.MC_RESP_T):
            self.rt_ctrl = 'Cease to Energize'

    def der_rem_operation(self, p_limited_w, q_limited_var, der_status):
        """
        Determine DER output P and Q based on DER ride-through control modes

        Variables used in this function:
        :param p_limited_w:	DER output active power after considering DER apparent power limits
        :param q_limited_var:	DER output reactive power after considering DER apparent power limits
        :param der_status:	Status of DER (Trip, Entering Service, Continuous Operation, etc)
        :param NP_VA_MAX:	Apparent power maximum rating
        :param v_pos_pu:    Positive sequence voltage phasor as complex number at RPA
        :param v_neg_pu:    Negative sequence voltage phasor as complex number at RPA

        Outputs
        :param i_pos_pu: DER output positive sequence current phasor as complex number in per unit
        :param i_neg_pu: DER output negative sequence current phasor as complex number in per unit

        """

        # Eq 3.10.1-1 Determine ride-through control modes
        self.determine_rt_ctrl(der_status)

        # Eq 3.10.1-2, calculate per-unit values based on DER nameplate apparent power rating
        self.p_limited_pu = p_limited_w / self.der_file.NP_VA_MAX
        self.q_limited_pu = q_limited_var / self.der_file.NP_VA_MAX

        # Eq 3.10.1-3~9, Calculate DER output currents
        self.calculate_i_output(self.p_limited_pu, self.q_limited_pu)

        return self.i_pos_pu, self.i_neg_pu


    def calculate_i_output(self, p_limited_pu, q_limited_pu):
        """
        Determine DER current outputs based on DER ride-through control modes

        Variables used in this function:
        :param NP_RT_RAMP_UP_TIME: Time required for the active current restore from 0 to 100% of rated current after momentary cessation
        :param NP_INV_DELAY: Time from a step change in the current reference input until the output changes by 90% of its final change
        :param NP_REACTIVE_SUSCEPTANCE:


        """
        if self.rt_ctrl == 'Normal Operation':
            # Eq 3.10.1-3, calculate current based on desired P, Q and terminal voltage.
            self.calculate_i_continuous_op(p_limited_pu, q_limited_pu)

        if self.rt_ctrl == 'Dynamic Voltage Support':
            # Eq 3.10.1-4,calcualte current based on desired P, Q terminal voltage, and dynamic voltage support settings
            self.calculate_i_DVS(p_limited_pu, q_limited_pu)

        # Current limitation to the nameplate current rating
        self.i_pos_d_limited_ref_pu, self.i_pos_q_limited_ref_pu, self.i_neg_limited_ref_pu = self.i_limit()

        # Eq 3.10.1-8, To model the ride-through recovery performance as required in IEEE 1547-2018 Section 6.4.2.7,
        # a ramp rate limit is applied to the active current component. This ramp rate limit is only applied for ramp up
        if self.i_pos_d_limited_ref_pu > 0:
            self.i_pos_limited_ref_pu = (self.i_pos_d_rrl.ramp(self.i_pos_d_limited_ref_pu, self.der_file.NP_RT_RAMP_UP_TIME, 0) + self.i_pos_q_limited_ref_pu * 1j) * np.exp(1j * self.der_input.v_angle)
        else:
            self.i_pos_limited_ref_pu = (self.i_pos_d_rrl.ramp(self.i_pos_d_limited_ref_pu, 0, self.der_file.NP_RT_RAMP_UP_TIME) + self.i_pos_q_limited_ref_pu * 1j) * np.exp(1j * self.der_input.v_angle)

        if self.rt_ctrl == 'Cease to Energize':
            self.calculate_i_block()

        # Eq 3.10.1-10, first order lag low pass filters are applied to the DER output current references,
        # emulating the closed-loop DER inverter control delay.
        self.i_pos_pu = self.i_pos_lpf.low_pass_filter(self.i_pos_limited_ref_pu, self.der_file.NP_INV_DELAY)
        self.i_neg_pu = self.i_neg_lpf.low_pass_filter(self.i_neg_limited_ref_pu, self.der_file.NP_INV_DELAY)

        if self.rt_ctrl == 'Trip':
            # Eq 3.10.1-11, if trips, DER output no current.
            self.i_pos_pu = 0
            self.i_neg_pu = 0


    def calculate_i_continuous_op(self, p_limited_pu, q_limited_pu):
        # Eq 3.10.1-3, calculate current based on desired P, Q and terminal voltage.
        self.i_pos_d_ref_pu = p_limited_pu / abs(self.der_input.v_pos_pu)
        self.i_pos_q_ref_pu = - q_limited_pu / abs(self.der_input.v_pos_pu)
        self.i_neg_ref_pu = 0

    def calculate_i_DVS(self, p_limited_pu, q_limited_pu):
        # Eq 3.10.1-4,calcualte current based on desired P, Q terminal voltage, and dynamic voltage support settings
        self.i_pos_d_ref_pu = p_limited_pu / abs(self.der_input.v_pos_pu)
        self.i_pos_q_ref_pu = - q_limited_pu / abs(self.der_input.v_pos_pu) + (
                    abs(self.der_input.v_pos_pu) - 1) * self.der_file.DVS_K
        self.i_neg_ref_pu = self.der_input.v_neg_pu * 1j * self.der_file.DVS_K

    def calculate_i_block(self):
        # Eq 3.10.1-9, In momentary cessation condition, active current is 0, reactive currents depend on DER filter
        # susceptance.
        self.i_pos_d_limited_ref_pu = 0
        self.i_pos_q_limited_ref_pu = - abs(self.der_input.v_pos_pu) * self.der_file.NP_AC_V_NOM * \
                                    self.der_file.NP_REACTIVE_SUSCEPTANCE / (
                                            self.der_file.NP_VA_MAX / self.der_file.NP_AC_V_NOM)

        self.i_neg_limited_ref_pu = 1j * self.der_input.v_neg_pu * self.der_file.NP_AC_V_NOM * \
                                    self.der_file.NP_REACTIVE_SUSCEPTANCE / (
                                            self.der_file.NP_VA_MAX / self.der_file.NP_AC_V_NOM)



    def i_limit(self):
        # Eq 3.10.1-5 calculate maximum current if output current follows reference
        i_pos_pu = (self.i_pos_d_ref_pu + 1j * self.i_pos_q_ref_pu) * np.exp(1j * np.angle(self.der_input.v_pos_pu))
        i_max_pu = max([abs(x) for x in sym_component.convert_symm_to_abc(i_pos_pu, self.i_neg_ref_pu)])

        if i_max_pu <= self.der_file.NP_CURRENT_PU:
            # Eq 3.10.1-6, DER is able to carry out the current reference
            i_pos_out_d_pu = self.i_pos_d_ref_pu
            i_pos_out_q_pu = self.i_pos_q_ref_pu
            i_neg_out_pu = self.i_neg_ref_pu
        else:
            # Recalculate i_max_pu assuming active current is 0.
            i_pos_pu = (1j * self.i_pos_q_ref_pu) * np.exp(1j * np.angle(self.der_input.v_pos_pu))
            i_max_pu = max([abs(x) for x in sym_component.convert_symm_to_abc(i_pos_pu, self.i_neg_ref_pu)])
            if i_max_pu > self.der_file.NP_CURRENT_PU:
                # Eq 3.10.1-7, if i_max_pu is still greater than nameplate current capability, active current should be
                # 0, and reactive currents reduces proportionally.
                i_pos_out_d_pu = 0
                i_pos_out_q_pu = self.i_pos_q_ref_pu / i_max_pu * self.der_file.NP_CURRENT_PU
                i_neg_out_pu = self.i_neg_ref_pu / i_max_pu * self.der_file.NP_CURRENT_PU
            else:
                # Search the maximum active current to maximize the current output to the nameplate current capability
                tolerance = 1e-5
                step = 0.1
                scale = 0
                while step > tolerance:
                    while i_max_pu < self.der_file.NP_CURRENT_PU:
                        scale = scale + step
                        i_pos_pu = (self.i_pos_d_ref_pu * scale + 1j * self.i_pos_q_ref_pu) \
                                   * np.exp(1j * np.angle(self.der_input.v_pos_pu))
                        i_max_pu = max([abs(x) for x in sym_component.convert_symm_to_abc(i_pos_pu, self.i_neg_ref_pu)])
                        if scale > 1:
                            break
                    scale = scale - step
                    step = step * step
                    i_pos_pu = (self.i_pos_d_ref_pu * scale + 1j * self.i_pos_q_ref_pu) \
                               * np.exp(1j * np.angle(self.der_input.v_pos_pu))
                    i_max_pu = max([abs(x) for x in sym_component.convert_symm_to_abc(i_pos_pu, self.i_neg_ref_pu)])

                # Keep reactive currents and scale down active current
                i_pos_out_d_pu = self.i_pos_d_ref_pu * scale
                i_pos_out_q_pu = self.i_pos_q_ref_pu
                i_neg_out_pu = self.i_neg_ref_pu

        # # Another option to reduce all current components proportionally
        # if i_max_pu > self.der_file.NP_CURRENT_PU:
        #     i_pos_out_d_pu = self.i_pos_d_ref_pu / i_max_pu * self.der_file.NP_CURRENT_PU
        #     i_pos_out_q_pu = self.i_pos_q_ref_pu / i_max_pu * self.der_file.NP_CURRENT_PU
        #     i_neg_out_pu = self.i_neg_ref_pu / i_max_pu * self.der_file.NP_CURRENT_PU
        #
        # else:
        #     i_pos_out_d_pu = self.i_pos_d_ref_pu
        #     i_pos_out_q_pu = self.i_pos_q_ref_pu
        #     i_neg_out_pu = self.i_neg_ref_pu

        return i_pos_out_d_pu, i_pos_out_q_pu, i_neg_out_pu

    def __str__(self):
        return f"i_pos_pu = {self.i_pos_pu:.2f}, i_neg_pu = {self.i_neg_pu:.2f}"
