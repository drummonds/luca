"""Journal Entry represents accounting entries.
"""
from copy import copy
import pandas as pd

from .utils import LucaError, p


class JournalEntryError(Exception):
    pass


class JournalItem:
    """This is simply a nominal code and an amount"""
    pass

def _allowed_chart_of_account(name):
    allowed_coa = ('SLF-MA', 'drummonds')
    assert name in allowed_coa, 'Only works for {} chart of accounts- you tried {}'.format(
        allowed_coa, name)


class ChartOfAccounts:
    """This has to be built before the journal entries are made"""

    def __init__(self, name):
        self.name = name
        self.dict = {}
        if name == 'SLF-MA':
            self.constants= {
                'period_pnl': 2125,  # Period Profit and Loss - is a caculated item from trial balance
                'pnl_nc_start': 3000  # Nominal codes greater than this are all profit and loss
            }
        elif name == 'drummonds':
            self.constants= {
                'period_pnl': 4200,  # Period Profit and Loss - is a caculated item from trial balance
                'pnl_nc_start': 4999  # Nominal codes greater than this are all profit and loss
            }
        elif name == 'Test':
            self.constants = {
                'period_pnl': 2125,  # Period Profit and Loss - is a caculated item from trial balance
                'pnl_nc_start': 3000  # Nominal codes greater than this are all profit and loss
            }
        else:
            self.constants = {}

    def __len__(self):
        return len(self.dict)

    def append(self, nominal_code, name, category='Unknown'):
        if nominal_code in self.dict:
            raise JournalEntryError('Attempting a second entry for nominal code {}, {}'. \
                                    format(nominal_code, name))
        else:
            self.dict[nominal_code] = (name, category)

    def add_dict(self, new_dict):
        #  Aim to do this
        #  self.dict = {**self.dict, **new_dict}
        # but want every value to be a decimal version
        for nominal_code, name in iter(new_dict.items()):
            self.append(nominal_code, name)

    def __getitem__(self, item):
        return self.name_of(item)

    def name_of(self, nominal_code):
        return self.dict[nominal_code][0]

    def category_of(self, nominal_code):
        return self.dict[nominal_code][1]

    @property
    def names(self):
        n = list(self.dict.keys())
        n.sort()
        return n

    def assert_valid_name(self):
        """Assert that the name of the chart of accounts is a valid one and supported.  This is more a temporary
        functon when only a small subset of chart of accounts are supported."""
        _allowed_chart_of_account(self.name)

    @property
    def pnl_nc_start(self):
        return self.constants['pnl_nc_start']

    @property
    def period_pnl(self):
        return self.constants['period_pnl']


class JournalEntry:
    """JournalEntry is a complete set of journal items.  It should add up to zero.  It can be as simple as representing
    a purchase invoice or it can be as complex as a trial balance from which you can derive a balance sheet and
    profit and loss statements.
    they are linked to a chart of accounts.
    Every value in the journal is a decimal."""

    def __init__(self, chart_of_accounts):
        self.chart_of_accounts = chart_of_accounts
        self.dict = {}

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
        # TODO should really check that chart of accounts is correct
        # Create union of nominal codes
        nc_list = list(set(self.chart_of_accounts.names) | set(b.chart_of_accounts.names))
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

    def __getitem__(self, item):
        return self.dict[item]

    def __setitem__(self, nominal_code, item):
        if nominal_code in self.dict:
            self.dict[nominal_code] = item
        else:
            raise LucaError('Setting nominal code {} but not in chart of accounts {}'.format(
                nominal_code, self.chart_of_accounts.name))


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
        result = p(0)
        for k, v in iter(self.dict.items()):
            if k > self.chart_of_accounts.pnl_nc_start:
                result += v
        return result


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