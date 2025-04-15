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
"""
@author: Jithendar Anandan
@email: janandan@epri.com
"""


class FlipFlop:
    """
    |  Flipflop logic
    |  EPRI Report Reference: Section 3.12.5 in Report #3002030962: IEEE 1547-2018 OpenDER Model
    """
    def __init__(self, ff_init):
        self.ff_out_prev = ff_init
        
    def flipflop(self, ff_set:int, ff_reset:int):
        """
        Flipflop logic

        Input
        :param ff_set: Set input of flipflop logic
        :param ff_reset: Reset input of flipflop logic

        Output:
        :param ff_out: flipflop logic output
        """

        # Eq. 3.12.5-2 Flipflop logic
        if(ff_set == 0 and ff_reset == 0):
            ff_out = self.ff_out_prev
        elif(ff_set == 1 and ff_reset == 0):
            ff_out = 1
        elif(ff_set == 0 and ff_reset == 1):
            ff_out = 0
        elif(ff_set == 1 and ff_reset == 1):
            ff_out = self.ff_out_prev
            
        self.ff_out_prev = ff_out
            
        return ff_out
        
