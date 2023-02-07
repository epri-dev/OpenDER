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


from opender.auxiliary_funcs import low_pass_filter
from opender.auxiliary_funcs.flipflop import FlipFlop
from opender.auxiliary_funcs.time_delay import TimeDelay


class FreqDroop:
    """
    Frequency-droop Function
    EPRI Report Reference: Section 3.7.1.4 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """
    
    def __init__(self, der_obj):

        self.der_obj = der_obj
        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay
        self.der_input = der_obj.der_input

        self.p_pf_pre_pu = None         # Pre-disturbance active power output, defined by the active power output at
                                        # the point of time the frequency exceeds the deadband.
        self.p_pf_pre_pu_prev = None    # Value of variable p_pf_pre_pu in the previous time step
        self.p_out_w_prev = None       # Value of variable p_out_w (DER output active power) in the previous time step

        self.p_pf_of_pu = None      # Frequency droop active power reference for over-frequency condition
        self.p_pf_uf_pu = None      # Frequency droop active power reference for under-frequency condition
        self.pf_uf = None           # Under-frequency detected
        self.pf_of = None           # Over-frequency detected
        self.pf_uf_prev = None      # Value of variable pf_uf in the previous time step
        self.pf_of_prev = None      # Value of variable pf_of in the previous time step
        self.pf_uf_active = 0       # Frequency-droop over-frequency active
        self.pf_of_active = 0       # Frequency-droop under-frequency active
        self.pf_olrt_appl = None    # Applied open-loop response time for frequency-droop function
        self.p_pf_ref_pu = None     # Frequency droop active power reference in per unit
        self.p_pf_lpf_pu = None     # Frequency droop active power after low pass filter, before reaction time

        self.p_pf_pu = 0            # Output active power from frequency-droop function
        self.pf_uf_active = 0       # Frequency-droop under-frequency active
        self.pf_of_active = 0       # Frequency-droop over-frequency active

        self.pf_uf_active_ff = FlipFlop(0)
        self.pf_of_active_ff = FlipFlop(0)
        self.pf_lpf = low_pass_filter.LowPassFilter()
        self.pf_delay = TimeDelay()

    def calculate_p_pf_pu(self, p_out_w, ap_limit_rt, p_pv_limit_pu):
        
        """
        Calculate power reference according to frequency-droop function

        Variable used in this function:
        :param p_out_w: DER output active power in the previous time step
        :param ap_limit_rt: Active power limit due to active power limit function
        :param p_pv_limit_pu: Active power limit due to Volt-watt function
        :param freq_hz:	DER frequency measurement in Hertz, from model input
        :param pf_dbof_exec:	Over frequency deadband offset from nominal frequency signal (PF_DBOF) after execution delay
        :param pf_dbuf_exec:	Under frequency deadband offset from nominal frequency signal (PF_DBUF) after execution delay
        :param pf_kof_exec:	Over frequency slope signal (PF_KOF) after execution delay
        :param pf_kuf_exec:	Under frequency slope signal (PF_KUF) after execution delay
        :param pf_olrt_exec:	Frequency-Active power open-loop response time signal (PF_OLRT) after execution delay
        :param pf_olrt_appl:  Applied open-loop response time for frequency droop function
        :param p_avl_pu:	DER available DC power in pu
        :param NP_EFFICIENCY:	DER system efficiency for DC/AC power conversion
        :param NP_P_MIN_PU:	DER minimum active power output
        :param NP_P_MAX:	DER active power rating at unity power factor
        :param PF_MODE_ENABLE: Frequency-Active power mode enable
        :param NP_REACT_TIME:   DER grid support function reaction time

        Output:
        :param p_pf_pu:     Output active power from frequency-droop function
        :param pf_uf_active:    Frequency-droop under-frequency active
        :param pf_of_active:    Frequency-droop over-frequency active
        """

        # Eq. 3.7.1-10, detect if in under-frequency or over-frequency condition
        if(self.der_input.freq_hz < (60 - self.exec_delay.pf_dbuf_exec)) and self.der_file.PF_MODE_ENABLE:
            self.pf_uf = 1
        else:
            self.pf_uf = 0
            
        if(self.der_input.freq_hz > (60 + self.exec_delay.pf_dbof_exec)) and self.der_file.PF_MODE_ENABLE:
            self.pf_of = 1
        else:
            self.pf_of = 0

        # Initialize internal state variables for under- and over-frequency condition detection
        if self.pf_uf_prev is None:
            self.pf_uf_prev = self.pf_uf
        if self.pf_of_prev is None:
            self.pf_of_prev = self.pf_of

        # Initialize internal state variables of DER output in previous time step
        if self.p_out_w_prev is None:
            self.p_out_w_prev = min(self.get_p_pu() * self.der_file.NP_P_MAX,
                                    ap_limit_rt * self.der_file.NP_P_MAX, p_pv_limit_pu * self.der_file.NP_P_MAX)
        else:
            self.p_out_w_prev = p_out_w

        # Initialize internal state variables of pre-disturbance active power output
        if self.p_pf_pre_pu_prev is None:
            self.p_pf_pre_pu_prev = min(self.der_input.p_avl_pu, ap_limit_rt, p_pv_limit_pu)

        # Eq. 3.7.1-11, calculate pre-disturbance active power output
        if self.pf_uf == 1 and self.pf_uf_prev == 1:
            self.p_pf_pre_pu = self.p_pf_pre_pu_prev
        elif self.pf_of == 1 and self.pf_of_prev == 1:
            self.p_pf_pre_pu = self.p_pf_pre_pu_prev
        else:
            self.p_pf_pre_pu = self.p_out_w_prev / self.der_file.NP_P_MAX

        # Eq. 3.7.1-12, calculate active power reference according to frequency-droop - overfrequency
        self.p_pf_of_pu = max(self.p_pf_pre_pu - 
                              ((self.der_input.freq_hz - (60 + self.exec_delay.pf_dbof_exec)) 
                               / (60 * self.exec_delay.pf_kof_exec)),
                              self.der_file.NP_P_MIN_PU)

        # Eq. 3.7.1-13, calculate active power reference according to frequency-droop - underfrequency
        self.p_pf_uf_pu = min(self.p_pf_pre_pu + 
                              (((60 - self.exec_delay.pf_dbof_exec) - self.der_input.freq_hz) 
                               / ((60 * self.exec_delay.pf_kuf_exec)))
                              , self.der_input.p_avl_pu)

        # Eq. 3.7.1-15, calculate active power reference according to frequency-droop
        if self.pf_of == 1:
            self.p_pf_ref_pu = self.p_pf_of_pu
        elif self.pf_uf == 1:
            self.p_pf_ref_pu = self.p_pf_uf_pu
        else:
            self.p_pf_ref_pu = min(self.p_pf_normal_pu(), ap_limit_rt, p_pv_limit_pu)

        # Eq. 3.7.1-16, apply the low pass filter
        self.pf_olrt_appl = self.exec_delay.pf_olrt_exec if self.pf_uf or self.pf_of or self.pf_uf_active or self.pf_of_active else 0
        self.p_pf_lpf_pu = self.pf_lpf.low_pass_filter(self.p_pf_ref_pu, self.pf_olrt_appl - self.der_file.NP_REACT_TIME)
        self.p_pf_pu = self.pf_delay.tdelay(self.p_pf_lpf_pu, self.der_file.NP_REACT_TIME)

        # Eq. 3.7.1-17, decide if frequency droop function is active
        self.pf_uf_active = self.pf_uf_active_ff.flipflop(self.pf_uf and self.der_file.PF_MODE_ENABLE,
                                                          (not (self.pf_uf and self.der_file.PF_MODE_ENABLE))
                                                          and abs(self.p_pf_pu-self.p_pf_ref_pu)<1.e-3)

        self.pf_of_active = self.pf_of_active_ff.flipflop(self.pf_of and self.der_file.PF_MODE_ENABLE,
                                                          (not (self.pf_of and self.der_file.PF_MODE_ENABLE))
                                                          and abs(self.p_pf_pu-self.p_pf_ref_pu)<1.e-3)

        # Save the values for calculations in next time step
        self.pf_uf_prev = self.pf_uf
        self.pf_of_prev = self.pf_of
        self.p_pf_pre_pu_prev = self.p_pf_pre_pu

        return self.p_pf_pu, self.pf_uf_active, self.pf_of_active

    def p_pf_normal_pu(self):
        # Eq. 3.7.1-14, if DER is entering service, the pre-disturbance power is obtained from the DER output power
        # in the previous simulation time step.
        if self.der_obj.der_status == 'Entering Service':
            return self.der_obj.p_out_w/self.der_file.NP_P_MAX
        else:
            return self.der_input.p_avl_pu

    def get_p_pu(self):
        # For initialization of p_pf_pre_pu_prev and p_out_w_prev
        return self.der_input.p_avl_pu