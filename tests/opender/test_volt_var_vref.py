"""
Copyright © 2022 Electric Power Research Institute, Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
· Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
· Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
· Neither the name of the EPRI nor the names of its contributors may be used
  to endorse or promote products derived from this software without specific
  prior written permission.
"""

import pytest
from opender import der
from opender import common_file_format
import pathlib
import os
# import matplotlib.pyplot as plt

input_list = [
    (300,1,"DER_CAT_A.csv"),
    (5000,10,"DER_CAT_A.csv"),
    (300, 1, "DER_CAT_B.csv"),
    (5000, 10, "DER_CAT_B.csv"),
]
class TestVoltVar5145:
    #IEEE 1547.1-2020, section 5.6.2: type test
    @pytest.fixture(autouse=True)
    def _request(self, si_obj_creation):
        pass


    @pytest.mark.parametrize("input_list", input_list)
    def test_volt_var_5_14_5(self, input_list:tuple):
        # self.si_obj = si_obj_creation

        script_path = pathlib.Path(os.path.dirname(__file__))

        as_file_path = script_path.joinpath(input_list[2])
        # print(as_file_path)
        # print(model_file_path)

        file_ss_obj = common_file_format.DERCommonFileFormat(as_file_path)

        self.si_obj = der.DER(file_ss_obj)

        t_s = der.DER.t_s = input_list[1]

        self.si_obj.der_file.QV_MODE_ENABLE = True
        self.si_obj.der_file.QV_VREF_AUTO_MODE = True
        self.si_obj.der_file.QV_VREF_TIME = input_list[0]
        self.si_obj.update_der_input(p_dc_pu=1.1,v_pu=1) #step d)
        self.si_obj.der_input.freq_hz = 60


        t = 0
        # q_array = []
        self.si_obj.run()
        v1=(self.si_obj.der_file.QV_CURVE_V3+self.si_obj.der_file.QV_CURVE_V4)/2
        self.si_obj.update_der_input(v_pu=v1) #step h)
        while t + t_s <= input_list[0]:
            self.si_obj.run()
            # q_array.append(self.si_obj.q_out_kvar)
            t=t+t_s
        # print(q_array)
        # plt.plot(q_array)
        # plt.show()
        assert self.si_obj.q_out_kvar > 0.1 * self.si_obj.der_file.NP_VA_MAX * self.si_obj.der_file.QV_CURVE_Q4

        while t + t_s <= 4*input_list[0]:
            self.si_obj.run()
            t=t+t_s


        t = 0
        q_array = []
        self.si_obj.run()
        v2=(self.si_obj.der_file.QV_CURVE_V1+self.si_obj.der_file.QV_CURVE_V2)/2
        self.si_obj.update_der_input(v_pu=v2) #step i)
        while t + t_s <= input_list[0]:
            self.si_obj.run()
            # q_array.append(self.si_obj.q_out_kvar)
            t=t+t_s
        # print(q_array)
        assert self.si_obj.q_out_kvar < 0.1 * self.si_obj.der_file.NP_VA_MAX * self.si_obj.der_file.QV_CURVE_Q1 * 2 # The criterion here seems to be unfair for decreasing voltage. Relaxed

