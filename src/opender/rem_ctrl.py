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


def RemainingControl(p_limited_kw, q_limited_kvar):
    """
    |  Remaining DER Control and Circuit Equivalents
    |  EPRI Report Reference: Section 3.10 in Report #3002021694: IEEE 1547-2018 DER Model
    """
    # DER faster dynamics, such as momentary cessation, dynamic voltage support, will be released in V2.0
    return p_limited_kw, q_limited_kvar