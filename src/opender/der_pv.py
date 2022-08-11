from .der import DER
from .enter_service_trip import EnterServiceTripPV


class DER_PV(DER):
    def __init__(self):
        super(DER_PV, self).__init__()
        # Replace enter service module to include cut-in and cut-out behavior
        self.enterservicetrip = EnterServiceTripPV(self.der_file, self.exec_delay, self.der_input, self.der_file.STATUS_INIT)


