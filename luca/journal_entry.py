"""Journal Entry represents accounting entries.
"""
from copy import copy
import pandas as pd

from .chart_of_accounts import ChartOfAccounts
from .utils import LucaError, p


class JournalEntryError(Exception):
    pass


class JournalItem:
    """This is simply a nominal code and an amount"""
    pass


class JournalEntry:
    """JournalEntry is a complete set of journal items.  It should add up to zero.  It can be as simple as representing
    a purchase invoice or it can be as complex as a trial balance from which you can derive a balance sheet and
    profit and loss statements.
    they are linked to a chart of accounts.
    Every value in the journal is a decimal."""

    def __init__(self, chart_of_accounts):
        if not isinstance(chart_of_accounts, ChartOfAccounts):
            raise LucaError(' Trying to create JournalEntry a chart of accounts that is not ChartOfAccounts. {}'.
                            format(chart_of_accounts))
        self.chart_of_accounts = chart_of_accounts
        self.dict = {}  # Dictionary for JournalEntry of nominal_code: value

    def __len__(self):
        return len(self.dict)

    def __copy__(self):
        new = JournalEntry(self.chart_of_accounts)  # Same chart of accounts
        new.dict = self.dict.copy()
        return new

    def __add__(self, b):

        def fill(nominal_code):
            try:
                a_value = self[nominal_code]
            except:
                a_value = p(0)
            try:
                b_value = b[nominal_code]
            except:
                b_value = p(0)
            return a_value + b_value

        assert self.chart_of_accounts.name == b.chart_of_accounts.name, 'Chart of accounts must be the same {}, {}'.\
                format(self.chart_of_accounts.name, b.chart_of_accounts.name)
        nc_list = list(set(self.nominal_codes) | set(b.nominal_codes))
        # For each nominal code add from both
        nc_list.sort()
        new = copy(self)
        new.dict = {nc:fill(nc) for nc in nc_list}
        return new

    def to_series(self):
        """Convert a journal entry to a Pandas DataSeries.  This is a lossy conversion so that things like the chart
        of accounts"""
        return pd.Series(self.dict)

    def is_valid(self):
        return self.series.sum() == p(0)

    def append(self, nominal_code, value):
        if nominal_code in self.dict:
            raise JournalEntryError('Attempting to add two entries to the same nominal code {} into {}'. \
                                    format(nominal_code, self.dict))
        else:
            self.dict[nominal_code] = p(value)

    def add_dict(self, new_dict):
        #  Aim to do this
        #  self.dict = {**self.dict, **new_dict}
        # but want every value to be a decimal version
        for k, v in iter(new_dict.items()):
            self.dict[k] = p(v)

    def add_series(self, new_series):
        #  Assume series has
        for k, v in new_series.iteritems():
            self.dict[k] = p(v)

    def sum(self):
        result = p(0)
        for k, v in iter(self.dict.items()):
            result += v
        return result

    def is_valid(self):
        return (len(self.dict) > 0) and (self.sum() == p(0))

    def __getitem__(self, nominal_code):
        """Use standard square bracket notation to get data from journal entry"""
        try:
            sum = 0
            for i in nominal_code:
                sum += self[i]
            return sum
        except TypeError:
            try:
                self[self.chart_of_accounts.virtual_nominal_codes[nominal_code]]
                # Some properties are like nominal codes but are in fact virtual.  Eg the period profit and loss
                # is a calculated number
            except KeyError:  # Just get the normal data
                try:
                    return self.dict[nominal_code]
                except KeyError:  #  There is no data but it might be a valid nominal code
                    if self.chart_of_accounts[nominal_code]:
                        return p(0)
                    else:
                        return LucaError('Nomiinal code not in chart of accounts {}'.format(nominal_code))


    def get_value(self, nominal_code, default = 0):
        """This might be used in reports where you want to make sure you just print blank data for
        information which is missing"""
        try:
            return self[nominal_code]
        except (KeyError, IndexError) as e:
            return default

    def __setitem__(self, nominal_code, item):
        if nominal_code in self.dict:  # Self.dict is all the codes that are present.  This is slightly slacker
            # than allowing only codes in the chart of accounts.  Inferring chart of accounts
            # TOO eliminate this and create a fnction to build an inferred chart of accounts
            self.dict[nominal_code] = item
        elif nominal_code in self.chart_of_accounts.dict:  # These are codes that could be present
            self.dict[nominal_code] = item
        else:
            raise LucaError('Setting nominal code {} but not in chart of accounts {}'.format(
                nominal_code, self.chart_of_accounts.name))

    @property
    def nominal_codes(self):
        nc = [nc for nc in self.dict.keys()]
        nc.sort()
        return nc

    @property
    def coa(self):  #  Aid as often used as an abrevation
        return self.chart_of_accounts


class TrialBalance(JournalEntry):
    """Every TrialBalance is or should be a valid JournalEntry."""

    def __init__(self, chart_of_accounts, period_start=None, period_end=None):
        super().__init__(chart_of_accounts)
        self.period_start= period_start
        self.period_end= period_end

    def __copy__(self):
        new = TrialBalance(self.chart_of_accounts, self.period_start, self.period_end)  # Same chart of accounts
        new.dict = self.dict.copy()
        return new

    @property
    def profit_and_loss(self):
        return self[self.chart_of_accounts.retained_profit]


    def close_period(self):
        """AT the end of a year you want to close off a year and only roll forward the Balance sheet items.
        These calculations do that."""
        self.chart_of_accounts.assert_valid_name()
        pnl = self.profit_and_loss
        # print("P&L = {}".format(pnl))
        try:
            old_pnl = self[self.chart_of_accounts.period_pnl]
        except KeyError:  # There is no old pnl
            old_pnl = p(0)
        # print("Prev retain = {}, changing to {}".format(old_pnl, old_pnl+pnl))
        b = copy(self)
        b[self.chart_of_accounts.period_pnl] = old_pnl+pnl
        new_pnl = b[self.chart_of_accounts.period_pnl]
        for k, v in iter(self.dict.items()):
            if k > self.chart_of_accounts.pnl_nc_start:
                b[k]=p(0)
        # print("Sum after clearing old balances = {}".format(b.sum()))
        return b