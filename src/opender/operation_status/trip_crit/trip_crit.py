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


from opender.auxiliary_funcs.cond_delay import ConditionalDelay


class TripCrit:
    """
    Trip criteria
    EPRI Report Reference: Section 3.5.1.2 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_obj):

        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay
        self.der_input = der_obj.der_input

        self.trip_crit = None   # Trip criteria met
        self.vf_trip = None     # Abnormal voltage and frequency trip criteria met
        self.uv1_trip = None    # DER trip criteria met due to under voltage must trip setting 1 (UV1)
        self.uv2_trip = None    # DER trip criteria met due to under voltage must trip setting 2 (UV2)
        self.ov1_trip = None    # DER trip criteria met due to over voltage must trip setting 1 (OV1)
        self.ov2_trip = None    # DER trip criteria met due to over voltage must trip setting 1 (OV2)
        self.uf1_trip = None    # DER trip criteria met due to under frequency must trip setting 1 (UF1)
        self.uf2_trip = None    # DER trip criteria met due to under frequency must trip setting 2 (UF2)
        self.of1_trip = None    # DER trip criteria met due to over frequency must trip setting 1 (OF1)
        self.of2_trip = None    # DER trip criteria met due to over frequency must trip setting 1 (OF2)

        self.uv1_delay = ConditionalDelay()
        self.uv2_delay = ConditionalDelay()
        self.ov1_delay = ConditionalDelay()
        self.ov2_delay = ConditionalDelay()
        self.uf1_delay = ConditionalDelay()
        self.uf2_delay = ConditionalDelay()
        self.of1_delay = ConditionalDelay()
        self.of2_delay = ConditionalDelay()

    def trip_decision(self):
        """
        Deciding Trip Criteria, if met, DER goes to "Trip" status.

        Variable used in this function:
        :param es_permit_service_exec: Permit service activated by request from the area EPS operator (ES_PERMIT_SERVICE) after execution delay

        Output:
        :param es_crit:	Enter service criteria met
        """

        # Eq 3.5.1-7 Decision depending on abnormal voltage and frequency trip settings, permit service setting,
        # and other trip criteria
        self.trip_crit = self.abnormal_voltage_freq_trip() \
                         or self.other_trip() \
                         or not self.exec_delay.es_permit_service_exec
        return self.trip_crit

    def abnormal_voltage_freq_trip(self):
        """
        Abnormal voltage and frequency trip criteria

        Variable used in this function:

        :param v_low_pu: Minimum applicable voltage as enter service, over voltage trip criterion in per unit
        :param v_high_pu: Maximum applicable voltage as enter service, over voltage trip criterion in per unit
        :param freq_hz: Frequency at RPA
        :param ov2_trip_v_exec: High voltage must trip curve point OV2 voltage setting (OV2_TRIP_V) signal after execution delay
        :param ov2_trip_t_exec: High voltage must trip curve point OV2 duration setting (OV2_TRIP_T) signal after execution delay
        :param ov1_trip_v_exec: High voltage must trip curve point OV1 voltage setting (OV1_TRIP_V) signal after execution delay
        :param ov1_trip_t_exec: High voltage must trip curve point OV1 duration setting (OV1_TRIP_T) signal after execution delay
        :param uv2_trip_v_exec: Low voltage must trip curve point UV2 voltage setting (UV2_TRIP_V) signal after execution delay
        :param uv2_trip_t_exec: Low voltage must trip curve point UV2 duration setting (UV2_TRIP_T) signal after execution delay
        :param uv1_trip_v_exec: Low voltage must trip curve point UV1 voltage setting (UV1_TRIP_V) signal after execution delay
        :param uv1_trip_t_exec: Low voltage must trip curve point UV1 duration setting (UV1_TRIP_T) signal after execution delay
        :param of2_trip_v_exec: High frequency must trip curve point OF2 voltage setting (OF2_TRIP_V) signal after execution delay
        :param of2_trip_t_exec: High frequency must trip curve point OF2 duration setting (OF2_TRIP_T) signal after execution delay
        :param of1_trip_v_exec: High frequency must trip curve point OF1 voltage setting (OF1_TRIP_V) signal after execution delay
        :param of1_trip_t_exec: High frequency must trip curve point OF1 duration setting (OF1_TRIP_T) signal after execution delay
        :param uf2_trip_v_exec: Low frequency must trip curve point UF2 voltage setting (UF2_TRIP_V) signal after execution delay
        :param uf2_trip_t_exec: Low frequency must trip curve point UF2 duration setting (UF2_TRIP_T) signal after execution delay
        :param uf1_trip_v_exec: Low frequency must trip curve point UF1 voltage setting (UF1_TRIP_V) signal after execution delay
        :param uf1_trip_t_exec: Low frequency must trip curve point UF1 duration setting (UF1_TRIP_T) signal after execution delay

        """
        # Eq 3.5.1-6, under- and over-voltage, under- and over-frequency trip criterion using conditional delayed enable
        self.uv1_trip = self.uv1_delay.con_del_enable(self.der_input.v_low_pu < self.exec_delay.uv1_trip_v_exec,
                                                      self.exec_delay.uv1_trip_t_exec)
        self.ov1_trip = self.ov1_delay.con_del_enable(self.der_input.v_high_pu > self.exec_delay.ov1_trip_v_exec,
                                                      self.exec_delay.ov1_trip_t_exec)
        self.uv2_trip = self.uv2_delay.con_del_enable(self.der_input.v_low_pu < self.exec_delay.uv2_trip_v_exec,
                                                      self.exec_delay.uv2_trip_t_exec)
        self.ov2_trip = self.ov2_delay.con_del_enable(self.der_input.v_high_pu > self.exec_delay.ov2_trip_v_exec,
                                                      self.exec_delay.ov2_trip_t_exec)
        self.uf1_trip = self.uf1_delay.con_del_enable(self.der_input.freq_hz < self.exec_delay.uf1_trip_f_exec,
                                                      self.exec_delay.uf1_trip_t_exec)
        self.of1_trip = self.of1_delay.con_del_enable(self.der_input.freq_hz > self.exec_delay.of1_trip_f_exec,
                                                      self.exec_delay.of1_trip_t_exec)
        self.uf2_trip = self.uf2_delay.con_del_enable(self.der_input.freq_hz < self.exec_delay.uf2_trip_f_exec,
                                                      self.exec_delay.uf2_trip_t_exec)
        self.of2_trip = self.of2_delay.con_del_enable(self.der_input.freq_hz > self.exec_delay.of2_trip_f_exec,
                                                      self.exec_delay.of2_trip_t_exec)

        # Part of Eq 3.5.1-7, abnormal voltage and frequency trip decision based on trip settings.
        self.vf_trip = self.uv1_trip or self.ov1_trip or self.uv2_trip or self.ov2_trip or \
                       self.uf1_trip or self.of1_trip or self.uf2_trip or self.of2_trip

        return self.vf_trip

    def other_trip(self):
        return False
