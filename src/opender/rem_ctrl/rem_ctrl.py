from opender import DERCommonFileFormat, DERInputs
# from opender.auxiliary_funcs.cond_delay import ConditionalDelay
import opender
import cmath
import numpy as np
from opender.auxiliary_funcs.low_pass_filter import LowPassFilter
from opender.auxiliary_funcs.ramping import Ramping
from opender.auxiliary_funcs.cond_delay import ConditionalDelay

class RemainingControl:

    def __init__(self, der_file: DERCommonFileFormat, exec_delay, der_input: DERInputs):

        self.der_file = der_file
        self.exec_delay = exec_delay
        self.der_input = der_input

        self._rt_mode = None
        self._rt_mode_v = None
        self._rt_mode_f = None
        self.rt_pass_time_req = False
        self.rt_status = None

        self.rt_time_lv = 0
        self.rt_time_hv = 0
        self.rt_time_hf = 0
        self.rt_time_lf = 0

        self.i_pos_pu = 0
        self.i_neg_pu = 0

        self.i_pos_lpf = LowPassFilter()
        self.i_neg_lpf = LowPassFilter()
        self.i_pos_d_rrl = Ramping()

        self.i_a_pu = 0
        self.i_b_pu = 0
        self.i_c_pu = 0

        self.i_pos_d_ref_pu = 0
        self.i_pos_q_ref_pu = 0
        self.i_neg_ref_pu = 0

        self.i_pos_d_limited_ref_pu = 0
        self.i_pos_q_limited_ref_pu = 0
        self.i_pos_limited_ref_pu = 0
        self.i_neg_limited_ref_pu = 0

        self.i_mag_pu = (0, 0, 0)
        self.i_theta = (0, 0, 0)

        self.p_limited_pu = 0
        self.q_limited_pu = 0

        self.p_out_pu = 0
        self.q_out_pu = 0
        self.p_out_w = 0
        self.q_out_var = 0
        self.p_out_kw = 0
        self.q_out_kvar = 0

        self.v_pos_out_cmd_pu = 0
        self.v_neg_out_cmd_pu = 0

        self.v_pos_out_pu = 0
        self.v_neg_out_pu = 0
        self.v_a_out_pu, self.v_b_out_pu, self.v_c_out_pu = 0, 0, 0
        self.v_out_mag_pu = (0, 0, 0)
        self.v_out_theta = (0, 0, 0)

        self.rt_mc_cond_delay = ConditionalDelay()
        self.rt_cte_cond_delay = ConditionalDelay()

    def determine_rt_mode(self):

        if self.der_input.v_low_pu >= 0.88 and self.der_input.v_high_pu <= 1.1:
            self.rt_mode_v = 'Continuous Operation'
            self.rt_time_lv = 0
            self.rt_time_hv = 0


        if self.der_file.NP_ABNORMAL_OP_CAT == 'CAT_I':
            if 1.1 < self.der_input.v_high_pu:
                self.rt_time_hv = self.rt_time_hv + opender.DER.t_s

                if self.der_input.v_high_pu <= 1.2:
                    self.rt_mode_v = 'Permissive Operation'
                else:
                    self.rt_mode_v = 'Cease to Energize'

                if (self.rt_time_hv <= 1) and (1.1 < self.der_input.v_high_pu <= 1.15) or \
                   (self.rt_time_hv <= 0.5) and (1.15 < self.der_input.v_high_pu <= 1.175) or \
                   (self.rt_time_hv <= 0.2) and (1.175 < self.der_input.v_high_pu <= 1.2):
                    self.rt_pass_time_req = True

            if self.der_input.v_low_pu < 0.88:
                self.rt_time_lv = self.rt_time_lv + opender.DER.t_s

                if 0.7 <= self.der_input.v_low_pu < 0.88:
                    self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 0.7 + 4 * (self.der_input.v_low_pu - 0.7):
                        self.rt_pass_time_req = True

                if 0.5 <= self.der_input.v_low_pu < 0.7:
                    self.rt_mode_v = 'Permissive Operation'
                    if self.rt_time_lv > 0.16:
                        self.rt_pass_time_req = True

                if self.der_input.v_low_pu < 0.5:
                    self.rt_mode_v = 'Cease to Energize'

        if self.der_file.NP_ABNORMAL_OP_CAT == 'CAT_II':

            if 1.1 < self.der_input.v_high_pu:
                self.rt_time_hv = self.rt_time_hv + opender.DER.t_s

                if self.der_input.v_high_pu <= 1.2:
                    self.rt_mode_v = 'Permissive Operation'
                else:
                    self.rt_mode_v = 'Cease to Energize'

                if (self.rt_time_hv <= 1) and (1.1 < self.der_input.v_high_pu <= 1.15) or \
                        (self.rt_time_hv <= 0.5) and (1.15 < self.der_input.v_high_pu <= 1.175) or \
                        (self.rt_time_hv <= 0.2) and (1.15 < self.der_input.v_high_pu <= 1.2):
                    self.rt_pass_time_req = True

            if self.der_input.v_low_pu < 0.88:
                self.rt_time_lv = self.rt_time_lv + opender.DER.t_s

                if 0.65 <= self.der_input.v_low_pu < 0.88:
                    self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 3 + 8.7 * (self.der_input.v_low_pu - 0.65):
                        self.rt_pass_time_req = True

                if 0.45 <= self.der_input.v_low_pu < 0.65:
                    self.rt_mode_v = 'Permissive Operation'
                    if self.rt_time_lv > 0.32:
                        self.rt_pass_time_req = True

                if 0.3 <= self.der_input.v_low_pu < 0.45:
                    self.rt_mode_v = 'Permissive Operation'
                    if self.rt_time_lv > 0.16:
                        self.rt_pass_time_req = True

                if self.der_input.v_low_pu < 0.3:
                    self.rt_mode_v = 'Cease to Energize'


        if self.der_file.NP_ABNORMAL_OP_CAT == 'CAT_III':

            if 1.1 < self.der_input.v_high_pu:
                self.rt_time_hv = self.rt_time_hv + opender.DER.t_s

                if self.der_input.v_high_pu <= 1.2:
                    self.rt_mode_v = 'Momentary Cessation'
                else:
                    self.rt_mode_v = 'Cease to Energize'

                if self.rt_time_hv <= 12:
                    self.rt_pass_time_req = True

            if self.der_input.v_low_pu < 0.88:
                self.rt_time_lv = self.rt_time_lv + opender.DER.t_s

                if 0.7 <= self.der_input.v_low_pu < 0.88:
                    self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 20:
                        self.rt_pass_time_req = True

                if 0.5 <= self.der_input.v_low_pu < 0.7:
                    self.rt_mode_v = 'Mandatory Operation'
                    if self.rt_time_lv > 10:
                        self.rt_pass_time_req = True

                if self.der_input.v_low_pu < 0.5:
                    self.rt_mode_v = 'Momentary Cessation'
                    if self.rt_time_lv > 1:
                        self.rt_pass_time_req = True

        if 58.5 <= self.der_input.freq_hz <= 61.2:
            self.rt_mode_f = 'Continuous Operation'
            self.rt_time_hf = 0
            self.rt_time_lf = 0

        if 61.2 <= self.der_input.freq_hz:
            self.rt_time_hf = self.rt_time_hf + opender.DER.t_s
            if self.der_input.freq_hz <= 61.8:
                self.rt_mode_f = 'Mandatory Operation'
            else:
                self.rt_mode_f = 'Not Defined'

            if self.rt_time_hf > 299:
                self.rt_pass_time_req = True

        if self.der_input.freq_hz <= 58.8:
            self.rt_time_lf = self.rt_time_lf + opender.DER.t_s
            if 57.0 <= self.der_input.freq_hz:
                self.rt_mode_f = 'Mandatory Operation'
            else:
                self.rt_mode_f = 'Not Defined'

            if self.rt_time_lf > 299:
                self.rt_pass_time_req = True


        if self.rt_mode_f == 'Not Defined':
            self.rt_mode = 'Not Defined'
        elif self.rt_mode_v in ['Cease to Energize', 'Permissive Operation', 'Momentary Cessation']:
            self.rt_mode = self.rt_mode_v

        elif self.rt_mode_v == 'Mandatory Operation' or self.rt_mode_f == 'Mandatory Operation':
            self.rt_mode = 'Mandatory Operation'
        else:
            self.rt_mode = 'Continuous Operation'
            self.rt_pass_time_req = False

        if self.rt_mode == 'Continuous Operation':
            self.rt_status = 'Normal Operation'

        if self.rt_mode in ['Mandatory Operation', 'Not Defined']:
            if self.der_file.DVS_MODE_ENABLE:
                self.rt_status = 'Dynamic Voltage Support'
            else:
                self.rt_status = 'Normal Operation'

        if self.rt_mode == 'Permissive Operation':
            pass

        if self.rt_mode == 'Cease to Energize':
            if self.rt_cte_cond_delay.con_del_enable(True, self.der_file.NP_CTE_RESP_T):
                self.rt_status = 'Cease to Energize'
            else:
                pass
        else:
            self.rt_cte_cond_delay.con_del_enable(False, self.der_file.NP_CTE_RESP_T)

        if self.rt_mode == 'Momentary Cessation':
            if self.rt_mc_cond_delay.con_del_enable(True, self.der_file.MC_RESP_T):
                self.rt_status = 'Cease to Energize'
            else:
                pass
        else:
            self.rt_mc_cond_delay.con_del_enable(False, self.der_file.MC_RESP_T)

    def der_rem_operation(self, p_limited_w, q_limited_var):

        self.determine_rt_mode()

        self.p_limited_pu = p_limited_w / self.der_file.NP_VA_MAX
        self.q_limited_pu = q_limited_var / self.der_file.NP_VA_MAX

        self.calculate_i_output(self.p_limited_pu, self.q_limited_pu)

        self.p_out_pu = (self.i_pos_pu * self.der_input.v_pos_pu.conjugate()).real
        self.q_out_pu = -(self.i_pos_pu * self.der_input.v_pos_pu.conjugate()).imag
        self.p_out_w = self.p_out_pu * self.der_file.NP_VA_MAX
        self.q_out_var = self.q_out_pu * self.der_file.NP_VA_MAX
        self.p_out_kw = self.p_out_w * 1e-3
        self.q_out_kvar = self.q_out_var * 1e-3

        return self.p_out_w, self.q_out_var

    def calculate_i_output(self, p_limited_pu, q_limited_pu):
        if self.rt_status == 'Normal Operation':
            self.calculate_i_continuous_op(p_limited_pu, q_limited_pu)

        if self.rt_status == 'Dynamic Voltage Support':
            self.calculate_i_DVS(p_limited_pu, q_limited_pu)

        if self.rt_status == 'Cease to Energize':
            self.calculate_i_block()


        if self.i_pos_d_limited_ref_pu > 0:
            self.i_pos_limited_ref_pu = (self.i_pos_d_rrl.ramp(self.i_pos_d_limited_ref_pu, self.der_file.NP_RT_RAMP_UP_TIME, 0) + self.i_pos_q_limited_ref_pu * 1j) * np.exp(1j * self.der_input.v_angle)
        else:
            self.i_pos_limited_ref_pu = (self.i_pos_d_rrl.ramp(self.i_pos_d_limited_ref_pu, 0, self.der_file.NP_RT_RAMP_UP_TIME) + self.i_pos_q_limited_ref_pu * 1j) * np.exp(1j * self.der_input.v_angle)

        self.i_pos_pu = self.i_pos_lpf.low_pass_filter(self.i_pos_limited_ref_pu, self.der_file.NP_INV_DELAY)
        self.i_neg_pu = self.i_neg_lpf.low_pass_filter(self.i_neg_limited_ref_pu, self.der_file.NP_INV_DELAY)

        self.i_a_pu, self.i_b_pu, self.i_c_pu = self.convert_symm_to_abc(self.i_pos_pu, self.i_neg_pu)

        self.i_mag_pu = (abs(self.i_a_pu), abs(self.i_b_pu), abs(self.i_c_pu))
        self.i_theta = (cmath.phase(self.i_a_pu), cmath.phase(self.i_b_pu), cmath.phase(self.i_c_pu))

    def calculate_i_continuous_op(self, p_limited_pu, q_limited_pu):
        self.i_pos_d_ref_pu = p_limited_pu / abs(self.der_input.v_pos_pu)
        self.i_pos_q_ref_pu = - q_limited_pu / abs(self.der_input.v_pos_pu)
        self.i_neg_ref_pu = 0

        self.i_pos_d_limited_ref_pu, self.i_pos_q_limited_ref_pu, self.i_neg_limited_ref_pu = self.i_limit(self.i_pos_d_ref_pu, self.i_pos_q_ref_pu, self.i_neg_ref_pu, self.der_input.v_pos_pu, self.der_file.NP_CURENT_PU)

    def calculate_i_DVS(self, p_limited_pu, q_limited_pu):
        self.i_pos_d_ref_pu = p_limited_pu / abs(self.der_input.v_pos_pu)
        self.i_pos_q_ref_pu = - q_limited_pu / abs(self.der_input.v_pos_pu) + (
                    abs(self.der_input.v_pos_pu) - 1) * self.der_file.DVS_K
        self.i_neg_ref_pu = self.der_input.v_neg_pu * 1j * self.der_file.DVS_K

        self.i_pos_d_limited_ref_pu, self.i_pos_q_limited_ref_pu, self.i_neg_limited_ref_pu = self.i_limit(self.i_pos_d_ref_pu, self.i_pos_q_ref_pu, self.i_neg_ref_pu, self.der_input.v_pos_pu, self.der_file.NP_CURENT_PU)

    def calculate_i_block(self):
        self.i_pos_limited_ref_pu = -1j * self.der_input.v_pos_pu * self.der_file.NP_AC_V_NOM * \
                                    self.der_file.NP_REACTIVE_SUSCEPTANCE / (
                                            self.der_file.NP_VA_MAX / self.der_file.NP_AC_V_NOM)

        self.i_neg_limited_ref_pu = -1j * self.der_input.v_neg_pu * self.der_file.NP_AC_V_NOM * \
                                    self.der_file.NP_REACTIVE_SUSCEPTANCE / (
                                            self.der_file.NP_VA_MAX / self.der_file.NP_AC_V_NOM)


    def calculate_v_output(self):

        self.v_pos_out_cmd_pu = self.der_input.v_pos_pu + self.i_pos_pu * (self.der_file.NP_RESISTANCE + 1j * self.der_file.NP_INDUCTANCE)
        self.v_neg_out_cmd_pu = self.der_input.v_neg_pu + self.i_neg_pu * (self.der_file.NP_RESISTANCE + 1j * self.der_file.NP_INDUCTANCE)

        self.v_pos_out_pu, self.v_neg_out_pu = self.v_limit(self.v_pos_out_cmd_pu, self.v_neg_out_cmd_pu, self.der_file.NP_V_DC / self.der_file.NP_AC_V_NOM)

        self.v_a_out_pu, self.v_b_out_pu, self.v_c_out_pu = self.convert_symm_to_abc(self.v_pos_out_pu, self.v_neg_out_pu)
        self.v_out_mag_pu = (abs(self.v_a_out_pu), abs(self.v_b_out_pu), abs(self.v_c_out_pu))

        self.v_out_theta = (cmath.phase(self.v_a_out_pu), cmath.phase(self.v_b_out_pu), cmath.phase(self.v_c_out_pu))

    def convert_symm_to_abc(self, pos_pu, neg_pu):
        a_pu = pos_pu + neg_pu
        b_pu = cmath.exp(1j * ((-2 / 3) * cmath.pi)) * pos_pu + cmath.exp(1j * ((2 / 3) * cmath.pi)) * neg_pu
        c_pu = cmath.exp(1j * ((2 / 3) * cmath.pi)) * pos_pu + cmath.exp(1j * ((-2 / 3)) * cmath.pi) * neg_pu #TODO make the exp as a constant to save calculation time
        return a_pu, b_pu, c_pu

    def v_limit(self, pos_pu, neg_pu, max_pu):
        max_abc_pu = max([abs(x) for x in self.convert_symm_to_abc(pos_pu, neg_pu)])
        if max_abc_pu > max_pu:
            pos_out_pu = pos_pu * max_pu / max_abc_pu
            neg_out_pu = neg_pu * max_pu / max_abc_pu
        else:
            pos_out_pu = pos_pu
            neg_out_pu = neg_pu

        return pos_out_pu, neg_out_pu

    def i_limit(self, i_pos_d_pu, i_pos_q_pu, i_neg_pu, v_pos_pu, i_max_pu):
        i_pos_pu = (i_pos_d_pu + 1j * i_pos_q_pu) * np.exp(1j * np.angle(v_pos_pu))
        max_abc_pu = max([abs(x) for x in self.convert_symm_to_abc(i_pos_pu, i_neg_pu)])

        if max_abc_pu > i_max_pu:
            i_pos_out_d_pu = i_pos_d_pu * i_max_pu / max_abc_pu
            i_pos_out_q_pu = i_pos_q_pu * i_max_pu / max_abc_pu
            i_neg_out_pu = i_neg_pu * i_max_pu / max_abc_pu
        else:
            i_pos_out_d_pu = i_pos_d_pu
            i_pos_out_q_pu = i_pos_q_pu
            i_neg_out_pu = i_neg_pu

        # if max_abc_pu > i_max_pu:
        #     tolerance = 1e-5
        #     scale = 1
        #     step = 0.1
        #
        #     while step > tolerance:
        #         while max(self.convert_symm_to_abc(i_pos_pu, i_neg_pu)) > i_max_pu:
        #             scale = scale - step
        #             i_pos_pu = (i_pos_d_pu * scale + 1j * i_pos_q_pu) * np.exp(np.angle(v_pos_pu))
        #             if scale < 0:
        #                 scale = 0
        #                 break
        #         scale = scale + step
        #         step = step / 10
        #
        # else:
        #     pos_out_pu = i_pos_pu
        #     neg_out_pu = i_neg_pu

        return i_pos_out_d_pu, i_pos_out_q_pu, i_neg_out_pu


    @property
    def rt_mode(self):
        return self._rt_mode

    @rt_mode.setter
    def rt_mode(self, rt_mode):
        if rt_mode in ['Continuous Operation', 'Mandatory Operation', 'Cease to Energize',
                         'Permissive Operation', 'Momentary Cessation', 'Not Defined', None]:
            self._rt_mode = rt_mode
        else:
            print('error in ride-through status, code incorrect')

    @property
    def rt_mode_v(self):
        return self._rt_mode_v

    @rt_mode_v.setter
    def rt_mode_v(self, rt_mode_v):
        if rt_mode_v in ['Continuous Operation', 'Mandatory Operation', 'Cease to Energize',
                           'Permissive Operation', 'Momentary Cessation', None]:
            self._rt_mode_v = rt_mode_v
        else:
            print('error in ride-through status, code incorrect')

    @property
    def rt_mode_f(self):
        return self._rt_mode_f

    @rt_mode_f.setter
    def rt_mode_f(self, rt_mode_f):
        if rt_mode_f in ['Continuous Operation', 'Mandatory Operation', 'Not Defined', None]:
            self._rt_mode_f = rt_mode_f
        else:
            print('error in ride-through status, code incorrect')


    def __str__(self):
        return f"i_pos_pu = {self.i_pos_pu:.2f}, i_neg_pu = {self.i_neg_pu:.2f}, i_mag_pu = {self.i_mag_pu}, i_theta = {self.i_theta}"
