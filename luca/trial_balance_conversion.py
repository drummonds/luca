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
        # Todo make sure that in the conversion table no item occurs twice
        from_nc_not_accounted_for = set_nc_from ^ coa_from.nc_set()
        if from_nc_not_accounted_for != set():
            print("From nominal codes mismatch {}".format(from_nc_not_accounted_for))
            f1 = list(set_nc_from)
            f1.sort()
            print("Conversion set from {}".format(f1))
            f2 = list(coa_from.nc_set())
            f2.sort()
            print("Chart of acounts {} set from {}".format(coa_from.name, f2))
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
            print("Chart of acounts {} set to {}".format(coa_to.name, t2))
        assert to_nc_not_accounted_for == set(),\
            'Make sure that in conversion all codes to are in the chart of accounts for {}'.format(coa_to.name)
        self.conversion[coa_from.name+'_to_'+coa_to.name] = conversion

    def convert_trial_balance(self, source_trial_balance, destination_coa = None):
        if destination_coa == None:
            destination_coa = self.coa_to
        # This will fail if the from and to are not predefined.
        conversion_name = '{}_to_{}'.format(
            source_trial_balance.chart_of_accounts.name,  # Converting from this COA
            destination_coa.name)
        conversion_table = self.conversion[conversion_name]  # converting to this COA
        index = []
        for key, value in conversion_table.items():
            index.append(key)
        index.sort()
        new = TrialBalance(destination_coa, source_trial_balance.period_start, source_trial_balance.period_end)
        # TODO more checking to make sure all old data is used
        for destination_nc in new.chart_of_accounts.nominal_codes:
            result = p(0)
            old_tb_list = conversion_table[destination_nc]
            for nc in old_tb_list:  # a list of accounts in the old trial balance
                try:
                    result += source_trial_balance[nc]
                except KeyError:  # Ignore where there are no entries
                    pass
            new.append(destination_nc, result)
        return new

