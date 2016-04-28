"""Trial Balance covnersion
Holding all conversion from one chart of account to another."""

import pandas as pd

from .utils import p
from .journal_entry import TrialBalance

class TrialBalanceConversion():

    def __init__(self, coa_to):
        self.coa_to = coa_to
        self.conversion = {}



    def add_conversion(self, conversion, coa_from, coa_to):
        """Check that it is complete and add the conversion. All of the input COA must be converted to all of
        the output coa.  Any part that is not used must be netted off"""
        set_nc_from = set()
        set_nc_to = set()
        for nc_to, nc_from_list in conversion.items():
            set_nc_to = set_nc_to | set([nc_to])
            set_nc_from = set_nc_from | set(nc_from_list)

        from_nc_not_accounted_for = set_nc_from ^ coa_from.nc_set()
        if from_nc_not_accounted_for != set():
            print("From nominal codes mismatch {}".format(from_nc_not_accounted_for))
            f1 = list(set_nc_from)
            f1.sort()
            print("Conversion set from {}".format(f1))
            f2 = list(coa_from.nc_set())
            f2.sort()
            print("Chart of acounts set from {}".format(f2))
        assert from_nc_not_accounted_for == set(),\
            'Make sure that in conversion all codes from are in the chart of accounts for {}'.format(coa_from.name)
        to_nc_not_accounted_for = set_nc_to ^ coa_to.nc_set()
        if to_nc_not_accounted_for != set():
            print("From nominal codes mismatch {}".format(to_nc_not_accounted_for))
            t1 = list(set_nc_from)
            t1.sort()
            print("Conversion set to {}".format(t1))
            t2 = list(coa_to.nc_set())
            t2.sort()
            print("Chart of acounts set to {}".format(t2))
        assert to_nc_not_accounted_for == set(),\
            'Make sure that in conversion all codes to are in the chart of accounts for {}'.format(coa_to.name)
        self.conversion[coa_from.name+'_to_'+coa_to.name] = conversion

    def convert_trial_balance(self, ttb):
        # This will fail if the from and to are not predefined.
        conversion = self.conversion['{} to {}'.format(
            ttb.chart_of_accounts.name,  # Converting from this COA
            self.coa_to.name)]  # converting to this COA
        index = []
        for key, value in conversion.items():
            index.append(key)
        index.sort()
        new = TrialBalance(self.coa_to, ttb.period_start, ttb.period_end)
        # TODO more checking to make sure all old data is used
        for name in new.chart_of_accounts.names:
            result = p(0)
            old_tb_list = conversion[name]
            for nc in old_tb_list:  # a list of accounts in the old trial balance
                try:
                    result += ttb[nc]
                except KeyError:  # Ignore where there are no entries
                    pass
            new.append(name, result)
        return new

