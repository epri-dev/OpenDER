from opender.auxiliary_funcs.time_delay import TimeDelay
from opender.auxiliary_funcs.cond_delay import ConditionalDelay
import numpy as np
import logging
import opender


class RideThroughCrit:
    def __init__(self, der_obj):
        """
        :NP_P_MIN_PU:	DER minimum active power output
        :ES_RANDOMIZED_DELAY_ACTUAL:	Specified value for enter service randomized delay for simulation purpose
        :NP_P_MAX:  Active power maximum rating
        :NP_VA_MAX: Apparent power maximum rating
        :STATUS_INIT:   Initial DER Status
        """

        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay
        self.der_input = der_obj.der_input

        self.der_status = der_obj.der_file.STATUS_INIT

        # self._rt_mode = None
        self.rt_mode_v = None
        self.rt_mode_f = None
        self.rt_pass_time_req = False

        self.rt_time_lv = 0
        self.rt_time_hv = 0
        self.rt_time_hf = 0
        self.rt_time_lf = 0


    def determine_ride_through_mode(self):

        if self.der_input.v_low_pu >= 0.88 and self.der_input.v_high_pu <= 1.1:
            self.rt_mode_v = 'Continuous Operation'
            self.rt_time_lv = 0
            self.rt_time_hv = 0


        if self.der_file.NP_ABNORMAL_OP_CAT == 'CAT_I':
            if 1.1 < self.der_input.v_high_pu:
                self.rt_time_hv = self.rt_time_hv + opender.DER.t_s

                if self.der_input.v_high_pu <= 1.2:
                    self.rt_mode_v = 'Permissive Operation'
                else:
                    self.rt_mode_v = 'Cease to Energize'

                if (self.rt_time_hv <= 1) and (1.1 < self.der_input.v_high_pu <= 1.15) or \
                   (self.rt_time_hv <= 0.5) and (1.15 < self.der_input.v_high_pu <= 1.175) or \
                   (self.rt_time_hv <= 0.2) and (1.175 < self.der_input.v_high_pu <= 1.2):
                    self.rt_pass_time_req = True

            if self.der_input.v_low_pu < 0.88:
                self.rt_time_lv = self.rt_time_lv + opender.DER.t_s

                if 0.7 <= self.der_input.v_low_pu < 0.88:
                    self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 0.7 + 4 * (self.der_input.v_low_pu - 0.7):
                        self.rt_pass_time_req = True

                if 0.5 <= self.der_input.v_low_pu < 0.7:
                    self.rt_mode_v = 'Permissive Operation'
                    if self.rt_time_lv > 0.16:
                        self.rt_pass_time_req = True

                if self.der_input.v_low_pu < 0.5:
                    self.rt_mode_v = 'Cease to Energize'

        if self.der_file.NP_ABNORMAL_OP_CAT == 'CAT_II':

            if 1.1 < self.der_input.v_high_pu:
                self.rt_time_hv = self.rt_time_hv + opender.DER.t_s

                if self.der_input.v_high_pu <= 1.2:
                    self.rt_mode_v = 'Permissive Operation'
                else:
                    self.rt_mode_v = 'Cease to Energize'

                if (self.rt_time_hv <= 1) and (1.1 < self.der_input.v_high_pu <= 1.15) or \
                        (self.rt_time_hv <= 0.5) and (1.15 < self.der_input.v_high_pu <= 1.175) or \
                        (self.rt_time_hv <= 0.2) and (1.15 < self.der_input.v_high_pu <= 1.2):
                    self.rt_pass_time_req = True

            if self.der_input.v_low_pu < 0.88:
                self.rt_time_lv = self.rt_time_lv + opender.DER.t_s

                if 0.65 <= self.der_input.v_low_pu < 0.88:
                    self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 3 + 8.7 * (self.der_input.v_low_pu - 0.65):
                        self.rt_pass_time_req = True

                if 0.45 <= self.der_input.v_low_pu < 0.65:
                    self.rt_mode_v = 'Permissive Operation'
                    if self.rt_time_lv > 0.32:
                        self.rt_pass_time_req = True

                if 0.3 <= self.der_input.v_low_pu < 0.45:
                    self.rt_mode_v = 'Permissive Operation'
                    if self.rt_time_lv > 0.16:
                        self.rt_pass_time_req = True

                if self.der_input.v_low_pu < 0.3:
                    self.rt_mode_v = 'Cease to Energize'


        if self.der_file.NP_ABNORMAL_OP_CAT == 'CAT_III':

            if 1.1 < self.der_input.v_high_pu:
                self.rt_time_hv = self.rt_time_hv + opender.DER.t_s

                if self.der_input.v_high_pu <= 1.2:
                    self.rt_mode_v = 'Momentary Cessation'
                else:
                    self.rt_mode_v = 'Cease to Energize'

                if self.rt_time_hv <= 12:
                    self.rt_pass_time_req = True

            if self.der_input.v_low_pu < 0.88:
                self.rt_time_lv = self.rt_time_lv + opender.DER.t_s

                if 0.7 <= self.der_input.v_low_pu < 0.88:
                    self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 20:
                        self.rt_pass_time_req = True

                if 0.5 <= self.der_input.v_low_pu < 0.7:
                    self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 10:
                        self.rt_pass_time_req = True

                if self.der_input.v_low_pu < 0.5:
                    self.rt_mode_v = 'Momentary Cessation'
                    if self.rt_time_lv > 1:
                        self.rt_pass_time_req = True

        if 58.5 <= self.der_input.freq_hz <= 61.2:
            self.rt_mode_f = 'Continuous Operation'
            self.rt_time_hf = 0
            self.rt_time_lf = 0

        if 61.2 <= self.der_input.freq_hz:
            self.rt_time_hf = self.rt_time_hf + opender.DER.t_s
            if self.der_input.freq_hz <= 61.8:
                self.rt_mode_f = 'Mandatory Operation'
            else:
                self.rt_mode_f = 'Not Defined'

            if self.rt_time_hf > 299:
                self.rt_pass_time_req = True

        if self.der_input.freq_hz <= 58.8:
            self.rt_time_lf = self.rt_time_lf + opender.DER.t_s
            if 57.0 <= self.der_input.freq_hz:
                self.rt_mode_f = 'Mandatory Operation'
            else:
                self.rt_mode_f = 'Not Defined'

            if self.rt_time_lf > 299:
                self.rt_pass_time_req = True

