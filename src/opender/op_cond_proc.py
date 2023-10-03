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


"""
Created on Thu March 24 00:45:28 2022
@author: pjan004
"""

import math
import cmath
import logging
from opender import DERCommonFileFormat
from opender import auxiliary_funcs


class DERInputs:
    """
    This module handles inputs to the DER model, and generate per unit value of applicable voltage,
    per unit available power for PV DER, per unit active power demand for BESS DER, etc.
    EPRI Report Reference: Section 3.3 in Report #3002026631: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_file: DERCommonFileFormat):

        self.der_file = der_file
        # Operating condition inputs to the DER model
        self.freq_hz = None     # Frequency at DER RPA in Hz
        self.v_a = None         # Phase a to ground voltage magnitude in volts
        self.v_b = None         # Phase b to ground voltage magnitude in volts
        self.v_c = None         # Phase c to ground voltage magnitude in volts
        self.theta_a = None     # Phase a to ground voltage angle
        self.theta_b = None     # Phase b to ground voltage angle
        self.theta_c = None     # Phase c to ground voltage angle
        self.v = None           # Single-phase RMS voltage at RPA of DER (if single-phase DER)
        self.theta = None       # Voltage angle at RPA of DER (if single-phase DER)
        self.p_dc_w = None      # Available DC power for PV
        self.p_dem_w = None     # Active power demand for BESS

        # Processed variables
        self.v_a_pu = None      # Phase a to ground voltage magnitude in per unit based on NP_AC_V_NOM/sqrt(3)
        self.v_b_pu = None      # Phase b to ground voltage magnitude in per unit based on NP_AC_V_NOM/sqrt(3)
        self.v_c_pu = None      # Phase c to ground voltage magnitude in per unit based on NP_AC_V_NOM/sqrt(3)
        self.v_ab_pu = None     # Phase a to b voltage magnitude in per unit based on NP_AC_V_NOM
        self.v_bc_pu = None     # Phase b to c voltage magnitude in per unit based on NP_AC_V_NOM
        self.v_ca_pu = None     # Phase c to a voltage magnitude in per unit based on NP_AC_V_NOM
        self.v_pos_pu = None    # Positive sequence voltage phasor as complex number at RPA
        self.v_neg_pu = None    # Negative sequence voltage phasor as complex number at RPA
        self.v_zero_pu = None   # Zero sequence voltage phasor as complex number at RPA
        self.v_angle = None     # Voltage angle at RPA in radian

        self.v_meas_pu = None   # Applicable voltage for volt-var and volt-watt calculation in per unit
        self.v_high_pu = None   # Maximum applicable voltage as enter service, over voltage trip criterion in per unit
        self.v_low_pu = None    # Minimum applicable voltage as enter service, over voltage trip criterion in per unit

        self.p_avl_pu = None    # Available power in pu considering efficiency (same value as p_dc_w for PV, 1 for BESS)
        self.p_dem_pu = None    # Active power demand for BESS

        self.v_lpf = auxiliary_funcs.low_pass_filter.LowPassFilter()    #

    def operating_condition_input_processing(self):
        """
        EPRI Report Reference: Section 3.3 in Report #3002026631: IEEE 1547-2018 OpenDER Model

        Used variables as inputs:
        :param v_a, v_b, v_c:	Three-phase line-to-ground RMS voltage at RPA
        :param theta_a, theta_b, theta_c:	Three-phase line-to-ground voltage phase angles at RPA
        :param v:	Single-phase RMS voltage at RPA of DER
        :param theta:   Single-phase voltage angle at RPA of DER
        :param p_dc_w: Available DC power
        :param p_dem_w: Active Power Demand for BESS DER
        :param NP_PHASE:	Single or Three-phase DER
        :param NP_AC_V_NOM: AC voltage base-nominal voltage rating
        :param NP_P_MAX:	Active power rating at unity power factor
        :param NP_V_MEAS_UNBALANCE: Unbalanced voltage response for volt-var and volt-watt (AVG or POS)
        :param NP_EFFICIENCY:   DC/AC conversion efficiency for PV DER
        :param NP_V_MEAS_DELAY: DER voltage measurement delay

        Outputs
        :param v_meas_pu:	Applicable voltage for volt-var and volt-watt calculation in per unit
        :param v_high_pu:	Maximum applicable voltage as enter service, over voltage trip criterion in per unit
        :param v_low_pu:	Minimum applicable voltage as enter service, over voltage trip criterion in per uni
        :param p_avl_pu:    DER available active power in per unit considering efficiency
        :param p_dem_pu:    BESS DER active power demand in per unit
        :param v_pos_pu:    Positive sequence voltage phasor as complex number at RPA
        :param v_neg_pu:    Negative sequence voltage phasor as complex number at RPA
        """

        # perform input validity check
        self.operating_conditions_validity_check()

        if self.der_file.NP_PHASE == "THREE":

            # Eq. 3.3.1-1, calculate per unit value of three phase voltage
            self.v_a_pu = (math.sqrt(3) * self.v_a) / self.der_file.NP_AC_V_NOM
            self.v_b_pu = (math.sqrt(3) * self.v_b) / self.der_file.NP_AC_V_NOM
            self.v_c_pu = (math.sqrt(3) * self.v_c) / self.der_file.NP_AC_V_NOM

            # Eq. 3.3.1-2, calculate symmetrical components and voltage angle from the positive sequence voltage
            self.v_zero_pu = (self.v_a_pu * cmath.exp(1j * self.theta_a) + (self.v_b_pu * cmath.exp(1j * self.theta_b))
                              + (self.v_c_pu * cmath.exp(1j * self.theta_c))) / 3
            self.v_pos_pu = (self.v_a_pu * cmath.exp(1j * self.theta_a)
                             + (self.v_b_pu * cmath.exp(1j * ((2 / 3) * math.pi + self.theta_b)))
                             + (self.v_c_pu * cmath.exp(1j * ((-2 / 3) * math.pi + self.theta_c)))) / 3
            self.v_neg_pu = (self.v_a_pu * cmath.exp(1j * self.theta_a)
                             + (self.v_b_pu * cmath.exp(1j * ((-2 / 3) * math.pi + self.theta_b)))
                             + (self.v_c_pu * cmath.exp(1j * ((2 / 3) * math.pi + self.theta_c)))) / 3
            self.v_angle = cmath.phase(self.v_pos_pu)

            # Eq. 3.3.1-3, if DER responds to the average of three phase RMS value
            if self.der_file.NP_V_MEAS_UNBALANCE == "AVG":
                self.v_meas_pu = self.v_lpf.low_pass_filter((self.v_a_pu + self.v_b_pu + self.v_c_pu)/3,
                                                            self.der_file.NP_V_MEAS_DELAY)

            # Eq. 3.3.1-4, if DER responds to positive sequence component of voltage.
            if self.der_file.NP_V_MEAS_UNBALANCE == "POS":
                self.v_meas_pu = self.v_lpf.low_pass_filter(abs(self.v_pos_pu), self.der_file.NP_V_MEAS_DELAY)

            # Eq. 3.3.1-5, calculate phase-to-phase voltages
            self.v_ab_pu = abs((self.v_a_pu - self.v_b_pu * cmath.exp((self.theta_b - self.theta_a)*1j)) / math.sqrt(3))
            self.v_bc_pu = abs((self.v_b_pu - self.v_c_pu * cmath.exp((self.theta_c - self.theta_b)*1j)) / math.sqrt(3))
            self.v_ca_pu = abs((self.v_c_pu - self.v_a_pu * cmath.exp((self.theta_a - self.theta_c)*1j)) / math.sqrt(3))

            # Eq. 3.3.1-6, calculate maximum and minimum voltages
            self.v_low_pu = min(self.v_a_pu, self.v_b_pu, self.v_c_pu, self.v_ab_pu, self.v_bc_pu, self.v_ca_pu)
            self.v_high_pu = max(self.v_a_pu, self.v_b_pu, self.v_c_pu, self.v_ab_pu, self.v_bc_pu, self.v_ca_pu)

        elif self.der_file.NP_PHASE == "SINGLE":

            # Eq. 3.3.1-7, single phase applicable voltages
            self.v_pos_pu = (self.v / self.der_file.NP_AC_V_NOM) * cmath.exp(1j * self.theta)
            self.v_high_pu = self.v_low_pu = (self.v / self.der_file.NP_AC_V_NOM)
            self.v_meas_pu = self.v_lpf.low_pass_filter(self.v / self.der_file.NP_AC_V_NOM,
                                                        self.der_file.NP_V_MEAS_DELAY)
            self.v_neg_pu = self.v_zero_pu = 0
            self.v_angle = cmath.phase(self.v_pos_pu)

        # Eq. 3.3.2-1, For PV DER: available power in per unit considering efficiency
        if self.p_dc_w is not None:
            self.p_avl_pu = self.p_dc_w / self.der_file.NP_P_MAX * self.der_file.NP_EFFICIENCY

        # For BESS DER
        if self.p_dem_w is not None:
            # Eq. 3.3.3-1, DER active power demand in per unit
            self.p_dem_pu = self.p_dem_w / self.der_file.NP_P_MAX
            # Eq. 3.3.3-2, DER available power is max
            self.p_avl_pu = 1

    def operating_conditions_validity_check(self):
        """
        Validity Check for DER Model operating conditions
        Reference: Table 3-5 in Report #3002026631: IEEE 1547-2018 OpenDER Model
        Should be executed every timestep
        """

        if self.der_file.NP_PHASE == "SINGLE":
            if self.v is None:
                raise ValueError("ValueError: V is not defined!")
            if self.v < 0:
                logging.error("Error: V should be greater than 0, converting it to postive")
                self.v = -self.v
            if self.theta is None:
                logging.warning("Error: Theta is not defined. Default to 0")
                self.theta = 0


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

        if self.p_dc_w is None:
            if self.der_file.NP_TYPE == 'PV':
                logging.error("ValueError: p_dc_w is not defined! Assuming 0")
            self.p_dc_w = 0

        if self.p_dc_w < 0:
            logging.warning("ValueError: p_dc_w is negative. By definition, available DC power should be positive")
            self.p_dc_w = 0

    def __str__(self):
        # Only for debug
        return f"v_meas_pu = {self.v_meas_pu}, v_high_pu = {self.v_high_pu}, v_low_pu = {self.v_low_pu}, " \
               f"freq_hz = {self.freq_hz}, p_avl_pu = {self.p_avl_pu}, p_dem_pu = {self.p_dem_pu}"
