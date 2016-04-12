"""Journal Entry represents accounting entries.
"""
import pandas as pd

from .utils import p

class JournalEntryError(Exception):
    pass

class JournalItem:
    """This is simply a nominal code and an amount"""
    pass

class JournalEntry:
    """JournalEntry is a complete set of journal items.  It should add up to zero.  It can be as simple as representing
    a purchase invoice or it can be as complex as a trial balance from which you can derive a balance sheet and
    profit and loss statements.
    they are linked to a chart of accounts."""

    def __init__(self, chart_of_accounts):
        self._coa = chart_of_accounts
        self.dict = {}

    def __len__(self):
        return len(self.dict)

    def to_series(self):
        """Convert a journal entry to a Pandas DataSeries.  This is a lossy conversion so that things like the chart
        of accounts"""
        return pd.Series(self.dict)

    def is_valid(self):
        return self.series.sum() == p(0)

    @property
    def coa(self):
        return self._coa

    def add_dict(self, new_dict):
        self.dict = {**self.dict, **new_dict}

    def sum(self):
        result = p(0)
        for k, v in iter(self.dict.items()):
            result += v
        return result


    def append(self, nominal_code, value):
        if nominal_code in self.transaction:
            raise JournalEntryError('Attempting to add two entries to the same nominal code {} into {}'. \
                                   format(nominal_code, self.dict))
        else:
            self.dict[nominal_code] = value


    def is_valid(self):
        return (len(self.dict) > 0) and (self.sum() == p(0))
