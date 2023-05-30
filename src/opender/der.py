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


from .common_file_format.common_file_format import DERCommonFileFormat
from .active_power_support_funcs.p_funcs import DesiredActivePower
from .reactive_power_support_funcs.q_funcs import DesiredReactivePower
from .operation_status import OperatingStatus
from opender.operation_status.enter_service_crit.es_crit import EnterServiceCrit
from opender.capability_and_priority import CapabilityPriority
from opender.op_cond_proc import DERInputs
from . import setting_execution_delay, rt_perf
from typing import Union, List, Tuple, Any
import numpy as np
import cmath
from .output_options import DEROutputs
from opender.auxiliary_funcs.sym_component import convert_symm_to_abc


class DER:
    # Global Variables
    t_s = 100000        # Simulation time step, default for snapshot analysis

    def __init__(self, der_file_obj=None, **kwargs):
        """
        Creating a DER Object
        :param der_file_obj: DER common file format object created from common_file_format.py
        """

        self.time = 0       # Elapsed time from start of simulation
        self.name = 'DER1'  # Identification if multiple DERs are defined
        self.bus = None     # Bus which DER is connected to

        if der_file_obj is None:
            der_file_obj = self.get_DERCommonFileFormat(**kwargs)

        self.der_file = der_file_obj
        self.der_file.nameplate_value_validity_check()

        # Intermediate variables
        self.p_desired_pu = None
        self.q_desired_pu = None
        self.p_limited_w = None
        self.q_limited_var = None
        self.i_pos_pu = None
        self.i_neg_pu = None
        self.p_out_w = None
        self.q_out_var = None
        self.p_out_pu = None
        self.q_out_pu = None
        self.p_out_kw = None
        self.q_out_kvar = None

        if self.der_file.STATUS_INIT:
            self.der_status = 'Continuous Operation'
        else:
            self.der_status = 'Trip'

        # DER model modules
        self.der_input = DERInputs(self.der_file)
        self.exec_delay = setting_execution_delay.SettingExecutionDelay(self.der_file)
        self.opstatus = OperatingStatus(self)
        self.activepowerfunc = DesiredActivePower(self)
        self.reactivepowerfunc = DesiredReactivePower(self)
        self.limited_p_q = CapabilityPriority(self)
        self.ridethroughperf = rt_perf.RideThroughPerf(self)
        self.der_output = DEROutputs(self)

    def update_der_input(self, p_dc_kw: float = None, v: Union[List[float], float] = None,
                         theta: Union[List[float], float] = None, v_symm_pu: List[complex] = None, f: float = None,
                         v_pu: Union[List[float], float] = None, p_dc_pu: float = None, p_dc_w: float = None) -> None:
        """
        Update DER inputs
        :param p_dc_w: Available DC power in W
        :param p_dc_kw:	Available DC power in kW
        :param p_dc_pu:	Available DC power in per unit
        :param v: DER RPA voltage in Volt: if receive a float for three phase DER, all three phases are updated
        :param v_pu: DER RPA voltage in per unit: if receive a float for three phase DER, all three phases are updated
        :param v_symm_pu: DER RPA voltage in per unit as complex number for positive, negative, and zero sequences
        :param theta: DER RPA voltage angles
        :param f: DER RPA frequency in Hertz
        """

        if p_dc_w is not None:
            self.der_input.p_dc_w = p_dc_w

        if p_dc_kw is not None:
            self.der_input.p_dc_w = p_dc_kw * 1000

        if p_dc_pu is not None:
            self.der_input.p_dc_w = p_dc_pu * self.der_file.NP_P_MAX

        self._update_der_input_v_f(v, theta, v_symm_pu, f, v_pu)

    def _update_der_input_v_f(self, v: Union[List[float], float] = None, theta: Union[List[float], float] = None,
                              v_symm_pu: List[complex] = None, f: float = None, v_pu: Union[List[float], float] = None) -> None:
        if f is not None:
            self.der_input.freq_hz = f

        if v is not None:
            if self.der_file.NP_PHASE == "THREE":
                if isinstance(v,(int,float,np.floating,np.int_)):
                    v = [v, v, v]
                self.der_input.v_a = v[0]
                self.der_input.v_b = v[1]
                self.der_input.v_c = v[2]

            if self.der_file.NP_PHASE == "SINGLE":
                self.der_input.v = v

        if v_pu is not None:
            if self.der_file.NP_PHASE == "THREE":
                v_base = self.der_file.NP_AC_V_NOM / np.sqrt(3)
                if isinstance(v_pu,(int,float,np.floating,np.int_)):
                    v = [v_pu * v_base, v_pu * v_base, v_pu * v_base]
                else:
                    v = [v_pu[0] * v_base, v_pu[1] * v_base, v_pu[2] * v_base]

                self.der_input.v_a = v[0]
                self.der_input.v_b = v[1]
                self.der_input.v_c = v[2]

            if self.der_file.NP_PHASE == "SINGLE":
                self.der_input.v = v_pu * self.der_file.NP_AC_V_NOM

        if theta is not None:
            if isinstance(theta,(int,float,np.floating,np.int_)):
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

    def run(self) -> Tuple[float, float]:
        """
        Main calculation loop.
        Call this function once for power flow analysis, or call this function in each simulation time step in dynamic
        simulation.
        """

        # Elapsed time calculation
        self.time = self.time + self.__class__.t_s

        # Input processing
        self.der_input.operating_condition_input_processing()

        # Execution delay
        self.exec_delay.mode_and_execution_delay()

        # Determine DER operating status
        self.der_status = self.opstatus.determine_der_status()

        self.bess_specific()

        # Calculate desired active power
        self.p_desired_pu = self.activepowerfunc.calculate_p_funcs(self.p_out_w)

        # Calculate desired reactive power
        self.q_desired_pu = self.reactivepowerfunc.calculate_reactive_funcs(self.p_desired_pu, self.der_status)

        # Limit DER output based on kVA rating and DER capability curve
        self.p_limited_w, self.q_limited_var = self.limited_p_q.calculate_limited_pq(self.p_desired_pu, self.q_desired_pu)

        # Calculate DER output positive and negative sequence current based on ride-through performance
        self.i_pos_pu, self.i_neg_pu = self.ridethroughperf.der_rem_operation(self.p_limited_w, self.q_limited_var, self.der_status)

        # Generate DER model output value
        self.p_out_w, self.q_out_var = self.der_output.calculate_p_q_output(self.i_pos_pu)
        self.p_out_kw = self.der_output.p_out_kw
        self.q_out_kvar = self.der_output.q_out_kvar
        self.p_out_pu = self.der_output.p_out_pu
        self.q_out_pu = self.der_output.q_out_pu

        return self.p_out_w, self.q_out_var

    def reinitialize(self):
        # only used when need to reset DER model
        self.der_status = self.der_file.STATUS_INIT
        self.time = 0
        # self.der_input = DERInputs(self.der_file)
        self.exec_delay = setting_execution_delay.SettingExecutionDelay(self.der_file)
        self.enterservicecrit = EnterServiceCrit(self)
        self.opstatus = OperatingStatus(self)
        self.activepowerfunc = DesiredActivePower(self)
        self.reactivepowerfunc = DesiredReactivePower(self)
        self.limited_p_q = CapabilityPriority(self)
        self.ridethroughperf = rt_perf.RideThroughPerf(self)
        self.der_output = DEROutputs(self)

        self.p_out_w = None
        self.q_out_var = None

    def get_der_output(self, output: str = 'PQ_pu') -> Union[Tuple[Any, Any], Tuple[List[Any], List[Any]]]:
        if output == 'PQ_VA':
            return self.p_out_w, self.q_out_var
        elif output == 'PQ_kVA':
            return self.p_out_kw, self.q_out_kvar
        elif output == 'PQ_pu':
            return self.p_out_pu, self.q_out_pu
        elif output == 'I_A':
            self.der_output.calculate_i_output(self.i_pos_pu, self.i_neg_pu)
            return self.der_output.i_mag_amp, self.der_output.i_theta
        elif output == 'I_pu':
            self.der_output.calculate_i_output(self.i_pos_pu, self.i_neg_pu)
            return self.der_output.i_mag_pu, self.der_output.i_theta
        elif output == 'Ipn_pu':
            return self.i_pos_pu, self.i_neg_pu
        elif output == 'V_pu':
            self.der_output.calculate_v_output(self.i_pos_pu, self.i_neg_pu)
            return self.der_output.v_out_mag_pu, self.der_output.v_out_theta
        elif output == 'V_V':
            self.der_output.calculate_v_output(self.i_pos_pu, self.i_neg_pu)
            return self.der_output.v_out_mag_v, self.der_output.v_out_theta
        else:
            print("please use 'PQ_VA', 'PQ_kVA', 'PQ_pu', 'I_A', 'I_pu', 'Ipn_pu'")



    def __str__(self):
        # for debug, generate a string
        # E.g. can be used when print(DER_obj)
        return f"{self.time:.1f}: {self.name} ({self.der_status})- " \
               f"v_meas_pu={self.der_input.v_meas_pu:.5f}, " \
               f"p_desired_pu={self.p_desired_pu:.2f}, q_desired_pu={self.q_desired_pu:.2f}, " \
               f"p_out_kw={self.p_out_kw:.3f}, q_out_kvar={self.q_out_kvar:.3f}"

    def get_DERCommonFileFormat(self, **kwargs):
        return DERCommonFileFormat(**kwargs)

    def bess_specific(self):
        pass