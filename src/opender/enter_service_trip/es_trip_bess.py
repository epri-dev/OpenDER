from opender.enter_service_trip.es_trip import EnterServiceTrip


class EnterServiceTripBESS(EnterServiceTrip):
    def __init__(self, der_file, exec_delay, der_input, STATUS_INIT):
        super(EnterServiceTripBESS, self).__init__(der_file, exec_delay, der_input, STATUS_INIT)

    def es_other_crit(self):
        # Eq 3.5.3-1 BESS DER model has no other enter service criteria
        return True

    def other_trip(self):
        # Eq 3.5.3-1 BESS DER model has no other trip criteria
        return False
