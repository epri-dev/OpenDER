# Copyright © 2022 Electric Power Research Institute, Inc. All rights reserved.

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


"""
Created on Thu March 24 00:45:28 2022
@author: pjan004
"""

import math
import cmath #For complex number operations
import logging
from opender.common_file_format import DERCommonFileFormat

class DERInputs:
    def __init__(self, der_file: DERCommonFileFormat):

        self.der_file = der_file
        # Operating condition inputs to the DER model
        self.freq_hz = None
        self.v_a = None
        self.v_b = None
        self.v_c = None
        self.theta_a = None
        self.theta_b = None
        self.theta_c = None
        self.v = None

        # Available DC power for PV
        self.p_dc_kw = None

        # P demand for BESS
        self.p_dem_kw = None

        # Processed variables
        self.v_meas_pu = None
        self.v_high_pu = None
        self.v_low_pu = None

        self.p_avl_pu = None
        self.p_dem_pu = None

    def operating_condition_input_processing(self):
        """
        |  Calculates the applicable voltage to be used by other modules of the DER model, as well as per-unit value of the
        available DC power
        |  EPRI Report Reference: Section 3.3 in Report #3002021694: IEEE 1547-2018 DER Model

        Used variables as inputs:
        
        :param v_a, v_b, v_c:	Three-phase line-to-ground RMS voltage at RPA
        :param theta_a, theta_b, theta_c:	Three-phase line-to-ground voltage phase angles at RPA
        :param v:	Single-phase RMS voltage at RPA of DER
        :param NP_PHASE:	Single or Three-phase DER
        :param NP_AC_V_NOM: AC voltage base-nominal voltage rating
        :param p_dc_kw: Available DC power
        :param NP_P_MAX:	Active power rating at unity power factor

        Internal variable:
        
        :param v_a_pu: Phase a to ground voltage magnitude in per unit
        :param v_b_pu: Phase b to ground voltage magnitude in per unit
        :param v_c_pu: Phase c to ground voltage magnitude in per unit
        :param v_ab_pu: Phase a to phase b voltage magnitude in per unit
        :param v_bc_pu: Phase b to phase c voltage magnitude in per unit
        :param v_ca_pu: Phase c to phase a voltage magnitude in per unit

        Output
        
        :param v_meas_pu:	Applicable voltage for volt-var and volt-watt calculation in per unit
        :param v_high_pu:	Maximum applicable voltage as enter service, over voltage trip criterion in per unit
        :param v_low_pu:	Minimum applicable voltage as enter service, over voltage trip criterion in per uni
        :param v_meas_pu:	DER available DC power in per uni
        """

        # perform input validity check
        self.operating_conditions_validity_check()

        if self.der_file.NP_PHASE == "THREE":

            # Eq. 1, calculate per unit value of three phase voltage
            v_a_pu = (math.sqrt(3) * self.v_a) / (self.der_file.NP_AC_V_NOM)
            v_b_pu = (math.sqrt(3) * self.v_b) / (self.der_file.NP_AC_V_NOM)
            v_c_pu = (math.sqrt(3) * self.v_c) / (self.der_file.NP_AC_V_NOM)

            # Eq. 2, if DER responds to the average of three phase RMS value
            if self.der_file.NP_V_MEAS_UNBALANCE == "AVG":
                self.v_meas_pu = (v_a_pu + v_b_pu + v_c_pu)/3

            # Eq. 3, if DER responds to positive sequence component of voltage.
            if self.der_file.NP_V_MEAS_UNBALANCE == "POS":
                self.v_meas_pu = abs(v_a_pu + (v_b_pu * cmath.exp(1j*((2/3)*math.pi + self.theta_b - self.theta_a)))
                                     + (v_c_pu * cmath.exp(1j*((-2/3)*math.pi + self.theta_c - self.theta_a))))/3

            # Eq. 4, calculate phase-to-phase voltages
            v_ab_pu = abs((v_a_pu - v_b_pu * cmath.exp((self.theta_b - self.theta_a)*1j)) / math.sqrt(3))
            v_bc_pu = abs((v_b_pu - v_c_pu * cmath.exp((self.theta_c - self.theta_b)*1j)) / math.sqrt(3))
            v_ca_pu = abs((v_c_pu - v_a_pu * cmath.exp((self.theta_a - self.theta_c)*1j)) / math.sqrt(3))

            # Eq. 5, calculate maximum and minimum voltages
            self.v_low_pu = min(v_a_pu, v_b_pu, v_c_pu, v_ab_pu, v_bc_pu, v_ca_pu)
            self.v_high_pu = max(v_a_pu, v_b_pu, v_c_pu, v_ab_pu, v_bc_pu, v_ca_pu)

        elif(self.der_file.NP_PHASE == "SINGLE"):

            # Eq. 6, single phase applicable voltage
            self.v_meas_pu = self.v_high_pu = self.v_low_pu = (self.v / self.der_file.NP_AC_V_NOM)

        # Eq. 7, DER power in per unit #TODO change model spec
        if self.p_dc_kw is not None:
            self.p_avl_pu = self.p_dc_kw / self.der_file.NP_P_MAX * self.der_file.NP_EFFICIENCY

        if self.p_dem_kw is not None:
            self.p_dem_pu = self.p_dem_kw / self.der_file.NP_P_MAX

        # return self.v_meas_pu, self.v_low_pu, self.v_high_pu, self.p_dc_pu

    def operating_conditions_validity_check(self):
        # Validity Check for DER Model operating conditions
        # Reference: Table 3-4 in Report #3002021694: IEEE 1547-2018 DER Model
        # Should be executed every timestep

        if self.der_file.NP_PHASE == "SINGLE":
            if self.v is None:
                raise ValueError("ValueError: V is not defined!")
            if self.v < 0:
                logging.error("Error: V should be greater than 0, converting it to postive")
                self.v = -self.v

        if self.der_file.NP_PHASE == "THREE":
            if self.v_a is None or self.v_b is None or self.v_c is None:
                raise ValueError("ValueError: V is not defined!")

            if(self.v_a < 0 or self.v_b < 0 or self.v_c < 0
                    or self.v_a != self.v_a or self.v_b != self.v_b or self.v_c != self.v_c):
                raise ValueError("ValueError: check failed for v_a, v_b, v_c")

            if self.theta_a is None:
                self.theta_a = 0
            if self.theta_b is None:
                self.theta_b = -2 * math.pi / 3
            if self.theta_c is None:
                self.theta_c = 2 * math.pi / 3


        if self.freq_hz is None:
            logging.error("Error: F is not defined! Assuming 60Hz")
            self.freq_hz = 60

        if self.p_dc_kw is None:
            if self.der_file.NP_TYPE == 'PV':
                logging.error("ValueError: p_dc_kw is not defined! Assuming 0")
            self.p_dc_kw = 0


    def __str__(self):
        return f"v_meas_pu = {self.v_meas_pu}, v_high_pu = {self.v_high_pu}, v_low_pu = {self.v_low_pu}, freq_hz = {self.freq_hz}, p_avl_pu = {self.p_avl_pu}"
