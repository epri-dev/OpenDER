from .der import DER
from .active_power_support_funcs.p_funcs_bess import DesiredActivePowerBESS
from .enter_service_trip.es_trip_bess import EnterServiceTripBESS
from typing import Tuple
from . import rem_ctrl

class DER_BESS(DER):
    def __init__(self):
        super(DER_BESS, self).__init__()
        # replace active power support functions and enter service
        self.activepowerfunc = DesiredActivePowerBESS()
        self.enterservicetrip = EnterServiceTripBESS(self.der_file.STATUS_INIT)


    def run(self) -> Tuple[float, float]:
        """
        Main calculation loop.
        Call this function once for power flow analysis, or call this function in each simulation time step in dynamic
        simulation.
        """

        # Elapsed time calculation
        self.time = self.time + self.__class__.t_s

        # Input processing
        self.der_input.operating_condition_input_processing(self.der_file)

        # Execution delay
        self.executiondelay.mode_and_execution_delay(self.der_file)

        # Enter service and trip decision making
        self.der_status = self.enterservicetrip.es_decision(self.der_file, self.executiondelay, self.der_input)

        # Calculate desired active power
        self.p_act_supp_kw = self.activepowerfunc.calculate_p_act_supp_kw(self.der_file, self.executiondelay, self.der_input, self.p_out_kw)

        # Enter service ramp
        self.p_desired_kw = self.enterserviceperf.es_performance(self.der_file, self.executiondelay, self.p_act_supp_kw, self.der_status)

        # Calculate desired reactive power
        self.q_desired_kvar = self.reactivepowerfunc.calculate_reactive_funcs(self.der_file, self.executiondelay, self.der_input, self.p_desired_kw, self.der_status)

        # Limit DER output based on kVA rating and DER capability curve
        self.p_limited_kw, self.q_limited_kvar = self.limited_p_q.calculate_limited_pq(self.der_file, self.executiondelay, p_desired_kw=self.p_desired_kw,q_desired_kvar=self.q_desired_kvar)

        # Determine DER model output value
        self.p_out_kw, self.q_out_kvar = rem_ctrl.RemainingControl(self.p_limited_kw, self.q_limited_kvar)

        return self.p_out_kw,self.q_out_kvar
