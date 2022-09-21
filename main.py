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

# -*- coding: utf-8 -*-

import pathlib
import os
import matplotlib.pyplot as plt
import opender as der


# Define DER parameter configuration directory (optional)
script_path = pathlib.Path(os.path.dirname(__file__))
as_file_path = script_path.joinpath("src", "opender", "Parameters", "AS-with std-values.csv")
model_file_path = script_path.joinpath("src", "opender","Parameters", "Model-parameters.csv")
file_ss_obj = der.common_file_format.DERCommonFileFormat(as_file_path, model_file_path)

# creating DER
der_test = der.DER(file_ss_obj)


# assign simulation time step
t_s = 1
der.DER.t_s = t_s
t = 0

# prepare arrays for plotting
t_plot = []
v_plot = []
pdc_plot = []
p_plot = []
q_plot = []
stat_plot = []
debug_plot = []


# test different DER settings

# der_test.der_file.NP_Q_CAPABILITY_BY_P_CURVE={
#     'P_Q_INJ_PU': [0, 1],
#     'P_Q_ABS_PU': [0, 1],
#     'Q_MAX_INJ_PU': [1, 1],
#     'Q_MAX_ABS_PU': [1, 1]
# }

der_test.der_file.QV_MODE_ENABLE = True
# der_test.der_file.NP_Q_MAX_INJ = 44
# der_test.der_file.NP_Q_MAX_ABS = 44
# der_test.der_file.NP_VA_MAX = 100
# der_test.der_file.NP_EFFICIENCY = 0.97
# der_test.der_file.NP_PRIO_OUTSIDE_MIN_Q_REQ = 'ACTIVE'

# der_test.der_file.QV_CURVE_V1=0.92
# der_test.der_file.QV_CURVE_Q1=0.44
# der_test.der_file.QV_CURVE_V2=0.98
# der_test.der_file.QV_CURVE_Q2=0
# der_test.der_file.QV_CURVE_V3=1.02
# der_test.der_file.QV_CURVE_Q3=0
# der_test.der_file.QV_CURVE_V4=1.08
# der_test.der_file.QV_CURVE_Q4=-0.44
# der_test.der_file.QV_OLRT = 5
#
# der_test.der_file.CONST_PF_EXCITATION = 'INJ'
# der_test.der_file.CONST_PF = 0.5
#

# der_test.der_file.ES_DELAY = 300
# der_test.der_file.OV2_TRIP_V=1.2
# der_test.der_file.OV2_TRIP_T=0.16
# der_test.der_file.OV1_TRIP_V=1.1
# der_test.der_file.OV1_TRIP_T=13
# der_test.der_file.UV1_TRIP_V=0.88
# der_test.der_file.UV1_TRIP_T=21
# der_test.der_file.UV2_TRIP_V=0.5
# der_test.der_file.UV2_TRIP_T=2
# der_test.der_file.OF2_TRIP_F=62
# der_test.der_file.OF2_TRIP_T=0.16
# der_test.der_file.OF1_TRIP_F=61.2
# der_test.der_file.OF1_TRIP_T=300
# der_test.der_file.UF1_TRIP_F=58.5
# der_test.der_file.UF1_TRIP_T=300
# der_test.der_file.UF2_TRIP_F=56.5
# der_test.der_file.UF2_TRIP_T=0.16
# der_test.der_file.ES_RAMP_RATE = 300
# der_test.der_file.ES_RANDOMIZED_DELAY = 0
#
# der_test.der_file.PV_CURVE_P1 = 1
# der_test.der_file.PV_CURVE_V1 = 1.06
# der_test.der_file.PV_CURVE_P2 = 0
# der_test.der_file.PV_CURVE_V2 = 1.1
# der_test.der_file.PV_OLRT = 10

# der_test.der_file.AP_LIMIT_ENABLE = True
# der_test.der_file.AP_LIMIT = 0.5
# der_test.der_file.PV_MODE_ENABLE = True

# der_test.der_file.QV_MODE_ENABLE = 1
# der_test.der_file.CONST_PF_MODE_ENABLE = 1
# der_test.der_file.PV_MODE_ENABLE = 1

# der_test.der_file.QV_VREF_AUTO_MODE = 1
# der_test.der_file.ES_RANDOMIZED_DELAY_ACTUAL = 100
# p_profile = [10,30,50,70,90,100,110]
# v_profile = [0.915, 0.925, 0.95, 0.975, 0.985, 1.015, 1.025, 1.05, 1.075, 1.085]
# v_profile = [1.01, 1.03, 1.05, 1.07, 1.09, 1.095]
# p_profile = [0, 4, 8, 12, 16, 20, 24]

