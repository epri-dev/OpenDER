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

import cmath
from typing import Tuple

alpha = cmath.exp(1j * ((2 / 3) * cmath.pi))
alpha2 = cmath.exp(1j * ((-2 / 3) * cmath.pi))


def convert_symm_to_abc(pos:complex, neg:complex, zero:complex=0) -> Tuple[complex, complex, complex]:
    """
    |  Convert symmetrical components (positive, negative, zero sequence) to phase components (abc axis)
    :param pos: Positive sequence component
    :param neg: Negative sequence component
    :param zero: Zero sequence component

    Output:
    :param a: Phase A component
    :param b: Phase B component
    :param c: Phase C component
    """
    a = pos + neg + zero
    b = alpha2 * pos + alpha * neg + zero
    c = alpha * pos + alpha2 * neg + zero
    return a, b, c