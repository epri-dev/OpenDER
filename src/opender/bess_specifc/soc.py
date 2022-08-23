from opender.der import DER
import logging
import numpy as np


class StateOfCharge:
    def __init__(self, der_file):
        self.der_file = der_file
        self.bess_soc = der_file.SOC_INIT
        self.p_max_charge_pu = self.p_max_charge_pu_ts = self.p_max_charge_pu_soc = 1
        self.p_max_discharge_pu = self.p_max_discharge_pu_ts = self.p_max_discharge_pu_soc = 1

    def calculate_soc(self, p_out_kw):

        # Eq. 3.6.3-1 assign charging and discharging power to 0
        p_charge_kw = p_discharge_kw = 0
        if p_out_kw is not None:
            if p_out_kw > 0:
                # Eq. 3.6.3-2, if discharging, assign output power in previous time step to discharge power
                p_discharge_kw = p_out_kw
            else:
                # Eq. 3.6.3-3, if charging, assign output power in previous time step to charge power
                p_charge_kw = - p_out_kw

        # Eq. 3.6.3-4, Calculate SOC based on energy capacity, efficiency, discharge rate, and simulation time step
        if self.der_file.NP_BESS_CAPACITY is not None:
            self.bess_soc = self.bess_soc + (((self.der_file.NP_EFFICIENCY * p_charge_kw - p_discharge_kw)
                                              / self.der_file.NP_BESS_CAPACITY) - self.der_file.NP_BESS_SELF_DISCHARGE
                                             - self.der_file.NP_BESS_SELF_DISCHARGE_SOC * self.bess_soc) * DER.t_s/3600

        # Generate warning if max or min SOC is reached
        if self.bess_soc >= self.der_file.NP_BESS_SOC_MAX:
            logging.warning('BESS SoC reached max')

        if self.bess_soc <= self.der_file.NP_BESS_SOC_MIN:
            logging.warning('BESS SoC reached min')

        # Set SOC to 0 if lower than 0 (it is possible in modeling due to self discharge)
        if self.bess_soc <= 0:
            self.bess_soc = 0

    def calculate_p_max_by_soc(self):

        # Eq. 3.6.3-5 Calculate maximum discharge and charge active power at current SOC, defined by the capability
        # curve NP_BESS_P_MAX_BU_SOC
        self.p_max_discharge_pu_soc = np.interp(self.bess_soc, self.der_file.NP_BESS_P_MAX_BY_SOC['SOC_P_CHARGE_MAX'],
                                                self.der_file.NP_BESS_P_MAX_BY_SOC['P_CHARGE_MAX_PU'])

        self.p_max_charge_pu_soc = np.interp(self.bess_soc, self.der_file.NP_BESS_P_MAX_BY_SOC['SOC_P_DISCHARGE_MAX'],
                                             self.der_file.NP_BESS_P_MAX_BY_SOC['P_DISCHARGE_MAX_PU'])

        # Eq. 3.6.3-6 Calculate P charge limit to avoid over-charging in the next time step
        self.p_max_charge_pu_ts = min(((self.der_file.NP_BESS_SOC_MAX - self.bess_soc) / DER.t_s * 3600 +
                                       self.der_file.NP_BESS_SELF_DISCHARGE_SOC * self.bess_soc +
                                       self.der_file.NP_BESS_SELF_DISCHARGE) * self.der_file.NP_BESS_CAPACITY /
                                      self.der_file.NP_EFFICIENCY / self.der_file.NP_P_MAX_CHARGE, 1)

        # Eq. 3.6.3-7 Calculate P discharge limit to avoid over-discharging in the next time step
        self.p_max_discharge_pu_ts = max(0, min(((self.bess_soc - self.der_file.NP_BESS_SOC_MIN) / DER.t_s * 3600 -
                                                 self.der_file.NP_BESS_SELF_DISCHARGE_SOC * self.bess_soc -
                                                 self.der_file.NP_BESS_SELF_DISCHARGE) * self.der_file.NP_BESS_CAPACITY
                                                / self.der_file.NP_P_MAX, 1))

        # Eq. 3.6.3-8 Calculate final maximum discharge/charge power using the two previously calculated limits
        self.p_max_discharge_pu = min(self.p_max_charge_pu_soc, self.p_max_discharge_pu_ts)
        self.p_max_charge_pu = min(self.p_max_discharge_pu_soc, self.p_max_charge_pu_ts)

    def snapshot_limits(self):
        # Eq. 3.6.3-8, For snapshot analysis, the operational active power limits are set to 1, so they do not
        # impact other module calculations
        self.p_max_discharge_pu = 1
        self.p_max_charge_pu = 1

    def reset_soc(self, soc_reset=None):
        if soc_reset is None:
            self.bess_soc = self.der_file.SOC_INIT
        else:
            self.bess_soc = soc_reset

    def __str__(self):
        return f"SoC = {self.bess_soc:.3f}, p_max_charge_kw = {self.p_max_charge_pu:.3f}, p_max_discharge_kw = {self.p_max_discharge_pu:.3f}"
