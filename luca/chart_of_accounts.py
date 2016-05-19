"""Journal Entry represents accounting entries.
"""
from copy import copy
import pandas as pd

from .utils import LucaError, p

class ChartOfAccountsError(Exception):
    pass


def _allowed_chart_of_account(name):
    allowed_coa = ('SLF-MA', 'drummonds', 'FY_Summary', 'FY_Detail_Summary', 'SAGE')  # Todo move to core
    assert name in allowed_coa, 'Only works for {} chart of accounts- you tried {}'.format(
        allowed_coa, name)


class ChartOfAccounts:
    """This has to be built before the journal entries are made"""

    def __init__(self, name):
        self.name = name
        self.dict = {}
        self.virtual_nominal_codes = {}
        if name == 'Test':
            self.__setup_test_chart_of_accounts()
        else:
            self.constants = {}

    def __len__(self):
        return len(self.dict)

    def append(self, nominal_code, name, category='Unknown', recalculate=True):
        if nominal_code in self.dict:
            raise ChartOfAccountsError('Attempting a second entry for nominal code {}, {}'. \
                                       format(nominal_code, name))
        elif nominal_code in self.virtual_nominal_codes:
            raise ChartOfAccountsError('Attempting to enter virtual nominal code {}, {}'. \
                                        format(nominal_code, name))
        else:
            self.dict[nominal_code] = (name, category,)
            if recalculate:  # Allow efficiency if adding lots
                self._recalculate_ranges()

    def add_dict(self, new_dict):
        #  Aim to do this
        #  self.dict = {**self.dict, **new_dict}
        # but want every value to be a decimal version
        for nominal_code, name in iter(new_dict.items()):
            self.append(nominal_code, name, recalculate=False)
        self._recalculate_ranges()

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
            set_nc = set_nc | {nc}
        return set_nc

    def add_virtual_nominal_code(self, nominal_code, nominal_code_list, overwrite=True):
        if not overwrite and nominal_code in self.virtual_nominal_codes:
            raise LucaError('Adding virtual nominal code that already exists {}'.format(nominal_code))
        self.virtual_nominal_codes[nominal_code] = [nc for nc in nominal_code_list]  # ensures and makes a list
        #  Note that ranges don't have to be recalculated.  By definition the virtual nominal code
        # has no actual item in the

    def _recalculate_ranges(self):
        """If any of the standard definitions eg retained_profit depends on calculated
        ranges of accounts then this needs to be recalculated every time the chart of account
        changes."""
        pass

    def __setup_test_chart_of_accounts(self):
        # Once only setup of default dictionary can't be part of recalculate as then
        self.dict = {
            10: ('Tangible fixed assets', 'Asset'),
            11: ('Debtors', 'Asset'),
            12: ('Cash at bank and in hand', 'Asset'),
            20: ('Creditors: Amounts falling due within one year', 'Liability'),
            21: ('Creditors: Amounts falling due after more than one year', 'Liability'),
            30: ('Profit and Loss Account', 'Equity'),
            31: ('Called up share capital', 'Equity'),
            # 32 Retained Earings virtual
            50: ('Turnover', 'Income'),
            60: ('Cost of sales', 'Expense'),
            70: ('Varriable costs', 'Expense'),
            80: ('Administrative Expenses', 'Expense'),
            91: ('Depreciation', 'Expense'),
            92: ('Amortization', 'Expense'),
            93: ('Interest', 'Expense'),
            94: ('Tax on(loss)/profit on ordinary acitivies', 'Expense'),
            96: ('Dividends', 'Expense')
        }
        self.company_name = 'Test Co Not Limited'
        self.company_number = '123'
        self.constants = {
            'period_pnl': 32,  # Period Retained Profit and Loss - is a calculated item from trial balance
            'pnl_nc_start': 49  # Nominal codes greater than this are all profit and loss
        }
        self._recalculate_ranges = self.__recalcalculate_test_chart_of_accounts
        self._recalculate_ranges()

    def __recalcalculate_test_chart_of_accounts(self):
        # See https://en.wikipedia.org/wiki/Profit_(accounting) for more information
        self.gross_profit = [50, 60]  # profit equals sales revenue minus cost of goods sold(COGS), thus
        # removing  only  the part of expenses that can be traced directly to the production or purchase of the
        # goods. Gross profit still includes general (overhead) expenses like R&D, S&M, G&A, also interest expense,
        # taxes and extraordinary items.
        self.EBITDA = self.gross_profit + [nc for nc, v in self.dict.items() if nc >=70 and nc < 90]
        #Earnings Before Interest, Taxes, Depreciation, and Amortization
        # (EBITDA) equals sales revenue minus cost of goods sold and all expenses except for interest,
        # amortization, depreciation and taxes. It measures the cash earnings that can be used to pay interest and
        # repay the principal. Since the interest is paid before income tax is calculated, the debtholder can
        # ignore taxes.
        self.PBIT = self.EBIT = self.EBITDA + [91, 92]
        # Earnings Before Interest and Taxes (EBIT)/ Operating profit equals
        # sales revenue minus cost of goods sold and all expenses except for interest and taxes. This is the
        # surplus generated by operations. It is also known as Operating Profit Before Interest and Taxes (OPBIT)
        # or simply Profit Before Interest and Taxes (PBIT).
        self.PBT = self.EBT = self.PBIT + [93]  # Earnings Before Taxes (EBT)/ Net Profit Before Tax equals sales
        # revenue minus cost of goods sold and all expenses except for taxes. It is also known as pre-tax book
        # income (PTBI), net operating income before taxes or simply pre-tax Income.
        self.PAT = self.EAT = self.PBT + [94]  # Earnings After Tax/ Net Profit After Tax equal sales revenue
        # after deducting all expenses, including taxes (unless some distinction about the treatment of
        # extraordinary expenses is made). In the US, the term Net Income is commonly used. Income before
        # extraordinary expenses represents the same but before adjusting for extraordinary items.
        self.retained_profit = self.retained_earnings = self.PAT + [96]  # Earnings After Tax/ Net Profit After Tax
        # minus payable dividends becomes Retained Earnings.
        self.calc_pnl = 32  # This is virtual nominal code as it is the balance of the P&L items for use in
        # balance sheet reports
        # TODO convert all lists of acounts to sets of accounts
        self.sales = [50]
        self.material_costs_name = 'Total Material Cost'
        self.material_costs = [60]
        self.variable_costs = [70]
        self.fixed_production_costs = []
        self.admin_costs = [80]
        self.establishment_costs = []
        self.finance_charges = [93]
        self.depreciation_costs = [90]
        self.dividends = [96]
        self.selling_costs = [60]
        self.fixed_asset = [10]
        self.current_asset = [11, 12]
        self.short_term_liabilities = [20]
        self.long_term_liabilities = [21]
        self.owners_equity = [30, 31, 32]
        self.called_up_capital = [31]
        self.profit_and_loss_account = [32]
        # Tooo There may be be a better place for this code so it doesn't have to be repeated
        self.add_virtual_nominal_code(self.calc_pnl, self.retained_profit, overwrite=True)

