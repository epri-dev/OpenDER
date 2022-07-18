from opender.enter_service_trip.es_trip import EnterServiceTrip


class EnterServiceTripBESS(EnterServiceTrip):
    def __init__(self, STATUS_INIT):
        super(EnterServiceTripBESS, self).__init__(STATUS_INIT)

    def es_p_crit(self, p_dc_pu, NP_P_MIN_PU):
        return True
