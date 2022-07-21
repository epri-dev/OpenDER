from .der import DER
from .active_power_support_funcs.p_funcs_bess import DesiredActivePowerBESS
from .enter_service_trip.es_trip_bess import EnterServiceTripBESS
from .capability_and_priority.capability_and_priority import CapabilityPriority
from typing import Tuple, Union, List
from . import rem_ctrl
import numpy as np

class DER_BESS(DER):
    def __init__(self):
        super(DER_BESS, self).__init__()
        self._NP_Q_CAPABILITY_LOW_P = 'SAME'
        self.der_file.initialize_NP_Q_CAPABILTY_BY_P_CURVE()
        self.der_input.p_avl_pu = 1 #TODO discussion - is this the best place to set available power? Or need to change freq-droop

        # replace active power support functions and enter service
        self.activepowerfunc = DesiredActivePowerBESS(self.der_file, self.exec_delay, self.der_input)
        # self.enterservicetrip = EnterServiceTripBESS(self.der_file, self.exec_delay, self.der_input, self.der_file.STATUS_INIT)
        self.limited_p_q = CapabilityPriority(self.der_file, self.exec_delay)

    def update_der_input(self, p_dem_kw: float = None, v: Union[List[float], float] = None, theta: List[float] = None,
                         f: float = None, v_pu: Union[List[float], float] = None, p_dem_pu: float = None) -> None:
        """
        Update DER inputs
        :param p_dem_kw:	Demand AC power in kW
        :param p_dem_pu:	Demand AC power in per unit
        :param v: DER RPA voltage in Volt: if receive a float for three phase DER, all three phases are updated
        :param v_pu: DER RPA voltage in per unit: if receive a float for three phase DER, all three phases are updated
        :param theta: DER RPA voltage angles
        :param f: DER RPA frequency in Hertz
        """

        if p_dem_kw is not None:
            self.der_input.p_dem_kw = p_dem_kw

        if p_dem_pu is not None:
            self.der_input.p_dem_kw = p_dem_pu * self.der_file.NP_P_MAX

        if f is not None:
            self.der_input.freq_hz = f

        if v is not None:
            if self.der_file.NP_PHASE == "THREE":
                if type(v) is float or type(v) is int:
                    v = [v, v, v]
                self.der_input.v_a = v[0]
                self.der_input.v_b = v[1]
                self.der_input.v_c = v[2]

            if self.der_file.NP_PHASE == "SINGLE":
                self.der_input.v = v

        if v_pu is not None:
            if self.der_file.NP_PHASE == "THREE":
                v_base = self.der_file.NP_AC_V_NOM / np.sqrt(3)
                if type(v_pu) is float or type(v_pu) is int:
                    v_pu = [v_pu * v_base, v_pu * v_base, v_pu * v_base]
                else:
                    v_pu = [v_pu[0] * v_base, v_pu[1] * v_base, v_pu[2] * v_base]

                self.der_input.v_a = v_pu[0]
                self.der_input.v_b = v_pu[1]
                self.der_input.v_c = v_pu[2]

            if self.der_file.NP_PHASE == "SINGLE":
                self.der_input.v = v_pu * self.der_file.NP_AC_V_NOM

        if theta is not None:
            self.der_input.theta_a = theta[0]
            self.der_input.theta_b = theta[1]
            self.der_input.theta_c = theta[2]
