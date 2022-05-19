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
# import matplotlib.pyplot as plt
input_list = [
    # (0.036, 0.05, 5), # comment out due to taking too long, should comment back if needed to test
    (0.017, 0.03, 1),
    (0.017, 0.02, 0.2)
]

class TestFrequencyDroop515:
    #IEEE 1547.1-2020, section 5.6.2: type test
    @pytest.fixture(autouse=True)
    def _request(self, si_obj_creation):
        self.si_obj = si_obj_creation

    @pytest.mark.parametrize("input_list", input_list)
    def test_frequency_droop_5_15_1(self, input_list:tuple):
        t_s = der.DER.t_s = 0.005

        self.si_obj.der_file.PF_DBOF = input_list[0]
        self.si_obj.der_file.PF_DBUF = input_list[0]
        self.si_obj.der_file.PF_KOF = input_list[1]
        self.si_obj.der_file.PF_KUF = input_list[1]
        self.si_obj.der_file.PF_OLRT = input_list[2]

        v_pu=1
        p_dc=self.si_obj.der_file.NP_P_MAX*1.1

        freq_list = (60,    # c)
                     60+input_list[0],      # h), i) (?)
                     60+input_list[0]+input_list[1]*60*0.05,    # j)
                     61.2,  # k)
                     61.2 - input_list[1]*60*0.05, # l)
                     60 + input_list[0],  # m), n) (?)
                     60)

        self.si_obj.update_der_input(v_pu=1, p_dc_pu=1.1, f=60)
        self.si_obj.run()

        for pdc in [1.1, 0.66, 0.2]:
            self.si_obj.update_der_input(p_dc_pu=pdc)

            for i,freq in enumerate(freq_list):
                self.si_obj.update_der_input(f=freq)
                P_init = self.si_obj.p_out_kw
                t = 0
                P_array = []
                while t+t_s <= input_list[2]:
                    self.si_obj.run()
                    t=t+t_s
                    P_array.append(self.si_obj.p_out_kw)
                P_olrt = self.si_obj.p_out_kw

                while t+t_s <= 4 * input_list[2]:
                    self.si_obj.run()
                    t=t+t_s
                    P_array.append(self.si_obj.p_out_kw)
                P_final = self.si_obj.p_out_kw
                # plt.plot(P_array)
                # plt.show()
                assert abs(P_olrt - 0.9*(P_final-P_init)-P_init)<self.si_obj.der_file.NP_P_MAX*0.05, f"Freq-droop OLRT error when in step{i}, f={freq}"




        freq_list =  (60 - input_list[0],  # g), h) (?)
                     60 - input_list[0] - input_list[1] * 60 * 0.05,  # i)
                     58.8,  # j)
                     58.8 + input_list[1] * 60 * 0.05,  # k)
                     60 - input_list[0],  # l), m) (?)
                     60     # n)
                     )
        self.si_obj.update_der_input(v_pu=1, p_dc_pu=1.1, f=60)
        self.si_obj.der_file.AP_LIMIT = 0.5
        self.si_obj.der_file.AP_LIMIT_ENABLE = True
        self.si_obj.reinitialize()
        self.si_obj.run()

        for i,freq in enumerate(freq_list):
            self.si_obj.update_der_input(f=freq)
            P_init = self.si_obj.p_out_kw
            t = 0
            P_array = []
            while t+t_s <= input_list[2]:
                self.si_obj.run()
                t=t+t_s
                P_array.append(self.si_obj.p_out_kw)
            P_olrt = self.si_obj.p_out_kw

            while t+t_s <= 4 * input_list[2]:
                self.si_obj.run()
                t=t+t_s
                P_array.append(self.si_obj.p_out_kw)
            P_final = self.si_obj.p_out_kw
            # plt.plot(P_array)
            # plt.show()
            assert abs(P_olrt - 0.9*(P_final-P_init)-P_init)<self.si_obj.der_file.NP_P_MAX*0.05, f"Freq-droop OLRT error when in step{i}, f={freq}"