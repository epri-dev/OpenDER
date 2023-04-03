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

from opender.der import DER
import logging
import numpy as np


class StateOfCharge:
    """
    State of Charge related Models for Battery Energy Storage System (BESS) DERs
    EPRI Report Reference: Section 3.6 in Report #3002026631: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_file):
        self.der_file = der_file
        self.bess_soc = der_file.SOC_INIT
        self.p_max_charge_pu = 1            # Maximum charge power in per unit
        self.p_max_charge_pu_ts = 1         # Maximum charge power for the current timestep
        self.p_max_charge_pu_soc = 1        # Maximum charge power for the current SOC, defined by the capability curve NP_BESS_P_MAX_BY_SOC
        self.p_max_discharge_pu = 1         # Maximum discharge power in per unit
        self.p_max_discharge_pu_ts = 1      # Maximum discharge power for the current timestep
        self.p_max_discharge_pu_soc = 1     # Maximum discharge power for the current SOC, defined by the capability curve NP_BESS_P_MAX_BY_SOC

        self.p_charge_w = 0  # DER charge power in W
        self.p_discharge_w = 0  # DER discharge power in W

    def calculate_soc(self, p_out_w):
        """
        Calculate State of Charge (SoC) for BESS DER
        Variable used in this function:
        :param NP_EFFICIENCY:	DER system round-trip efficiency
        :param NP_BESS_CAPACITY:	BESS Total Energy Capacity in Wh
        :param NP_BESS_SELF_DISCHARGE:	Self-Discharge Rate (Constant)
        :param NP_BESS_SELF_DISCHARGE_SOC:	Self-Discharge Rate (SOC-dependent)
        :param t_s:	Simulation time step in seconds

        Output:
        :param bess_soc:    BESS state of charge (SOC) in per unit
        """

        # Eq. 3.6.1-1 assign charging and discharging power to 0
        self.p_charge_w = self.p_discharge_w = 0
        if p_out_w is not None:
            if p_out_w > 0:
                # Eq. 3.6.1-2, if discharging, assign output power in previous time step to discharge power
                self.p_discharge_w = p_out_w
            else:
                # Eq. 3.6.1-3, if charging, assign output power in previous time step to charge power
                self.p_charge_w = - p_out_w

        # Eq. 3.6.1-4, Calculate SOC based on energy capacity, efficiency, discharge rate, and simulation time step
        if self.der_file.NP_BESS_CAPACITY is not None:
            self.bess_soc = self.bess_soc + (((self.der_file.NP_EFFICIENCY * self.p_charge_w - self.p_discharge_w)
                                              / self.der_file.NP_BESS_CAPACITY) - self.der_file.NP_BESS_SELF_DISCHARGE
                                             - self.der_file.NP_BESS_SELF_DISCHARGE_SOC * self.bess_soc) * DER.t_s/3600

        # Generate warning if max or min SOC is reached
        if self.bess_soc >= self.der_file.NP_BESS_SOC_MAX:
            logging.warning('BESS SoC reached max')

        if self.bess_soc <= self.der_file.NP_BESS_SOC_MIN:
            logging.warning('BESS SoC reached min')

        # Eq. 3.6.1-5, Set SOC to 0 if lower than 0 (it is possible in modeling due to self discharge)
        if self.bess_soc <= 0:
            self.bess_soc = 0

    def calculate_p_max_by_soc(self):

        # Eq. 3.6.2-1 Calculate maximum discharge and charge active power at current SOC, defined by the capability
        # curve NP_BESS_P_MAX_BU_SOC
        self.p_max_discharge_pu_soc = np.interp(self.bess_soc, self.der_file.NP_BESS_P_MAX_BY_SOC['SOC_P_CHARGE_MAX'],
                                                self.der_file.NP_BESS_P_MAX_BY_SOC['P_CHARGE_MAX_PU'])

        self.p_max_charge_pu_soc = np.interp(self.bess_soc, self.der_file.NP_BESS_P_MAX_BY_SOC['SOC_P_DISCHARGE_MAX'],
                                             self.der_file.NP_BESS_P_MAX_BY_SOC['P_DISCHARGE_MAX_PU'])

        # Eq. 3.6.2-2 Calculate P charge limit to avoid over-charging in the next time step
        self.p_max_charge_pu_ts = min(((self.der_file.NP_BESS_SOC_MAX - self.bess_soc) / DER.t_s * 3600 +
                                       self.der_file.NP_BESS_SELF_DISCHARGE_SOC * self.bess_soc +
                                       self.der_file.NP_BESS_SELF_DISCHARGE) * self.der_file.NP_BESS_CAPACITY /
                                      self.der_file.NP_EFFICIENCY / self.der_file.NP_P_MAX_CHARGE, 1)

        # Eq. 3.6.2-3 Calculate P discharge limit to avoid over-discharging in the next time step
        self.p_max_discharge_pu_ts = max(0, min(((self.bess_soc - self.der_file.NP_BESS_SOC_MIN) / DER.t_s * 3600 -
                                                 self.der_file.NP_BESS_SELF_DISCHARGE_SOC * self.bess_soc -
                                                 self.der_file.NP_BESS_SELF_DISCHARGE) * self.der_file.NP_BESS_CAPACITY
                                                / self.der_file.NP_P_MAX, 1))

        # Eq. 3.6.2-4 Calculate final maximum discharge/charge power using the two previously calculated limits
        self.p_max_discharge_pu = min(self.p_max_charge_pu_soc, self.p_max_discharge_pu_ts)
        self.p_max_charge_pu = min(self.p_max_discharge_pu_soc, self.p_max_charge_pu_ts)

    def snapshot_limits(self):
        # Eq. 3.6.2-5, For snapshot analysis, the operational active power limits are set to 1, so they do not
        # impact other module calculations
        self.p_max_discharge_pu = 1
        self.p_max_charge_pu = 1

    def reset_soc(self, soc_reset=None):
        # For debug, or for simulations that need to manually set the SoC to a specific value,
        # SoC is forced to change to the initial value (SOC_INIT) or the provided value (soc_reset)

        if soc_reset is None:
            self.bess_soc = self.der_file.SOC_INIT
        else:
            self.bess_soc = soc_reset

    def __str__(self):
        return f"SoC = {self.bess_soc:.3f}, p_max_charge_w = {self.p_max_charge_pu:.3f}, p_max_discharge_w = {self.p_max_discharge_pu:.3f}"
