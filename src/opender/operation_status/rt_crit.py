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


import opender


class RideThroughCrit:
    """
    Abnormal Voltage and Frequency Ride-through Criteria
    EPRI Report Reference: Section 3.5.1.3 in Report #3002030962: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_obj):

        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay
        self.der_input = der_obj.der_input

        self.der_status = der_obj.der_file.STATUS_INIT

        self._rt_mode_v = None          # DER voltage ride-through performance mode.
        self.rt_mode_f = None           # DER frequency ride-through performance mode.
        self.rt_pass_time_req = False   # Flag indicating the minimum ride-through time has passed, and the DER is in the “may ride-through and may trip” region

        self.rt_time_lv = 0     # Low voltage ride through timer
        self.rt_time_hv = 0     # High voltage ride through timer
        self.rt_time_hf = 0     # Low frequency ride through timer
        self.rt_time_lf = 0     # High frequency ride through timer

    def determine_ride_through_mode(self):
        """
        Determine the ride-through modes for voltage and frequency ride-through, separately.
        Voltage ride-through modes include: Continuous Operation, Mandatory Operation, Permissive Operation,
        Momentary Cessation, and Cease to Energize.
        Frequency ride-through modes include: Continuous Operation, Mandatory Operation, and Not Defined

        Variable used in this function:
        :param v_high_pu:   Maximum applicable voltage as enter service, over voltage trip criterion in per unit
        :param v_low_pu:    Minimum applicable voltage as enter service, over voltage trip criterion in per unit
        :param freq_hz:     Frequency at RPA
        :param NP_ABNORMAL_OP_CAT:	DER Abnormal operating performance category
        """

        # Eq 3.5.1-8, clear and re-determine the abnormal voltage ride-through mode 
        self._rt_mode_v = None

        if self.der_file.NP_ABNORMAL_OP_CAT == 'CAT_I':
            if 1.1 < self.der_input.v_high_pu:
                # Eq 3.5.1-9, if voltage is higher than 1.1pu, high voltage ride-through timer starts to count
                self.rt_time_hv = self.rt_time_hv + opender.DER.t_s

                # Eq 3.5.1-10,11, depending on voltage level, voltage ride-through mode is determined.
                if self.der_input.v_high_pu <= 1.2:
                    self.rt_mode_v = 'Permissive Operation'
                else:
                    self.rt_mode_v = 'Cease to Energize'

                # Eq 3.5.1-12, a flag is used to indicate if any ride-through timer is greater than
                # the standard defined minimum ride through time.
                if (self.rt_time_hv <= 1) and (1.1 < self.der_input.v_high_pu <= 1.15) or \
                   (self.rt_time_hv <= 0.5) and (1.15 < self.der_input.v_high_pu <= 1.175) or \
                   (self.rt_time_hv <= 0.2) and (1.175 < self.der_input.v_high_pu <= 1.2):
                    self.rt_pass_time_req = True

            if self.der_input.v_low_pu < 0.88:
                # Eq 3.5.1-13, if voltage is lower than 0.88pu, low voltage ride-through timer starts to count
                self.rt_time_lv = self.rt_time_lv + opender.DER.t_s

                # Eq 3.5.1-14,15, determine if in mandatory operation and if passed the minimum required time
                if 0.7 <= self.der_input.v_low_pu < 0.88:
                    self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 0.7 + 4 * (self.der_input.v_low_pu - 0.7):
                        self.rt_pass_time_req = True

                # Eq 3.5.1-16,17, determine if in permissive operation and if passed the minimum required time
                if 0.5 <= self.der_input.v_low_pu < 0.7:
                    self.rt_mode_v = 'Permissive Operation'
                    if self.rt_time_lv > 0.16:
                        self.rt_pass_time_req = True

                # Eq 3.5.1-18, determine if in cease to energize region
                if self.der_input.v_low_pu < 0.5:
                    self.rt_mode_v = 'Cease to Energize'

            # Eq 3.5.1-19,20, determine if in momentary cessation region
            if self.der_file.MC_ENABLE and self.der_input.v_high_pu >= self.der_file.MC_HVRT_V1:
                self.rt_mode_v = 'Momentary Cessation'
            if self.der_file.MC_ENABLE and self.der_input.v_low_pu <= self.der_file.MC_LVRT_V1:
                self.rt_mode_v = 'Momentary Cessation'

        if self.der_file.NP_ABNORMAL_OP_CAT == 'CAT_II':

            if 1.1 < self.der_input.v_high_pu:
                # Eq 3.5.1-21, if voltage is higher than 1.1pu, high voltage ride-through timer starts to count
                self.rt_time_hv = self.rt_time_hv + opender.DER.t_s

                # Eq 3.5.1-22,23, depending on voltage level, voltage ride-through mode is determined.
                if self.der_input.v_high_pu <= 1.2:
                    self.rt_mode_v = 'Permissive Operation'
                else:
                    self.rt_mode_v = 'Cease to Energize'

                # Eq 3.5.1-24, determine if ride-through time passed the minimum required time
                if (self.rt_time_hv <= 1) and (1.1 < self.der_input.v_high_pu <= 1.15) or \
                        (self.rt_time_hv <= 0.5) and (1.15 < self.der_input.v_high_pu <= 1.175) or \
                        (self.rt_time_hv <= 0.2) and (1.15 < self.der_input.v_high_pu <= 1.2):
                    self.rt_pass_time_req = True

            if self.der_input.v_low_pu < 0.88:
                # Eq 3.5.1-25, if voltage is lower than 0.88pu, low voltage ride-through timer starts to count
                self.rt_time_lv = self.rt_time_lv + opender.DER.t_s

                # Eq 3.5.1-26,27, determine if in mandatory operation and if passed the minimum required time
                if 0.65 <= self.der_input.v_low_pu < 0.88:
                    self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 3 + 8.7 * (self.der_input.v_low_pu - 0.65):
                        self.rt_pass_time_req = True

                # Eq 3.5.1-28,29, determine if in permissive operation block 1 and if passed the minimum required time
                if 0.45 <= self.der_input.v_low_pu < 0.65:
                    self.rt_mode_v = 'Permissive Operation'
                    if self.rt_time_lv > 0.32:
                        self.rt_pass_time_req = True

                # Eq 3.5.1-30,31, determine if in permissive operation block 2 and if passed the minimum required time
                if 0.3 <= self.der_input.v_low_pu < 0.45:
                    self.rt_mode_v = 'Permissive Operation'
                    if self.rt_time_lv > 0.16:
                        self.rt_pass_time_req = True

                # Eq 3.5.1-32, determine if in cease to energize region
                if self.der_input.v_low_pu < 0.3:
                    self.rt_mode_v = 'Cease to Energize'

            # Eq 3.5.1-33,34, determine if in momentary cessation region
            if self.der_file.MC_ENABLE and self.der_input.v_high_pu >= self.der_file.MC_HVRT_V1:
                self.rt_mode_v = 'Momentary Cessation'
            if self.der_file.MC_ENABLE and self.der_input.v_low_pu <= self.der_file.MC_LVRT_V1:
                self.rt_mode_v = 'Momentary Cessation'

        if self.der_file.NP_ABNORMAL_OP_CAT == 'CAT_III':
            if 1.1 < self.der_input.v_high_pu:
                # Eq 3.5.1-35, if voltage is higher than 1.1pu, high voltage ride-through timer starts to count
                self.rt_time_hv = self.rt_time_hv + opender.DER.t_s

                # Eq 3.5.1-36,37, depending on voltage level, voltage ride-through mode is determined.
                if self.der_file.MC_ENABLE and self.der_input.v_high_pu > self.der_file.MC_HVRT_V1:
                    self.rt_mode_v = 'Momentary Cessation'
                else:
                    self.rt_mode_v = 'Mandatory Operation'
                # else:
                #     self.rt_mode_v = 'Cease to Energize'

                # Eq 3.5.1-38, determine if passed the minimum required time
                if self.rt_time_hv <= 12:
                    self.rt_pass_time_req = True

            if self.der_input.v_low_pu < 0.88:
                # Eq 3.5.1-39, if voltage is lower than 0.88pu, low voltage ride-through timer starts to count
                self.rt_time_lv = self.rt_time_lv + opender.DER.t_s

                # Eq 3.5.1-40,41, determine if in mandatory operation block 1 and if passed the minimum required time
                if 0.7 <= self.der_input.v_low_pu < 0.88:
                    self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 20:
                        self.rt_pass_time_req = True

                # Eq 3.5.1-42,43, determine if in mandatory operation block 2 and if passed the minimum required time
                if self.der_input.v_low_pu < 0.7:
                    # self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 10:
                        self.rt_pass_time_req = True

                # Eq 3.5.1-44,45, determine if in momentary cessation mode and if passed the minimum required time
                if self.der_file.MC_ENABLE and self.der_input.v_low_pu < self.der_file.MC_LVRT_V1:
                    self.rt_mode_v = 'Momentary Cessation'
                else:
                    self.rt_mode_v = 'Mandatory Operation'
                
                # Eq 3.5.1-46, Mark the ride-through time passed flag as true, to indicate actual DER may not decide to continue riding-through
                if self.der_input.v_low_pu <= 0.5 and self.rt_time_lv > 1:
                    self.rt_pass_time_req = True

        if self.der_file.NP_ABNORMAL_OP_CAT == 'CAT_IV':
            if 1.1 < self.der_input.v_high_pu:
                # Eq 3.5.1-?? if voltage is higher than 1.1pu, high voltage ride-through timer starts to count
                self.rt_time_hv = self.rt_time_hv + opender.DER.t_s

                # Eq 3.5.1-??, ??, depending on voltage level, voltage ride-through mode is determined.
                if self.der_input.v_high_pu > 1.1:
                    self.rt_mode_v = 'Mandatory Operation'

                # Eq 3.5.1-??, determine if passed the minimum required time
                if self.rt_time_hv <= 12:
                    self.rt_pass_time_req = True

            if self.der_input.v_low_pu < 0.88:
                # Eq 3.5.1-??, if voltage is lower than 0.88pu, low voltage ride-through timer starts to count
                self.rt_time_lv = self.rt_time_lv + opender.DER.t_s

                # Eq 3.5.1-??,??, determine if in mandatory operation block 1 and if passed the minimum required time
                if 0.7 <= self.der_input.v_low_pu < 0.88:
                    self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 20:
                        self.rt_pass_time_req = True

                # Eq 3.5.1-??,??, determine if in mandatory operation block 2 and if passed the minimum required time
                if 0.5 <= self.der_input.v_low_pu < 0.7:
                    self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 10:
                        self.rt_pass_time_req = True

                if 0.1 <= self.der_input.v_low_pu < 0.5:
                    self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 2:
                        self.rt_pass_time_req = True

                if self.der_input.v_low_pu < 0.1:
                    self.rt_mode_v = 'Permissive Operation'
                    if self.rt_time_lv > 1:
                        self.rt_pass_time_req = True

            # Eq 3.5.1-19,20, determine if in momentary cessation region
            if self.der_file.MC_ENABLE and self.der_input.v_high_pu >= self.der_file.MC_HVRT_V1:
                self.rt_mode_v = 'Momentary Cessation'
            if self.der_file.MC_ENABLE and self.der_input.v_low_pu <= self.der_file.MC_LVRT_V1:
                self.rt_mode_v = 'Momentary Cessation'

 
        # Eq 3.5.1-47, Continuous operation if voltage is between 0.88-1.1, reset timers
        if self.der_input.v_low_pu >= 0.88 and self.der_input.v_high_pu <= 1.1:
            self.rt_mode_v = 'Continuous Operation'
            self.rt_time_lv = 0
            self.rt_time_hv = 0

        # Eq 3.5.1-48, Continuous operation if frequency is between 58.5 and 61.2, reset timers
        if 58.5 <= self.der_input.freq_hz <= 61.2:
            self.rt_mode_f = 'Continuous Operation'
            self.rt_time_hf = 0
            self.rt_time_lf = 0

        if 61.2 <= self.der_input.freq_hz:
            # Eq 3.5.1-49, if frequency is higher than 61.2 Hz, high frequency ride-through timer starts to count
            self.rt_time_hf = self.rt_time_hf + opender.DER.t_s

            # Eq 3.5.1-50,51, depending on system frequency, frequency ride-through mode is determined.
            if self.der_input.freq_hz <= 61.8:
                self.rt_mode_f = 'Mandatory Operation'
            else:
                self.rt_mode_f = 'Not Defined'

            # Eq 3.5.1-52, determine if passed the minimum required ride-through time
            if self.rt_time_hf > 299:
                self.rt_pass_time_req = True

        if self.der_input.freq_hz <= 58.8:
            # Eq 3.5.1-53, if frequency is lower than  58.8 Hz, low frequency ride-through timer starts to count
            self.rt_time_lf = self.rt_time_lf + opender.DER.t_s

            # Eq 3.5.1-54,55, depending on system frequency, frequency ride-through mode is determined.
            if 57.0 <= self.der_input.freq_hz:
                self.rt_mode_f = 'Mandatory Operation'
            else:
                self.rt_mode_f = 'Not Defined'

            # Eq 3.5.1-56, determine if passed the minimum required ride-through time
            if self.rt_time_lf > 299:
                self.rt_pass_time_req = True

    def reset_rt_pass_time_req(self):
        """
        Called by operating_status.py to reset the ride-through time passed flag (rt_pass_time_req)
        """
        self.rt_pass_time_req = False

    @property
    def rt_mode_v(self) -> str:
        return self._rt_mode_v

    @rt_mode_v.setter
    def rt_mode_v(self, rt_mode_v):
        if (rt_mode_v == 'Continuous Operation' and self._rt_mode_v not in ['Mandatory Operation', 'Permissive Operation', 'Momentary Cessation', 'Cease to Energize']) or\
           (rt_mode_v == 'Mandatory Operation' and self._rt_mode_v not in ['Permissive Operation', 'Momentary Cessation', 'Cease to Energize']) or \
           (rt_mode_v == 'Permissive Operation' and self._rt_mode_v not in ['Momentary Cessation', 'Cease to Energize']) or \
           (rt_mode_v == 'Momentary Cessation') or (rt_mode_v == 'Cease to Energize'):
            self._rt_mode_v = rt_mode_v
        # else:
        #     print('ERROR! Mode was ', self._rt_mode_v, ' and is ', rt_mode_v)  # TODO delete this after debug




