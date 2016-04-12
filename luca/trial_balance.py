"""Trial Balance is a derivative of dataSeries.  Represents a trial balance wiht numeric COA
"""
import pandas as pd

from h3_yearend import p


class JournalEntry:
    """JournalEntry is a complete set of journal items.  It should add up to zero.  It can be as simple as representing
    a purchase invoice or it can be as complex as a trial balance from which you can derive a balance sheet and
    profit and loss statements."""

    def __init__(self, chart_of_accounts):
        self._coa = chart_of_accounts
        self.series = pd.Series()

    def __len__(self):
        return len(self.series)

    def is_valid(self):
        return self.series.sum() == p(0)

    @property
    def coa(self):
        return self._coa

    def add_dict(self, new_dict):
        def fill(nc):
            try:
                y_value = ttb[nc]
            except:
                y_value=p(0)
            try:
                t_value = year_open.ix[nc]['TB']
            except:
                t_value = p(0)
            return y_value + t_value
        # Create union of nominal codes
        new_nc = list(year_open.index.values)
        ttb_nc = list(ttb.axes[0])
        nc_list = list(set(ttb_nc) | set(year_nc))
        # For each nominal code add from both
        print('Added trial balance')
        nc_list.sort()
        df = pd.DataFrame([p(0)]*len(nc_list), index = nc_list, columns=['TB'])
        df['TB'] = [fill(r) for r in df.index]

