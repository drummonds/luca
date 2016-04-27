"""Journal Entry represents accounting entries.
"""
from copy import copy
import pandas as pd

from .utils import LucaError, p

class ChartOfAccountsError(Exception):
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
            self.company_name = 'Slumberfleece Limited'
            self.company_number = '123'
            self.constants= {
                'period_pnl': 2125,  # Period Profit and Loss - is a caculated item from trial balance
                'pnl_nc_start': 3000  # Nominal codes greater than this are all profit and loss
            }
            self.sales = [4000]
            self.material_costs_name = 'Total Material Cost'
            self.material_costs = [5000, 5001]
            self.variable_costs = [7000, 7100, 7103, 7102, 7105, 7006]
            self.fixed_production_costs = [7200, 7202, 7204, 7206]
            self.admin_costs = [7020, 8100, 8200, 8204, 8300, 7906, 8310, 8400, 8402, 8405, 8201,
                                8433, 8408, 8410, 8414, 8420, 8424, 8426, 8430, 8435, 8440]
            self.selling_costs = [4905, 6100, 6200, 6201, 4009]
            self.fixed_asset = [10]
            self.current_asset = [1001, 1100, 1102, 1115, 1103, 2105, 2104, 1200, 1202, 1203, 1204]
            self.short_term_liabilities = [2100, 2106, 2107, 2108, 2109, 2110]
            self.long_term_liabilities = [2103]
            self.owners_equity = [2120, 2125, 2126]
            self.optional_accounts = [5001]  # These nominal codes should only be present in the report if non zero
        elif name == 'drummonds':
            self.company_name = 'Drummonds.net Limited'
            self.company_number = '05759862'
            self.constants= {
                'period_pnl': 4200,  # Period Profit and Loss - is a caculated item from trial balance
                'pnl_nc_start': 4999  # Nominal codes greater than this are all profit and loss
            }
            self.sales = [5000, 5100]
            self.material_costs_name = 'Cost of Sales'
            self.material_costs = [6000, 6100, 6200]
            self.variable_costs = [7000]
            self.fixed_production_costs = [7001, 7002, 7100, 7205, 7300]
            self.admin_costs = [8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010, 8011, 8012, 8013,
                                8014, 8015, 8016, 8017, 8018, 8019, 8020, 8100, 8900]
            self.selling_costs = []
            self.fixed_asset = [100]
            self.current_asset = [1200, 1205, 1250, 2200]
            self.short_term_liabilities = [2000]
            self.long_term_liabilities = []
            self.owners_equity = [4100, 4200, 4999]
            self.optional_accounts = []  # These nominal codes should only be present in the report if non zero
            self.tax_control_account = 9500  # This is a balancing account for tax that is carried forward
            self.year_coporation_tax = 9510
        elif name == 'Test':
            self.company_name = 'Test Co Not Limited'
            self.company_number = '123'
            self.constants = {
                'period_pnl': 2125,  # Period Profit and Loss - is a caculated item from trial balance
                'pnl_nc_start': 3000  # Nominal codes greater than this are all profit and loss
            }
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
