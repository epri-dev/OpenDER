from opender.enter_service_trip.es_trip import EnterServiceTrip


class EnterServiceTripBESS(EnterServiceTrip):
    def __init__(self, der_file, exec_delay, der_input, STATUS_INIT):
        super(EnterServiceTripBESS, self).__init__(der_file, exec_delay, der_input, STATUS_INIT)

    def es_p_crit(self, p_avl_pu, NP_P_MIN_PU):
        return True