# v_profile_vw = [[1.09, 1.09, 1.06, 0, -2.0944, 2.0944],
#               [1.09, 1.06, 1.09, 0, -2.0944, 2.0944],
#               [1.06, 1.09, 1.09, 0, -2.0944, 2.0944],
#               [1.03, 1.09, 1.03, 0, -2.0944, 2.0944],
#               [1.03, 1.03, 1.09, 0, -2.0944, 2.0944],
#               [1.09, 1.03, 1.03, 0, -2.0944, 2.0944],
#               [1.06, 1.09, 1.09, 0, -1.9, 1.9],
#               [1.06, 1.09, 1.09, 0, -2.2, 2.2],
#               [1.09, 1.09, 1.09, 0, -1.9, 1.9],
#               [1.09, 1.09, 1.09, 0, -2.2, 2.2]]
#
# v_profile_vv = [[1.09, 1.03, 1.03, 0, -2.0944, 2.0944],
#               [0.91, 0.97, 0.97, 0, -2.0944, 2.0944],
#               [1, 1, 1, 0, -2, 2],
#               [1, 1, 1, 0, -2.15, 2.15],
#               [1.09, 1.03, 1.03, 0, -1.9, 1.9],
#               [1.09, 1.03, 1.03, 0, -2.2, 2.2],
#               [0.91, 0.97, 0.97, 0, -1.9, 1.9],
#               [0.91, 0.97, 0.97, 0, -2.2, 2.2]]
#
# v_profile_trip = [[1.11, 1.03, 1.03, 0, -2.0944, 2.0944],
#               [0.87, 0.97, 0.97, 0, -2.0944, 2.0944],
#             [1.03, 1.07, 1.07, 0, -1.9, 1.9],
#             [1.03, 1.07, 1.07, 0, -2.2, 2.2],
#               [0.97, 0.92, 0.92, 0, -1.9, 1.9],
#               [0.97, 0.92, 0.92, 0, -2.2, 2.2]]


der_test.der_input.freq_hz=60
der_test.der_input.p_dc_w=100000
while t < 2500:
    if (t < 5)or(100<t<700)or(800<t<1400)or(1500<t<2100):
        der_test.der_input.v_a = 1*240/1.732
        der_test.der_input.v_b = 1*240/1.732
        der_test.der_input.v_c = 1*240/1.732
    else:
        der_test.der_input.v_a = 1.11 * 240 / 1.732
        der_test.der_input.v_b = 1.11 * 240 / 1.732
        der_test.der_input.v_c = 1.11 * 240 / 1.732
# for p in p_profile:
#     der_test.p_dc_kw = p
    # der_test.p_dc_pu = der_test.p_dc_kw / der_test.NP_P_MAX

# for v in v_profile:
#     der_test.v_a = v*480/1.732
#     der_test.v_b = v*480/1.732
#     der_test.v_c = v*480/1.732
#
# for v in v_profile_trip:
#     der_test.v_a = v[0]*480/1.732
#     der_test.v_b = v[1]*480/1.732
#     der_test.v_c = v[2]*480/1.732
#     der_test.theta_a = v[3]
#     der_test.theta_b = v[4]
#     der_test.theta_c = v[5]

    # if (10<t<=30)or(50<t<=70)or(1500<t<2100):
    #     der_test.v_meas_pu = 1.05
    # else:
    #     der_test.v_meas_pu = 1.00



    # calculate output power each time step
    der_test.run()

    # save result
    t_plot.append(t)
    p_plot.append(der_test.p_limited_w)
    q_plot.append(der_test.q_limited_var)
    pdc_plot.append(der_test.der_input.p_dc_w)
    v_plot.append(der_test.der_input.v_meas_pu)
    stat_plot.append(der_test.der_status)
    debug_plot.append(der_test.enterservicetrip.es_flag)

    # increase t
    t = t + t_s


# plot
fig = plt.figure(figsize=[15,10])
plt.clf()
ax1=plt.subplot(4, 1, 1)
plt.plot(t_plot, v_plot, label = 'Voltage (pu)')
plt.grid()
plt.legend()
plt.subplot(4, 1, 2, sharex=ax1)
plt.plot(t_plot, pdc_plot, label='P_dc (W)')
plt.plot(t_plot, p_plot, label='P_out (W)')
plt.grid()
plt.legend()
plt.subplot(4, 1, 3, sharex=ax1)
plt.plot(t_plot, q_plot, label='Q_out (kvar)')
plt.grid()
plt.legend()
plt.subplot(4, 1, 4, sharex=ax1)
plt.plot(t_plot, stat_plot, label='on/off status')
plt.grid()
plt.legend()
plt.xlabel('Time (s)')
plt.show()