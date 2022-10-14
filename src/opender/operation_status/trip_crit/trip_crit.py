from opender.auxiliary_funcs.time_delay import TimeDelay
from opender.auxiliary_funcs.cond_delay import ConditionalDelay
import numpy as np
import logging
import opender

class TripCrit:
    def __init__(self, der_obj: opender):
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

        self.uv1_delay = ConditionalDelay()
        self.uv2_delay = ConditionalDelay()
        self.ov1_delay = ConditionalDelay()
        self.ov2_delay = ConditionalDelay()
        self.uf1_delay = ConditionalDelay()
        self.uf2_delay = ConditionalDelay()
        self.of1_delay = ConditionalDelay()
        self.of2_delay = ConditionalDelay()

    def trip_decision(self):
        trip_crit = self.abnormal_voltage_freq_trip() or self.other_trip() or not self.exec_delay.es_permit_service_exec
        return trip_crit

    def abnormal_voltage_freq_trip(self):
        # Eq 3.5.1-6, under- and over-voltage, under- and over-frequency trip criterion using conditional delayed enable
        uv1_trip = self.uv1_delay.con_del_enable(self.der_input.v_low_pu < self.exec_delay.uv1_trip_v_exec,
                                                 self.exec_delay.uv1_trip_t_exec)
        ov1_trip = self.ov1_delay.con_del_enable(self.der_input.v_high_pu > self.exec_delay.ov1_trip_v_exec,
                                                 self.exec_delay.ov1_trip_t_exec)
        uv2_trip = self.uv2_delay.con_del_enable(self.der_input.v_low_pu < self.exec_delay.uv2_trip_v_exec,
                                                 self.exec_delay.uv2_trip_t_exec)
        ov2_trip = self.ov2_delay.con_del_enable(self.der_input.v_high_pu > self.exec_delay.ov2_trip_v_exec,
                                                 self.exec_delay.ov2_trip_t_exec)
        uf1_trip = self.uf1_delay.con_del_enable(self.der_input.freq_hz < self.exec_delay.uf1_trip_f_exec,
                                                 self.exec_delay.uf1_trip_t_exec)
        of1_trip = self.of1_delay.con_del_enable(self.der_input.freq_hz > self.exec_delay.of1_trip_f_exec,
                                                 self.exec_delay.of1_trip_t_exec)
        uf2_trip = self.uf2_delay.con_del_enable(self.der_input.freq_hz < self.exec_delay.uf2_trip_f_exec,
                                                 self.exec_delay.uf2_trip_t_exec)
        of2_trip = self.of2_delay.con_del_enable(self.der_input.freq_hz > self.exec_delay.of2_trip_f_exec,
                                                 self.exec_delay.of2_trip_t_exec)

        # Eq 3.5.1-7, final trip decision based on all trip conditions
        vf_trip = uv1_trip or ov1_trip or uv2_trip or ov2_trip \
                          or uf1_trip or of1_trip or uf2_trip or of2_trip

        # return der_status output
        return vf_trip

    def other_trip(self):
        return False
