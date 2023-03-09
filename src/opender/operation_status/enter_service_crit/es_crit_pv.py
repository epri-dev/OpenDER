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


from opender.operation_status.enter_service_crit.es_crit import EnterServiceCrit


class EnterServiceCritPV(EnterServiceCrit):
    """
    Enter Service criteria for PV DER
    EPRI Report Reference: Section 3.5.2 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """
    def __init__(self, der_obj):
        super(EnterServiceCritPV, self).__init__(der_obj)
        self.es_p_crit = None

    def es_other_crit(self):
        """
        Override other enter service criteria in the parent class.

        Variable used in this function:
        :param p_avl_pu: DER available DC power in per unit considering efficiency
        :param NP_P_MIN_PU: DER minimum active power output
        """

        # Eq 3.5.2-1, PV DER enters service when the available power is greater than the minimum power output
        self.es_p_crit = self.der_input.p_avl_pu >= self.der_file.NP_P_MIN_PU
        return self.es_p_crit

