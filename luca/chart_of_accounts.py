"""Journal Entry represents accounting entries.
"""
from copy import copy
import pandas as pd

from .utils import LucaError, p

class ChartOfAccountsError(Exception):
    pass


def _allowed_chart_of_account(name):
    allowed_coa = ('SLF-MA', 'drummonds', 'FY_Summary', 'FY_Detail_Summary')  # Todo move to core
    assert name in allowed_coa, 'Only works for {} chart of accounts- you tried {}'.format(
        allowed_coa, name)


class ChartOfAccounts:
    """This has to be built before the journal entries are made"""

    def __init__(self, name):
        self.name = name
        self.dict = {}
        if name == 'Test':
            self.company_name = 'Test Co Not Limited'
            self.company_number = '123'
            self.constants = {
                'period_pnl': 2125,  # Period Profit and Loss - is a caculated item from trial balance
                'pnl_nc_start': 3000  # Nominal codes greater than this are all profit and loss
            }
            self.calc_pnl = 2126  # This is virtual nominal code as it is the balance of the P&L items for use in
            # balance sheet reports
            self.sales = [4000]
            self.material_costs_name = 'Total Material Cost'
            self.material_costs = [5000]
            self.variable_costs = [7000]
            self.fixed_production_costs = [7200]
            self.admin_costs = [8100, 8200]
            self.selling_costs = [6100]
            self.fixed_asset = [10]
            self.current_asset = [1200]
            self.short_term_liabilities = [2100]
            self.long_term_liabilities = [2103]
            self.owners_equity = [2125]
            self.optional_accounts = [5001]  # These nominal codes should only be present in the report if non zero
        else:
            self.constants = {}

    def __len__(self):
        return len(self.dict)

    def append(self, nominal_code, name, category='Unknown'):
        if nominal_code in self.dict:
            raise ChartOfAccountsError('Attempting a second entry for nominal code {}, {}'. \
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
        n = [self.name_of(nc) for nc in self.dict.keys()]
        n.sort()
        return n

    @property
    def nominal_codes(self):
        nc = [nc for nc in self.dict.keys()]
        nc.sort()
        return nc

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

    def nc_set(self):
        """Return set of all nominal codes"""
        set_nc = set()
        for nc, name in self.dict.items():
            set_nc = set_nc | set([nc])
        return set_nc
