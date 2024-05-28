"""
Copyright © 2023 Electric Power Research Institute, Inc. All rights reserved.

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
import opender

input_list = [  #Category, V, MC_ENABLE, MC_LVRT_V1, MC_HVRT_V1, expected status
    ('CAT_I', 1.11, False, 0.5, 1.1, 'Permissive Operation'),
    ('CAT_I', 1.21, False, 0.5, 1.1, 'Cease to Energize'),
    ('CAT_I', 0.8, False, 0.5, 1.1, 'Mandatory Operation'),
    ('CAT_I', 0.6, False, 0.5, 1.1, 'Permissive Operation'),
    ('CAT_I', 0.2, False, 0.5, 1.1, 'Cease to Energize'),
    ('CAT_II', 1.11, False, 0.5, 1.1, 'Permissive Operation'),
    ('CAT_II', 1.21, False, 0.5, 1.1, 'Cease to Energize'),
    ('CAT_II', 0.8, False, 0.5, 1.1, 'Mandatory Operation'),
    ('CAT_II', 0.6, False, 0.5, 1.1, 'Permissive Operation'),
    ('CAT_II', 0.4, False, 0.5, 1.1, 'Permissive Operation'),
    ('CAT_II', 0.2, False, 0.5, 1.1, 'Cease to Energize'),
    ('CAT_II', 1.11, True, 0.5, 1.1, 'Momentary Cessation'),
    ('CAT_II', 0.8, True, 0.5, 1.1, 'Mandatory Operation'),
    ('CAT_II', 0.6, True, 0.5, 1.1, 'Permissive Operation'),
    ('CAT_II', 0.4, True, 0.5, 1.1, 'Momentary Cessation'),
    ('CAT_II', 0.2, True, 0.5, 1.1, 'Momentary Cessation'),
    ('CAT_III', 1.11, True, 0.5, 1.1, 'Momentary Cessation'),
    ('CAT_III', 0.8, True, 0.5, 1.1, 'Mandatory Operation'),
    ('CAT_III', 0.4, True, 0.5, 1.1, 'Momentary Cessation'),
    ('CAT_III', 0.2, True, 0.1, 1.1, 'Mandatory Operation'),
    ('CAT_III', 1.11, True, 0.1, 1.15, 'Mandatory Operation'),
    ('CAT_III', 1.11, False, 0.5, 1.1, 'Mandatory Operation'),
    ('CAT_III', 0.8, False, 0.5, 1.1, 'Mandatory Operation'),
    ('CAT_III', 0.4, False, 0.5, 1.1, 'Mandatory Operation'),

    ('CAT_III', (1.11, 0.8, 0.8), True, 0.5, 1.1, 'Momentary Cessation'),
    ('CAT_III', (1.11, 0.8, 0.8), False, 0.5, 1.1, 'Mandatory Operation'),
    ('CAT_II', (1.11, 0.8, 0.8), True, 0.5, 1.1, 'Momentary Cessation'),
    ('CAT_II', (1.11, 0.8, 0.8), False, 0.5, 1.1, 'Permissive Operation'),
    ('CAT_II', (1.21, 0.8, 0.8), False, 0.5, 1.1, 'Cease to Energize'),
]


class TestRT:

    @pytest.mark.parametrize("Category, v_pu, MC_ENABLE, MC_LVRT_V1, MC_HVRT_V1, status", input_list,
                             ids=[f"ride-through Category={i[0]}, V={i[1]}, MC_ENABLE={i[2]}"
                                  for i in input_list])
    def test_rt(self, Category, v_pu, MC_ENABLE, MC_LVRT_V1, MC_HVRT_V1, status):
        opender.DER.t_s = 0.01
        self.der_obj = opender.DER(NP_ABNORMAL_OP_CAT=Category,
                                   MC_ENABLE = MC_ENABLE,
                                   MC_LVRT_V1 = MC_LVRT_V1,
                                   MC_HVRT_V1 = MC_HVRT_V1)

        self.der_obj.update_der_input(v_pu=1, p_dc_pu=1)
        self.der_obj.run()
        self.der_obj.update_der_input(v_pu=v_pu, p_dc_pu=1)
        self.der_obj.run()

        assert self.der_obj.der_status == status