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


from .auxiliary_funcs import time_delay as td


class SettingExecutionDelay:
    """
    |  Modeling delayed execution of DER setting changes.
    |  EPRI Report Reference: Section 3.4 in Report #3002026631: IEEE 1547-2018 OpenDER Model
    """

    parameters_list = ['AP_LIMIT_ENABLE', 'AP_LIMIT', 'ES_RANDOMIZED_DELAY', 'ES_PERMIT_SERVICE',
                       'ES_V_LOW', 'ES_V_HIGH', 'ES_F_LOW', 'ES_F_HIGH', 'ES_DELAY', 'ES_RAMP_RATE',
                       'CONST_PF_MODE_ENABLE', 'CONST_PF_EXCITATION', 'CONST_PF', 'CONST_Q_MODE_ENABLE', 'CONST_Q',
                       'QV_MODE_ENABLE', 'QV_VREF', 'QV_VREF_AUTO_MODE',
                       'QV_VREF_TIME', 'QV_CURVE_V2', 'QV_CURVE_Q2', 'QV_CURVE_V3', 'QV_CURVE_Q3', 'QV_CURVE_V1',
                       'QV_CURVE_Q1', 'QV_CURVE_V4', 'QV_CURVE_Q4', 'QV_OLRT', 'QP_MODE_ENABLE', 'QP_CURVE_P3_GEN',
                       'QP_CURVE_P2_GEN', 'QP_CURVE_P1_GEN', 'QP_CURVE_Q3_GEN', 'QP_CURVE_Q2_GEN', 'QP_CURVE_Q1_GEN',
                       'QP_CURVE_P3_LOAD', 'QP_CURVE_P2_LOAD', 'QP_CURVE_P1_LOAD', 'QP_CURVE_Q3_LOAD',
                       'QP_CURVE_Q2_LOAD', 'QP_CURVE_Q1_LOAD', 'PV_MODE_ENABLE', 'PV_CURVE_V1', 'PV_CURVE_P1',
                       'PV_CURVE_V2', 'PV_CURVE_P2', 'PV_OLRT',
                       'OV2_TRIP_V', 'OV2_TRIP_T', 'OV1_TRIP_V', 'OV1_TRIP_T', 'UV1_TRIP_V', 'UV1_TRIP_T', 'UV2_TRIP_V',
                       'UV2_TRIP_T', 'OF2_TRIP_F', 'OF2_TRIP_T', 'OF1_TRIP_F', 'OF1_TRIP_T', 'UF1_TRIP_F', 'UF1_TRIP_T',
                       'UF2_TRIP_F', 'UF2_TRIP_T', 'PF_MODE_ENABLE', 'PF_DBOF', 'PF_DBUF', 'PF_KOF', 'PF_KUF', 'PF_OLRT'
                       ]

    __slots__ = tuple([param.lower()+'_exec' for param in parameters_list]+['tdelay', 'der_file_exec', 'der_file'])

    def __init__(self, der_file):

        self.der_file = der_file

        self.tdelay = td.TimeDelay()

        self.der_file_exec = None

        # Define variables indicating the DER control settings after execution delay
        self.es_permit_service_exec = None

        self.ap_limit_enable_exec = None
        self.pv_mode_enable_exec = None
        self.pf_mode_enable_exec = None
        self.ap_limit_exec = None

        self.pv_olrt_exec = None
        self.pv_curve_p1_exec = None
        self.pv_curve_v1_exec = None
        self.pv_curve_p2_exec = None
        self.pv_curve_v2_exec = None

        self.pf_dbuf_exec = None
        self.pf_dbof_exec = None
        self.pf_kuf_exec = None
        self.pf_kof_exec = None
        self.pf_olrt_exec = None

        self.const_pf_exec = None
        self.const_pf_excitation_exec = None
        self.const_pf_mode_enable_exec = None

        self.const_q_exec = None
        self.const_q_mode_enable_exec = None

        self.qv_olrt_exec = None
        self.qv_vref_auto_mode_exec = None
        self.qv_vref_exec = None
        self.qv_vref_time_exec = None
        self.qv_mode_enable_exec = None

        self.qv_curve_v1_exec = None
        self.qv_curve_v2_exec = None
        self.qv_curve_v3_exec = None
        self.qv_curve_v4_exec = None

        self.qv_curve_q1_exec = None
        self.qv_curve_q2_exec = None
        self.qv_curve_q3_exec = None
        self.qv_curve_q4_exec = None

        self.qp_curve_p1_gen_exec = None
        self.qp_curve_p2_gen_exec = None
        self.qp_curve_p3_gen_exec = None
        self.qp_curve_q1_gen_exec = None
        self.qp_curve_q2_gen_exec = None
        self.qp_curve_q3_gen_exec = None
        self.qp_curve_p1_load_exec = None
        self.qp_curve_p2_load_exec = None
        self.qp_curve_p3_load_exec = None
        self.qp_curve_q1_load_exec = None
        self.qp_curve_q2_load_exec = None
        self.qp_curve_q3_load_exec = None
        self.qp_mode_enable_exec = None

        self.es_v_low_exec = None
        self.es_v_high_exec = None
        self.es_f_low_exec = None
        self.es_f_high_exec = None
        self.es_delay_exec = None
        self.uv1_trip_v_exec = None
        self.uv1_trip_t_exec = None
        self.ov1_trip_t_exec = None
        self.ov1_trip_v_exec = None
        self.uv2_trip_v_exec = None
        self.uv2_trip_t_exec = None
        self.ov2_trip_v_exec = None
        self.ov2_trip_t_exec = None
        self.uf1_trip_f_exec = None
        self.uf1_trip_t_exec = None
        self.uf2_trip_f_exec = None
        self.uf2_trip_t_exec = None
        self.of1_trip_f_exec = None
        self.of1_trip_t_exec = None
        self.of2_trip_f_exec = None
        self.of2_trip_t_exec = None
        self.es_randomized_delay_exec = None
        self.es_ramp_rate_exec = None

    def mode_and_execution_delay(self):

        # Eq. 3.4.1, For each time step, execute time delay function to all settings by NP_SET_EXE_TIME
        self.der_file_exec = self.tdelay.tdelay(self.der_file, self.der_file.NP_SET_EXE_TIME)

        # Extract only the control settings from the DER common file format object
        self.ap_limit_enable_exec = self.der_file_exec.AP_LIMIT_ENABLE
        self.ap_limit_exec = self.der_file_exec.AP_LIMIT
        self.es_permit_service_exec = self.der_file_exec.ES_PERMIT_SERVICE
        self.es_v_low_exec = self.der_file_exec.ES_V_LOW
        self.es_v_high_exec = self.der_file_exec.ES_V_HIGH
        self.es_f_low_exec = self.der_file_exec.ES_F_LOW
        self.es_f_high_exec = self.der_file_exec.ES_F_HIGH
        self.es_randomized_delay_exec = self.der_file_exec.ES_RANDOMIZED_DELAY
        self.es_delay_exec = self.der_file_exec.ES_DELAY
        self.es_ramp_rate_exec = self.der_file_exec.ES_RAMP_RATE
        self.const_pf_mode_enable_exec = self.der_file_exec.CONST_PF_MODE_ENABLE
        self.const_pf_exec = self.der_file_exec.CONST_PF
        self.const_pf_excitation_exec = self.der_file_exec.CONST_PF_EXCITATION
        self.qv_mode_enable_exec = self.der_file_exec.QV_MODE_ENABLE
        self.qv_vref_auto_mode_exec = self.der_file_exec.QV_VREF_AUTO_MODE
        self.qv_vref_time_exec = self.der_file_exec.QV_VREF_TIME
        self.qv_vref_exec = self.der_file_exec.QV_VREF
        self.qv_curve_v1_exec = self.der_file_exec.QV_CURVE_V1
        self.qv_curve_q1_exec = self.der_file_exec.QV_CURVE_Q1
        self.qv_curve_v2_exec = self.der_file_exec.QV_CURVE_V2
        self.qv_curve_q2_exec = self.der_file_exec.QV_CURVE_Q2
        self.qv_curve_v3_exec = self.der_file_exec.QV_CURVE_V3
        self.qv_curve_q3_exec = self.der_file_exec.QV_CURVE_Q3
        self.qv_curve_v4_exec = self.der_file_exec.QV_CURVE_V4
        self.qv_curve_q4_exec = self.der_file_exec.QV_CURVE_Q4
        self.qv_olrt_exec = self.der_file_exec.QV_OLRT
        self.const_q_mode_enable_exec = self.der_file_exec.CONST_Q_MODE_ENABLE
        self.const_q_exec = self.der_file_exec.CONST_Q
        self.qp_mode_enable_exec = self.der_file_exec.QP_MODE_ENABLE
        self.qp_curve_p1_gen_exec = self.der_file_exec.QP_CURVE_P1_GEN
        self.qp_curve_q1_gen_exec = self.der_file_exec.QP_CURVE_Q1_GEN
        self.qp_curve_p2_gen_exec = self.der_file_exec.QP_CURVE_P2_GEN
        self.qp_curve_q2_gen_exec = self.der_file_exec.QP_CURVE_Q2_GEN
        self.qp_curve_p3_gen_exec = self.der_file_exec.QP_CURVE_P3_GEN
        self.qp_curve_q3_gen_exec = self.der_file_exec.QP_CURVE_Q3_GEN
        self.qp_curve_p1_load_exec = self.der_file_exec.QP_CURVE_P1_LOAD
        self.qp_curve_q1_load_exec = self.der_file_exec.QP_CURVE_Q1_LOAD
        self.qp_curve_p2_load_exec = self.der_file_exec.QP_CURVE_P2_LOAD
        self.qp_curve_q2_load_exec = self.der_file_exec.QP_CURVE_Q2_LOAD
        self.qp_curve_p3_load_exec = self.der_file_exec.QP_CURVE_P3_LOAD
        self.qp_curve_q3_load_exec = self.der_file_exec.QP_CURVE_Q3_LOAD
        self.pv_mode_enable_exec = self.der_file_exec.PV_MODE_ENABLE
        self.pv_curve_p1_exec = self.der_file_exec.PV_CURVE_P1
        self.pv_curve_v1_exec = self.der_file_exec.PV_CURVE_V1
        self.pv_curve_p2_exec = self.der_file_exec.PV_CURVE_P2
        self.pv_curve_v2_exec = self.der_file_exec.PV_CURVE_V2
        self.pv_olrt_exec = self.der_file_exec.PV_OLRT
        self.ov2_trip_v_exec = self.der_file_exec.OV2_TRIP_V
        self.ov2_trip_t_exec = self.der_file_exec.OV2_TRIP_T
        self.ov1_trip_v_exec = self.der_file_exec.OV1_TRIP_V
        self.ov1_trip_t_exec = self.der_file_exec.OV1_TRIP_T
        self.uv1_trip_v_exec = self.der_file_exec.UV1_TRIP_V
        self.uv1_trip_t_exec = self.der_file_exec.UV1_TRIP_T
        self.uv2_trip_v_exec = self.der_file_exec.UV2_TRIP_V
        self.uv2_trip_t_exec = self.der_file_exec.UV2_TRIP_T
        self.of2_trip_f_exec = self.der_file_exec.OF2_TRIP_F
        self.of2_trip_t_exec = self.der_file_exec.OF2_TRIP_T
        self.of1_trip_f_exec = self.der_file_exec.OF1_TRIP_F
        self.of1_trip_t_exec = self.der_file_exec.OF1_TRIP_T
        self.uf1_trip_f_exec = self.der_file_exec.UF1_TRIP_F
        self.uf1_trip_t_exec = self.der_file_exec.UF1_TRIP_T
        self.uf2_trip_f_exec = self.der_file_exec.UF2_TRIP_F
        self.uf2_trip_t_exec = self.der_file_exec.UF2_TRIP_T
        self.pf_dbof_exec = self.der_file_exec.PF_DBOF
        self.pf_dbuf_exec = self.der_file_exec.PF_DBUF
        self.pf_kof_exec = self.der_file_exec.PF_KOF
        self.pf_kuf_exec = self.der_file_exec.PF_KUF
        self.pf_olrt_exec = self.der_file_exec.PF_OLRT
