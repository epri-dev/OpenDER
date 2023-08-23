# Copyright © 2023 Electric Power Research Institute, Inc. All rights reserved.

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
from .bess_specifc import bess_specific
from .active_power_support_funcs.p_funcs_bess import DesiredActivePowerBESS
from typing import Union, List

class DER_BESS(DER):
    def __init__(self, der_file_obj=None, **kwargs):
        super(DER_BESS, self).__init__(der_file_obj, **kwargs)
        self.der_file.NP_Q_CAPABILITY_LOW_P = 'SAME'
        self.der_file.initialize_NP_Q_CAPABILTY_BY_P_CURVE()

        # replace active power support functions and enter service
        self.activepowerfunc = DesiredActivePowerBESS(self)
        self.bessspecific = bess_specific.BESSspecific(self)

    def update_der_input(self, p_dem_w: float = None, v: Union[List[float], float] = None,
                         theta: Union[List[float], float] = None, v_symm_pu: List[complex] = None,
                         f: float = None, v_pu: Union[List[float], float] = None,
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

        self._update_der_input_v_f(v, theta, v_symm_pu, f, v_pu)

    def get_DERCommonFileFormat(self, **kwargs):
        return DERCommonFileFormatBESS(**kwargs)

    def get_bess_soc(self) -> float:
        return self.bessspecific.soc_calc.bess_soc

    def bess_specific(self):
        self.bessspecific.run()