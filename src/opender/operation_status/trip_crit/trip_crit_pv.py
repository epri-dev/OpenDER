from opender.auxiliary_funcs.time_delay import TimeDelay
from opender.auxiliary_funcs.cond_delay import ConditionalDelay
import numpy as np
import logging
import opender
from .trip_crit import TripCrit

class TripCritPV(TripCrit):
    def __init__(self, der_obj):
        super(TripCritPV, self).__init__(der_obj)

    def other_trip(self):
        # Eq 3.5.2-2, if available DC power is lower than minimum DER output, trip PV DER
        self.p_min_trip = self.der_input.p_avl_pu < self.der_file.NP_P_MIN_PU
        return self.p_min_trip
