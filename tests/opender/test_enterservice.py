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

input_list = [  #ES_DELAY, ES_RAMP_RATE, ES_RANDOMIZED_DELAY, ES_V_HIGH, ES_V_LOW, ES_F_HIGH, ES_F_LOW, initial voltage, final voltage, initial freq, final freq
    (300,300,0,1.05,0.917,60.1,59.5,0.897,0.937,60.0,60.0),
    (0, 0, 300, 1.05,0.917,60.1,59.5,1.0,1.0,59.48,59.52),
    (600,1000,0,1.06,0.95,61.0,59.9,1.08,1.04,60.0,60.0),
    (0,0,1000,1.06,0.95,61.0,59.9,1.0,1.0,61.02,60.98),
    (0,1,0,1.05,0.88,60.1,59.0,0.86,0.9,60.0,60.0),
    (0,0,1,1.05,0.88,60.1,59.0,1.0,1.0,58.98,59.92)

]
t_s_list = [1, 10,100,1000000]

class TestEnterService562:
    #IEEE 1547.1-2020, section 5.6.2: type test
    @pytest.fixture(autouse=True)
    def _request(self, si_obj_creation):
        self.si_obj = si_obj_creation


    @pytest.mark.parametrize("t_s", t_s_list)
    @pytest.mark.parametrize("input_list", input_list)
    def test_enter_service_5_6_2(self, t_s, input_list:tuple):
        der.DER.t_s = t_s
        self.si_obj.der_file.ES_DELAY = input_list[0]
        self.si_obj.der_file.ES_RAMP_RATE = input_list[1]
        self.si_obj.der_file.ES_RANDOMIZED_DELAY = input_list[2]
        self.si_obj.der_file.ES_V_HIGH = input_list[3]
        self.si_obj.der_file.ES_V_LOW = input_list[4]
        self.si_obj.der_file.ES_F_HIGH = input_list[5]
        self.si_obj.der_file.ES_F_LOW = input_list[6]
        self.si_obj.der_file.PF_MODE_ENABLE = False #disabled so that test case 3 does not curtail power
        self.si_obj.der_status=False
        self.si_obj.der_file.STATUS_INIT=False
        self.si_obj.der_file.ES_PERMIT_SERVICE=False
        self.si_obj.reinitialize()
        init_v=input_list[7]
        final_v=input_list[8]
        init_f=input_list[9]
        final_f=input_list[10]

        v_pu=init_v
        p_dc=self.si_obj.der_file.NP_P_MAX*1.1

        t1=0
        period1=max(60,2*self.si_obj.der_file.ES_DELAY+self.si_obj.der_file.ES_RANDOMIZED_DELAY)
        self.si_obj.update_der_input(v_pu=v_pu, p_dc_kw=p_dc)
        self.si_obj.der_input.freq_hz = init_f

        while t1+t_s<=period1:
            self.si_obj.run()
            assert False == self.si_obj.der_status, 'enter service stage e) fail'
            t1=t1+t_s

        t2=0
        period2=max(60,2*self.si_obj.der_file.ES_DELAY+self.si_obj.der_file.ES_RANDOMIZED_DELAY)
        self.si_obj.der_file.ES_PERMIT_SERVICE = True
        self.si_obj.update_der_input(v_pu=v_pu)
        while t2+t_s<=period2:
            self.si_obj.run()
            assert False == self.si_obj.der_status, f'enter service stage h) fail, at t={t2}'
            t2=t2+t_s

        t3=0
        period3=0.25*self.si_obj.der_file.ES_DELAY
        v_pu = final_v
        self.si_obj.update_der_input(v_pu=v_pu)
        self.si_obj.der_input.freq_hz=final_f
        while t3+t_s <= period3:
            self.si_obj.run()
            assert False == self.si_obj.der_status, f'enter service stage i) fail, at t={t3}'
            t3=t3+t_s

        t4=0
        v_pu = init_v
        self.si_obj.update_der_input(v_pu=v_pu)
        self.si_obj.der_input.freq_hz=init_f
        self.si_obj.run()

        v_pu = final_v
        self.si_obj.update_der_input(v_pu=v_pu)
        self.si_obj.der_input.freq_hz=final_f

        while self.si_obj.der_status == False:
            p_prev = self.si_obj.p_out_kw
            self.si_obj.run()
            t4=t4+t_s

        assert t4 >= self.si_obj.der_file.ES_DELAY, f'enter service stage j) fail: enter service too soon, at t={t4}'

        p = self.si_obj.p_out_kw
        while self.si_obj.p_out_kw < 1.e-5 or abs(p-p_prev) > 1.e-5: # waiting or ramping
            p_prev = p
            self.si_obj.run()
            p = self.si_obj.p_out_kw
            if self.si_obj.der_file.ES_RAMP_RATE>0:
                assert abs(p-p_prev) <= t_s*(self.si_obj.der_file.NP_P_MAX/self.si_obj.der_file.ES_RAMP_RATE)+1.e-4, 'enter service stage j) fail: ramp rate too fast'
            t4=t4+t_s


        assert t4>0.985*(self.si_obj.der_file.ES_DELAY+self.si_obj.der_file.ES_RAMP_RATE), f'enter service stage j) fail: ramp time {t4} is too fast than the ramp time'

        self.si_obj.der_file.ES_PERMIT_SERVICE=False
        self.si_obj.run()

        if self.si_obj.der_file.ES_DELAY>0:
            t5=0
            self.si_obj.der_file.ES_PERMIT_SERVICE=True
            self.si_obj.run()
            while t5+t_s <= 5:
                self.si_obj.run()
                assert False == self.si_obj.der_status, 'enter service stage l) fail'
                t5=t5+t_s