from opender import DERCommonFileFormat, DERInputs
# from opender.auxiliary_funcs.cond_delay import ConditionalDelay
import opender
import cmath
from opender.auxiliary_funcs.low_pass_filter import LowPassFilter

class RemainingControl:

    def __init__(self, der_file: DERCommonFileFormat, exec_delay, der_input: DERInputs):

        self.der_file = der_file
        self.exec_delay = exec_delay
        self.der_input = der_input

        self._rt_status = None
        self.rt_pass_time_req = False

        self.rt_time_lv = 0
        self.rt_time_hv = 0
        self.rt_time_of = 0
        self.rt_time_uf = 0

        self.i_pos_pu = 0
        self.i_neg_pu = 0

        self.i_pos_lpf = LowPassFilter()
        self.i_neg_lpf = LowPassFilter()

        self.i_a_pu = 0
        self.i_b_pu = 0
        self.i_c_pu = 0

        self.i_mag_pu = (0,0,0)
        self.i_theta = (0,0,0)

    def determine_rt_status(self):

        if (self.der_input.v_low_pu >= 0.88 and self.der_input.v_high_pu <= 1.1) and \
                (58.5 <= self.der_input.freq_hz <= 61.2):
            self.rt_status = 'Continuous Operation'
            self.rt_last_status = 'Continuous Operation'
            self.rt_time_lv = 0
            self.rt_time_hv = 0
            self.rt_time_of = 0
            self.rt_time_uf = 0
            self.rt_pass_time_req = False

        if 61.2 <= self.der_input.freq_hz <= 61.8:
            self.rt_time_of = self.rt_time_of + opender.DER.t_s
            if self.rt_time_of <= 299:
                self.rt_status = 'Mandatory Operation'
            else:
                self.rt_pass_time_req = True

        if 57.0 <= self.der_input.freq_hz <= 58.8:
            self.rt_time_uf = self.rt_time_uf + opender.DER.t_s
            if self.rt_time_uf <= 299:
                self.rt_status = 'Mandatory Operation'
            else:
                self.rt_pass_time_req = True

        if self.der_input.freq_hz > 62.0 or self.der_input.freq_hz < 57.0:
            self.rt_status = 'Not Defined'

        if self.der_file.NP_ABNORMAL_OP_CAT == 'CAT_I':
            if 1.1 < self.der_input.v_high_pu:
                self.rt_time_hv = self.rt_time_hv + opender.DER.t_s

                if self.der_input.v_high_pu <= 1.2:
                    self.rt_status = 'Permissive Operation'
                else:
                    self.rt_status = 'Not Defined'

                if (self.rt_time_hv <= 1) and (1.1 < self.der_input.v_high_pu <= 1.15) or \
                   (self.rt_time_hv <= 0.5) and (1.15 < self.der_input.v_high_pu <= 1.175) or \
                   (self.rt_time_hv <= 0.2) and (1.15 < self.der_input.v_high_pu <= 1.2):
                    self.rt_pass_time_req = True

            if self.der_input.v_low_pu < 0.88:
                self.rt_time_lv = self.rt_time_lv + opender.DER.t_s

                if 0.7 <= self.der_input.v_low_pu < 0.88:
                    self.rt_status = 'Mandatory Operation'
                    if self.rt_time_lv > 0.7 + 4 * (self.der_input.v_low_pu - 0.7):
                        self.rt_pass_time_req = True

                if 0.5 <= self.der_input.v_low_pu < 0.7:
                    self.rt_status = 'Permissive Operation'
                    if self.rt_time_lv > 0.16:
                        self.rt_pass_time_req = True

                if self.der_input.v_low_pu < 0.5:
                    self.rt_status = 'Not Defined'

        if self.der_file.NP_ABNORMAL_OP_CAT == 'CAT_II':

            if 1.1 < self.der_input.v_high_pu:
                self.rt_time_hv = self.rt_time_hv + opender.DER.t_s

                if self.der_input.v_high_pu <= 1.2:
                    self.rt_status = 'Permissive Operation'
                else:
                    self.rt_status = 'Not Defined'

                if (self.rt_time_hv <= 1) and (1.1 < self.der_input.v_high_pu <= 1.15) or \
                        (self.rt_time_hv <= 0.5) and (1.15 < self.der_input.v_high_pu <= 1.175) or \
                        (self.rt_time_hv <= 0.2) and (1.15 < self.der_input.v_high_pu <= 1.2):
                    self.rt_pass_time_req = True

            if self.der_input.v_low_pu < 0.88:
                self.rt_time_lv = self.rt_time_lv + opender.DER.t_s

                if 0.65 <= self.der_input.v_low_pu < 0.88:
                    self.rt_status = 'Mandatory Operation'
                    if self.rt_time_lv > 3 + 8.7 * (self.der_input.v_low_pu - 0.65):
                        self.rt_pass_time_req = True

                if 0.45 <= self.der_input.v_low_pu < 0.65:
                    self.rt_status = 'Permissive Operation'
                    if self.rt_time_lv > 0.32:
                        self.rt_pass_time_req = True

                if 0.3 <= self.der_input.v_low_pu < 0.45:
                    self.rt_status = 'Permissive Operation'
                    if self.rt_time_lv > 0.16:
                        self.rt_pass_time_req = True

                if self.der_input.v_low_pu < 0.3:
                    self.rt_status = 'Not Defined'


        if self.der_file.NP_ABNORMAL_OP_CAT == 'CAT_III':

            if 1.1 < self.der_input.v_high_pu:
                self.rt_time_hv = self.rt_time_hv + opender.DER.t_s

                if self.der_input.v_high_pu <= 1.2:
                    self.rt_status = 'Momentary Cessation'
                else:
                    self.rt_status = 'Not Defined'

                if (self.rt_time_hv <= 12):
                    self.rt_pass_time_req = True

            if self.der_input.v_low_pu < 0.88:
                self.rt_time_lv = self.rt_time_lv + opender.DER.t_s

                if 0.7 <= self.der_input.v_low_pu < 0.88:
                    self.rt_status = 'Mandatory Operation'
                    if self.rt_time_lv > 20:
                        self.rt_pass_time_req = True

                if 0.5 <= self.der_input.v_low_pu < 0.7:
                    self.rt_status = 'Mandatory Operation'
                    if self.rt_time_lv > 10:
                        self.rt_pass_time_req = True

                if self.der_input.v_low_pu < 0.5:
                    self.rt_status = 'Momentary Cessation'
                    if self.rt_time_lv > 1:
                        self.rt_pass_time_req = True


        if self.rt_status is None:
            print('error in code')
            #TODO debug



    def der_rem_operation(self, p_limited_w, q_limited_var):

        self.determine_rt_status()

        self.p_limited_pu = p_limited_w / self.der_file.NP_VA_MAX
        self.q_limited_pu = q_limited_var / self.der_file.NP_VA_MAX

        self.calculate_i_output(self.p_limited_pu, self.q_limited_pu)

        self.p_out_pu = (self.i_pos_pu * self.der_input.v_pos_pu).real
        self.q_out_pu = -(self.i_pos_pu * self.der_input.v_pos_pu).imag
        self.p_out_w = self.p_out_pu * self.der_file.NP_VA_MAX
        self.q_out_var = self.q_out_pu * self.der_file.NP_VA_MAX
        self.p_out_kw = self.p_out_w * 1e-3
        self.q_out_kvar = self.q_out_var * 1e-3

        return self.p_out_w, self.q_out_var

    def calculate_i_output(self, p_limited_pu, q_limited_pu):
        if self.rt_status in ['Continuous Operation', 'Mandatory Operation',
                              'Permissive Operation', 'Not Defined']:
            self.i_pos_ref_pu = ((p_limited_pu + 1j * q_limited_pu) / self.der_input.v_pos_pu).conjugate()
            self.i_neg_ref_pu = self.der_input.v_neg_pu * 1j / 1

        if self.rt_status == 'Momentary Cessation':
            self.i_pos_ref_pu = 1j * self.der_input.v_pos_pu * self.der_file.NP_AC_V_NOM * \
                      self.der_file.NP_REACTIVE_SUSCEPTANCE / (self.der_file.NP_VA_MAX / self.der_file.NP_AC_V_NOM)

            self.i_neg_ref_pu = 1j * self.der_input.v_neg_pu * self.der_file.NP_AC_V_NOM * \
                      self.der_file.NP_REACTIVE_SUSCEPTANCE / (self.der_file.NP_VA_MAX / self.der_file.NP_AC_V_NOM)

        self.i_pos_limited_ref_pu, self.i_neg_limited_ref_pu = self.limit_pos_neg(self.i_pos_ref_pu, self.i_neg_ref_pu, self.der_file.NP_CURENT_PU)

        self.i_pos_pu = self.i_pos_lpf.low_pass_filter(self.i_pos_limited_ref_pu, self.der_file.NP_CTRL_LOOP_DELAY)
        self.i_neg_pu = self.i_neg_lpf.low_pass_filter(self.i_neg_limited_ref_pu, self.der_file.NP_CTRL_LOOP_DELAY)

        self.i_a_pu, self.i_b_pu, self.i_c_pu = self.convert_symm_to_abc(self.i_pos_pu, self.i_neg_pu)

        self.i_mag_pu = (abs(self.i_a_pu), abs(self.i_b_pu), abs(self.i_c_pu))
        self.i_theta = (cmath.phase(self.i_a_pu)+ self.der_input.theta_a, cmath.phase(self.i_b_pu) + self.der_input.theta_a, cmath.phase(self.i_c_pu)+ self.der_input.theta_a)

    def calculate_v_output(self):

        self.v_pos_out_cmd_pu = self.der_input.v_pos_pu + self.i_pos_pu * (self.der_file.NP_RESISTANCE + 1j * self.der_file.NP_INDUCTANCE)
        self.v_neg_out_cmd_pu = self.der_input.v_neg_pu + self.i_neg_pu * (self.der_file.NP_RESISTANCE + 1j * self.der_file.NP_INDUCTANCE)

        self.v_pos_out_pu, self.v_neg_out_pu = self.limit_pos_neg(self.v_pos_out_cmd_pu, self.v_pos_out_cmd_pu, self.der_file.NP_V_DC / self.der_file.NP_AC_V_NOM)

        self.v_a_out_pu, self.v_b_out_pu, self.v_c_out_pu = self.convert_symm_to_abc(self.v_pos_out_pu, self.v_neg_out_pu)
        self.v_out_mag_pu = (abs(self.v_a_out_pu), abs(self.v_b_out_pu), abs(self.v_c_out_pu))
        self.v_out_theta = (cmath.phase(self.v_a_out_pu)+ self.der_input.theta_a, cmath.phase(self.v_b_out_pu)+ self.der_input.theta_a, cmath.phase(self.v_c_out_pu)+ self.der_input.theta_a)
        # self.v_out_theta = (cmath.phase(self.v_a_out_pu), cmath.phase(self.v_b_out_pu), cmath.phase(self.v_c_out_pu))


    def convert_symm_to_abc(self, pos_pu, neg_pu):
        a_pu = pos_pu + neg_pu
        b_pu = cmath.exp(1j * ((-2 / 3) * cmath.pi)) * pos_pu + cmath.exp(1j * ((2 / 3) * cmath.pi)) * neg_pu
        c_pu = cmath.exp(1j * ((2 / 3) * cmath.pi)) * pos_pu + cmath.exp(1j * ((-2 / 3)) * cmath.pi) * neg_pu #TODO make the exp as a constant to save calculation time
        return a_pu, b_pu, c_pu

    def limit_pos_neg(self, pos_pu, neg_pu, max_pu):
        max_abc_pu = max(self.convert_symm_to_abc(pos_pu, neg_pu))
        if max_abc_pu > max_pu:
            pos_out_pu = pos_pu * max_pu / max_abc_pu
            neg_out_pu = neg_pu * max_pu / max_abc_pu
        else:
            pos_out_pu = pos_pu
            neg_out_pu = neg_pu

        return pos_out_pu, neg_out_pu

    @property
    def rt_status(self):
        return self._rt_status

    @rt_status.setter
    def rt_status(self, rt_status):
        if rt_status in ['Continuous Operation', 'Mandatory Operation',
                         'Permissive Operation', 'Momentary Cessation', 'Not Defined', None]:
            self._rt_status = rt_status
        else:
            print('error in ride-through status, code incorrect')


    def __str__(self):
        return f"i_pos_pu = {self.i_pos_pu:.2f}, i_neg_pu = {self.i_neg_pu:.2f}, i_mag_pu = {self.i_mag_pu}, i_theta = {self.i_theta}"
