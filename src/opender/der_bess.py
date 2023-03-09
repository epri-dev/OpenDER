# Copyright © 2023 Electric Power Research Institute, Inc. All rights reserved.
import cmath

# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# · Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# · Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# · Neither the name of the EPRI nor the names of its contributors may be used
#   to endorse or promote products derived from this software without specific
#   prior written permission.


from . import DERCommonFileFormatBESS
from .der import DER
from .active_power_support_funcs.p_funcs_bess import DesiredActivePowerBESS
# from opender.operation_status.enter_service_crit.es_crit_bess import EnterServiceCritBESS
from typing import Union, List
import numpy as np
from opender.auxiliary_funcs.sym_component import convert_symm_to_abc

class DER_BESS(DER):
    def __init__(self, der_file_obj=None):
        super(DER_BESS, self).__init__(der_file_obj)
        self.der_file.NP_Q_CAPABILITY_LOW_P = 'SAME'
        self.der_file.initialize_NP_Q_CAPABILTY_BY_P_CURVE()

        # replace active power support functions and enter service
        self.activepowerfunc = DesiredActivePowerBESS(self)
        # self.enterservicetrip = EnterServiceCritBESS(self)

    def update_der_input(self, p_dem_w: float = None, v: Union[List[float], float] = None, theta: List[float] = None,
                         v_symm_pu: List[complex] = None, f: float = None, v_pu: Union[List[float], float] = None,
                         p_dem_pu: float = None, p_dem_kw: float = None) -> None:
        """
        Update DER inputs
        :param p_dem_w: Demand AC power in W
        :param p_dem_w:	Demand AC power in kW
        :param p_dem_pu:	Demand AC power in per unit
        :param v: DER RPA voltage in Volt: if receive a float for three phase DER, all three phases are updated
        :param v_pu: DER RPA voltage in per unit: if receive a float for three phase DER, all three phases are updated
        :param v_symm_pu: DER RPA voltage in per unit as complex number for positive, negative, and zero sequences
        :param theta: DER RPA voltage angles
        :param f: DER RPA frequency in Hertz
        """

        if p_dem_w is not None:
            self.der_input.p_dem_w = p_dem_w

        if p_dem_kw is not None:
            self.der_input.p_dem_w = p_dem_kw * 1000

        if p_dem_pu is not None:
            self.der_input.p_dem_w = p_dem_pu * self.der_file.NP_P_MAX

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
            if type(v_pu) is float or type(v_pu) is int:
                self.der_input.theta = theta
            else:
                self.der_input.theta_a = theta[0]
                self.der_input.theta_b = theta[1]
                self.der_input.theta_c = theta[2]

        if v_symm_pu is not None:
            if self.der_file.NP_PHASE == "THREE":
                v_base = self.der_file.NP_AC_V_NOM / np.sqrt(3)
                v_pos = v_symm_pu[0] * v_base
                v_neg = v_symm_pu[1] * v_base
                if len(v_symm_pu)<3:
                    v_zero = 0
                else:
                    v_zero = v_symm_pu[2] * v_base

                v_a_cplx, v_b_cplx, v_c_cplx = convert_symm_to_abc(v_pos,v_neg,v_zero)
                self.der_input.v_a = abs(v_a_cplx)
                self.der_input.v_b = abs(v_b_cplx)
                self.der_input.v_c = abs(v_c_cplx)
                self.der_input.theta_a = np.angle(v_a_cplx)
                self.der_input.theta_b = np.angle(v_b_cplx)
                self.der_input.theta_c = np.angle(v_c_cplx)

            else:
                self.der_input.v = abs(v_symm_pu[0] * self.der_file.NP_AC_V_NOM)
                self.der_input.theta = np.angle(v_symm_pu[0] * self.der_file.NP_AC_V_NOM)

    def get_DERCommonFileFormat(self):
        return DERCommonFileFormatBESS()
