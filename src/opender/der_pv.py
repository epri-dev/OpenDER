from .der import DER
from .operation_status.enter_service_crit import EnterServiceCritPV
from .active_power_support_funcs.p_funcs_pv import DesiredActivePowerPV


class DER_PV(DER):
    def __init__(self, der_file_obj=None):
        super(DER_PV, self).__init__(der_file_obj)
        # Replace enter service module to include cut-in and cut-out behavior

        self.enterservicetrip = EnterServiceCritPV(self)
        self.activepowerfunc = DesiredActivePowerPV(self.der_file, self.exec_delay, self.der_input)


