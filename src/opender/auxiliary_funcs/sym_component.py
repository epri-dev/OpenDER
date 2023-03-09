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

import cmath
from typing import Tuple

alpha = cmath.exp(1j * ((2 / 3) * cmath.pi))
alpha2 = cmath.exp(1j * ((-2 / 3) * cmath.pi))


def convert_symm_to_abc(pos_pu:complex, neg_pu:complex, zero_pu:complex=0) -> Tuple[complex, complex, complex]:
    a_pu = pos_pu + neg_pu + zero_pu
    b_pu = alpha2 * pos_pu + alpha * neg_pu + zero_pu
    c_pu = alpha * pos_pu + alpha2 * neg_pu + zero_pu
    return a_pu, b_pu, c_pu