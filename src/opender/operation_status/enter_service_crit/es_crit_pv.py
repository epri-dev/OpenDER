from opender.operation_status.enter_service_crit.es_crit import EnterServiceCrit


class EnterServiceCritPV(EnterServiceCrit):
    def __init__(self, der_obj):
        super(EnterServiceCritPV, self).__init__(der_obj)
        self.es_p_crit = None
        self.p_min_trip = None

    def es_other_crit(self):
        # Eq 3.5.2-1, PV DER enters service when the available power is greater than the minimum power output
        self.es_p_crit = self.der_input.p_avl_pu >= self.der_file.NP_P_MIN_PU
        return self.es_p_crit

