from opender.der import DER
import logging
import numpy as np


class StateOfCharge:
    def __init__(self, der_file):
        self.der_file = der_file
        self.bess_soc = der_file.SOC_INIT
        self.p_max_charge_pu = self.p_max_charge_pu_ts = der_file.NP_P_MAX_CHARGE
        self.p_max_discharge_pu = self.p_max_discharge_pu_ts = der_file.NP_P_MAX

    def calculate_soc(self, p_out_kw):
        p_charge_kw = p_discharge_kw = 0
        if p_out_kw is not None:
            if p_out_kw > 0:
                p_discharge_kw = p_out_kw
            else:
                p_charge_kw = - p_out_kw
        if self.der_file.NP_BESS_CAPACITY is not None:
            self.bess_soc = self.bess_soc + (((self.der_file.NP_EFFICIENCY * p_charge_kw - p_discharge_kw)
                                              / self.der_file.NP_BESS_CAPACITY) - self.der_file.NP_BESS_SELF_DISCHARGE
                                             - self.der_file.NP_BESS_SELF_DISCHARGE_SOC * self.bess_soc) * DER.t_s/3600

        if self.bess_soc >= self.der_file.NP_BESS_SOC_MAX:
            logging.warning('BESS SoC reached max')

        if self.bess_soc <= self.der_file.NP_BESS_SOC_MIN:
            logging.warning('BESS SoC reached min')

        if self.bess_soc <= 0:
            self.bess_soc = 0

    def calculate_p_max_by_soc(self):

        if DER.t_s <= 7200 and self.der_file.NP_BESS_CAPACITY is not None:  # for time series simulation
            self.p_max_charge_pu_ts = min(((self.der_file.NP_BESS_SOC_MAX - self.bess_soc) / DER.t_s * 3600 + self.der_file.NP_BESS_SELF_DISCHARGE_SOC * self.bess_soc + self.der_file.NP_BESS_SELF_DISCHARGE) * self.der_file.NP_BESS_CAPACITY / self.der_file.NP_EFFICIENCY / self.der_file.NP_P_MAX_CHARGE, 1)
            self.p_max_discharge_pu_ts = max(0, min(((self.bess_soc - self.der_file.NP_BESS_SOC_MIN) / DER.t_s * 3600 - self.der_file.NP_BESS_SELF_DISCHARGE_SOC * self.bess_soc - self.der_file.NP_BESS_SELF_DISCHARGE) * self.der_file.NP_BESS_CAPACITY / self.der_file.NP_P_MAX, 1))

        self.p_max_charge_pu = min(
            np.interp(self.bess_soc, self.der_file.NP_BESS_P_MAX_BY_SOC['SOC_P_MAX_CHARGE'],
                      self.der_file.NP_BESS_P_MAX_BY_SOC['P_CHARGE_MAX_PU']), self.p_max_charge_pu_ts)
        self.p_max_discharge_pu = min(
            np.interp(self.bess_soc, self.der_file.NP_BESS_P_MAX_BY_SOC['SOC_P_MAX_DISCHARGE'],
                      self.der_file.NP_BESS_P_MAX_BY_SOC['P_DISCHARGE_MAX_PU']), self.p_max_discharge_pu_ts)

    def reset_soc(self, soc_reset=None):
        if soc_reset is None:
            self.bess_soc = self.der_file.SOC_INIT
        else:
            self.bess_soc = soc_reset

    def __str__(self):
        return f"SoC = {self.bess_soc:.3f}, p_max_charge_kw = {self.p_max_charge_pu:.3f}, p_max_discharge_kw = {self.p_max_discharge_pu:.3f}"
