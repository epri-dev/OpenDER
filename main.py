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


der_test.der_file.QV_MODE_ENABLE = True
der_test.der_file.NP_ABNORMAL_OP_CAT = 'Cat_II'


der_test.update_der_input(f=60, p_dc_pu=1)
while t < 2500:
    if (t < 5)or(100<t<800)or(900<t<1600)or(1700<t<2400):
        der_test.update_der_input(v_pu=1)
    else:
        der_test.update_der_input(v_pu=1.11)


    # calculate output power each time step
    der_test.run()

    # save result
    t_plot.append(t)
    p_plot.append(der_test.p_out_pu)
    q_plot.append(der_test.q_out_pu)
    pdc_plot.append(der_test.der_input.p_avl_pu)
    v_plot.append(der_test.der_input.v_meas_pu)
    stat_plot.append(der_test.der_status)

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
plt.plot(t_plot, pdc_plot, label='P_dc (pu)')
plt.plot(t_plot, p_plot, label='P_out (pu)')
plt.grid()
plt.legend()
plt.subplot(4, 1, 3, sharex=ax1)
plt.plot(t_plot, q_plot, label='Q_out (pu)')
plt.grid()
plt.legend()
plt.subplot(4, 1, 4, sharex=ax1)
plt.plot(t_plot, stat_plot, label='der status')
plt.grid()
plt.legend()
plt.xlabel('Time (s)')
plt.show()