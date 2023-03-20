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

import cmath
from opender.auxiliary_funcs import sym_component


class DEROutputs:
    """
    DER model outputs, in terms of active and reactive power, currents, or voltage behind impedance
    EPRI Report Reference: Section 3.11 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_obj):

        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay
        self.der_input = der_obj.der_input

        self.p_out_pu = 0    # DER output active power in per unit based on the DER nameplate apparent power rating
        self.q_out_pu = 0    # DER output reactive power in per unit based on the DER nameplate apparent power rating
        self.p_out_w = 0     # DER output active power in Watts
        self.q_out_var = 0   # DER output reactive power in vars
        self.p_out_kw = 0    # DER output active power in kilowatts
        self.q_out_kvar = 0  # DER output reactive power in kilovars

        self.i_a_pu = 0     # DER output phase a current in per unit
        self.i_b_pu = 0     # DER output phase b current in per unit
        self.i_c_pu = 0     # DER output phase c current in per unit
        self.i_mag_pu = [0, 0, 0]   # For single phase DER: an array of a single floating number of DER output current magnitude in per unit
                                    # For three phase DER: an array of three floating numbers of DER three phase output current magnitude in per unit
        self.i_mag_amp = [0, 0, 0]  # DER output current magnitude in ampere
        self.i_theta = [0, 0, 0]    # DER output current phase angle

        self.v_pos_out_cmd_pu = 0   # DER output positive sequence voltage magnitude before limitation in per unit
        self.v_neg_out_cmd_pu = 0   # DER output negative sequence voltage magnitude before limitation in per unit

        self.v_pos_out_pu = 0       # DER output positive sequence voltage magnitude in per unit
        self.v_neg_out_pu = 0       # DER output negative sequence voltage magnitude in per unit
        self.v_a_out_pu, self.v_b_out_pu, self.v_c_out_pu = 0, 0, 0  # DER output phase voltage in per unit
        self.v_out_mag_pu = [0, 0, 0]   # For single phase DER: an array of a single floating number of DER output voltage magnitude in per unit
                                        # For three phase DER: an array of three floating numbers of DER three phase output voltage magnitude in per unit
        self.v_out_mag_v = [0, 0, 0]    # DER output voltage magnitude in volts
        self.v_out_theta = [0, 0, 0]    # DER output voltage phase angle

    def calculate_p_q_output(self, i_pos_pu):
        """
        Calculate DER output active and reactive power

        Used variables as inputs:
        :param i_pos_pu:	DER output positive sequence current in per unit
        :param v_pos_pu:	Positive sequence voltage at RPA
        :param NP_VA_MAX:	DER nameplate apparent power rating
        """
        # Eq 3.11.1-1 Calculate DER output active and reactive power based on current and voltage
        self.p_out_pu = (i_pos_pu * self.der_input.v_pos_pu.conjugate()).real
        self.q_out_pu = -(i_pos_pu * self.der_input.v_pos_pu.conjugate()).imag

        # Eq 3.11.1-2 Calculate DER output P and Q in watts, vars
        self.p_out_w = self.p_out_pu * self.der_file.NP_VA_MAX
        self.q_out_var = self.q_out_pu * self.der_file.NP_VA_MAX

        # Eq 3.11.1-3 Calculate DER output P and Q in kW and kvar
        self.p_out_kw = self.p_out_w * 1e-3
        self.q_out_kvar = self.q_out_var * 1e-3

        return self.p_out_w, self.q_out_var

    def calculate_i_output(self, i_pos_pu, i_neg_pu):
        """
        Calculate DER output currents

        Used variables as inputs:
        :param i_pos_pu:	DER output positive sequence current in per unit
        :param i_neg_pu	DER output negative sequence current in per unit
        :param v_pos_pu:	Positive sequence voltage at RPA
        :param v_neg_pu:	Negative sequence voltage at RPA
        :param v_angle:	Voltage angle at RPA in radian
        :param NP_VA_MAX:	DER nameplate apparent power rating
        :param NP_AC_V_NOM:	AC voltage base—nominal voltage rating
        :param NP_PHASE:	Single- or Three-phase DER
        """

        if self.der_file.NP_PHASE == "THREE":
            # Eq 3.11.2-1, calculate three phase current
            self.i_a_pu, self.i_b_pu, self.i_c_pu = sym_component.convert_symm_to_abc(i_pos_pu, i_neg_pu)

            self.i_mag_pu = [abs(self.i_a_pu), abs(self.i_b_pu), abs(self.i_c_pu)]

            # Eq 3.11.2-2, calculate three phase current in ampere
            self.i_mag_amp = [i * self.der_file.NP_VA_MAX / self.der_file.NP_AC_V_NOM * 0.5773502691896258 for i in
                              self.i_mag_pu]

            # Eq 3.11.2-3, Calculate current phase angles
            self.i_theta = [cmath.phase(self.i_a_pu), cmath.phase(self.i_b_pu), cmath.phase(self.i_c_pu)]
        else:
            # Eq 3.11.2-4, calculate current amplitude and angles for single phase DER
            self.i_mag_pu = [abs(i_pos_pu)]
            self.i_mag_amp = [self.i_mag_pu * self.der_file.NP_VA_MAX / self.der_file.NP_AC_V_NOM]
            self.i_theta = [cmath.phase(i_pos_pu)]

    def calculate_v_output(self, i_pos_pu, i_neg_pu):
        """
        Calculate DER output currents

        Used variables as inputs:
        :param i_pos_pu:	DER output positive sequence current in per unit
        :param i_neg_pu	DER output negative sequence current in per unit
        :param v_pos_pu:	Positive sequence voltage at RPA
        :param v_neg_pu:	Negative sequence voltage at RPA
        :param v_angle:	Voltage angle at RPA in radian
        :param NP_VA_MAX:	DER nameplate apparent power rating
        :param NP_AC_V_NOM:	AC voltage base—nominal voltage rating
        :param NP_PHASE:	Single- or Three-phase DER
        :param P_RESISTANCE:	DER source resistance for voltage output
        :param NP_REACTANCE:	DER source reactance for voltage output
        """

        # Eq 3.11.3-1, calculate DER output voltage based on measured voltage, calculated current and impedance
        self.v_pos_out_cmd_pu = self.der_input.v_pos_pu + i_pos_pu * (self.der_file.NP_RESISTANCE + 1j * self.der_file.NP_REACTANCE)
        self.v_neg_out_cmd_pu = self.der_input.v_neg_pu + i_neg_pu * (self.der_file.NP_RESISTANCE + 1j * self.der_file.NP_REACTANCE)

        # Limit output voltage based on DER inverter DC voltage
        self.v_pos_out_pu, self.v_neg_out_pu = self.v_limit(self.v_pos_out_cmd_pu, self.v_neg_out_cmd_pu)

        if self.der_file.NP_PHASE == "THREE":
            # Eq 3.11.3-4, Calculate three phase voltages in per unit based on limited positive and negative voltage
            self.v_a_out_pu, self.v_b_out_pu, self.v_c_out_pu = sym_component.convert_symm_to_abc(self.v_pos_out_pu, self.v_neg_out_pu)
            self.v_out_mag_pu = [abs(self.v_a_out_pu), abs(self.v_b_out_pu), abs(self.v_c_out_pu)]

            # Eq 3.11.3-5, Calculate three phase voltage in volts
            self.v_out_mag_v = [i * self.der_file.NP_AC_V_NOM * 0.5773502691896258 for i in self.v_out_mag_pu]

            # Eq 3.11.3-6, Calculate three phase voltage angles
            self.v_out_theta = [cmath.phase(self.v_a_out_pu), cmath.phase(self.v_b_out_pu), cmath.phase(self.v_c_out_pu)]
        else:

            # Eq 3.11.3-7~9, Calculate three phase voltage angles
            self.v_out_mag_pu = [abs(self.v_pos_out_pu)]
            self.v_out_mag_v = [self.v_out_mag_pu * self.der_file.NP_AC_V_NOM]
            self.v_out_theta = [cmath.phase(self.v_pos_out_pu)]

    def v_limit(self, pos_pu, neg_pu):
        v_limit = self.der_file.NP_V_DC / self.der_file.NP_AC_V_NOM

        # Eq 3.11.3-2, calculate maximum phase voltage
        v_max_pu = max([abs(x) for x in sym_component.convert_symm_to_abc(pos_pu, neg_pu)])
        if v_max_pu > v_limit:
            # Eq 3.11.3-3 reduce voltage output to the voltage limited by the DER inverter DC voltage
            pos_out_pu = pos_pu * v_limit / v_max_pu
            neg_out_pu = neg_pu * v_limit / v_max_pu
        else:
            pos_out_pu = pos_pu
            neg_out_pu = neg_pu

        return pos_out_pu, neg_out_pu
