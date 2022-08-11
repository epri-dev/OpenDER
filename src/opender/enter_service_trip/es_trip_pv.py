from opender.enter_service_trip.es_trip import EnterServiceTrip


class EnterServiceTripPV(EnterServiceTrip):
    def __init__(self, der_file, exec_delay, der_input, STATUS_INIT):
        super(EnterServiceTripPV, self).__init__(der_file, exec_delay, der_input, STATUS_INIT)
        self.es_p_crit = None
        self.p_min_trip = None

    def es_other_crit(self):
        # Eq 3.5.2-1, PV DER enters service when the available power is greater than the minimum power output
        self.es_p_crit = self.der_input.p_avl_pu >= self.der_file.NP_P_MIN_PU
        return self.es_p_crit

    def other_trip(self):
        # Eq 3.5.2-2, if available DC power is lower than minimum DER output, trip PV DER
        self.p_min_trip = self.der_input.p_avl_pu < self.der_file.NP_P_MIN_PU
        return self.p_min_trip
