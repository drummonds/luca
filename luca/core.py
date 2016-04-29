"""This is the core of the code that I am using for practicaly purpposes.
It is however system specific."""
import pandas as pd
import sqlite3

from .coa_sqlite import chart_of_accounts_from_db
from .trial_balance_conversion import TrialBalanceConversion

DRUMMONDS_TO_FY_SUMMARY = {
    10: (100, ),  # Tangible fixed assets
    11: (),  # Debtors
    12: (1200, 1205, 1250, 2200),  # Cash at bank and in hand
    20: (2000, ),  # Creditors: Amounts falling due within one year
    21: (),  # Creditors: Amounts falling due after more than one year
    30: (4200, 4300),  # Profit and Loss Account
    31: (4100, ),  # Called up share capital
    50: (5000, 5100),  # Turnover
    60: (6000, 6100, 6200, 7010, 7500),  # Cost of sales
    80: (7000, 7001, 7002, 7100, 7205, 7300, 8000, 8001, 8002, 8003, 8005, 8006, 8007,
         8008, 8009, 8010, 8011, 8012, 8013, 8014, 8017, 8018, 8019, 8020, 8100, 8900),
    # Administrative Expenses
    91: (3500, 9500, 9510),  # Tax on(loss)/profit on ordinary activities
    }

DRUMMONDS_TO_FY_DETAIL = {
    100: (100, ),  # Tangible fixed assets
    110: (),  # Debtors
    120: (1200, 1205, 1250, 2200),  # Cash at bank and in hand
    200: (2000, ),  # Creditors: Amounts falling due within one year
    210: (),  # Creditors: Amounts falling due after more than one year
    300: (4200, 4300),  # Profit and Loss Account
    310: (4100, ),  # Called up share capital
    500: (5000, 5100),  # Turnover
    600: (6000, 6100, 6200, 7010, 7500),  # Cost of sales
    800: (7000, 7001, 7002, 7100, 7205, 7300, 8000, 8001, 8002, 8003, 8005, 8006, 8007,
         8008, 8009, 8010, 8011, 8012, 8013, 8014, 8017, 8018, 8019, 8020, 8100, 8900),
    # Administrative Expenses
    910: (3500, 9500, 9510),  # Tax on(loss)/profit on ordinary activities
    }
SLF_MA_TO_FY_SUMMARY = {
    10: (10, ),  # 20, 21, 30, 31, 40, 41,),
    11: (1100, ),
    12: (1001, 1102, 1115, 1103, 2105, 2104, 1200, 1202, 1203, 1204),
    20: (2100, 2107, 2108, 2109, 2110),
    21: (2103, ),
    30: (2125, 2126),
    31: (2120, ),
    50: (4000, ),
    60: (5000, 5001, 4905, 6100, 6200, 6201, 4009),
    80: (7000, 7100, 7103, 7102, 7105, 7006, 7200, 7202, 7204, 7206, 7020, 8100, 8200, 8204, 8300, 7906, 8310, 8400,
         8402, 8405, 8201, 8433, 8408, 8410, 8414, 8420, 8424, 8426, 8430, 8435, 8440),
    91: (2106, ),
}

SAGE_TO_SLF_MA = {
    10: (10, 20, 21, 30, 31, 40, 41,),
    1001: (1001, 1004, 1254, 1256, 7906,),
    1100: (1100, 1101,),
    1102: (1102,),
    1103: (1103, 1110, 1120,),
    1115: (1104, 1115, 1117,),
    1200: (1200, 1205, 1240, 1250, 1260, 1262, 1263, 9998, 9999,),
    1202: (1202, 1207, 1210, 1212, 1252,),
    1203: (1203, 1220,),
    1204: (1204, 1230, 1232,),
    2100: (2100, 2220,),
    2103: (2103, 2101,),
    2104: (2104, 2102,),
    2105: (2105,),
    2106: (2106, 2320,),
    2107: (2107, 2210, 2211,),
    2108: (2200, 2201, 2202, 2204,),
    2109: (2109,),
    2110: (2110, 2108,),
    2120: (2120, 3000,),
    2125: (2125, 3210,),
    2126: (2126, 3200,),
    4000: (4000,),
    4009: (4009,),
    4905: (4905,),
    5000: (5000,),
    5001: (5001,),
    6100: (6100,),
    6200: (6200,),
    6201: (6201,),
    7000: (7000,),
    7006: (7006,),
    7020: (7020,),
    7100: (7100,),
    7102: (7102,),
    7103: (7103,),
    7105: (7105,),
    7200: (7200,),
    7202: (7202,),
    7204: (7204,),
    7206: (7206,),
    7906: (),
    8100: (8100, 8102,),
    8200: (8200,),
    8201: (7604, 8201,),
    8204: (7901, 8204,),
    8300: (8300,),
    8310: (8310,),
    8400: (8400,),
    8402: (8402,),
    8405: (8301, 8405,),
    8408: (8408,),
    8410: (8410,),
    8414: (8414,),
    8420: (8420, 8421,),
    8424: (8424,),
    8426: (8426,),
    8430: (8430,),
    8433: (8433,),
    8435: (8435,),
    8440: (7503, 8440,),
}


class Core:

    def __init__(self, file_name = 'historic_trial_balances.db'):
        self.filename = file_name
        self.dbname = file_name  # Default database name
        with chart_of_accounts_from_db(self.dbname) as coa_s:
            self.fy_coa = coa_s.get_chart_of_account('FY_Summary')
        self.__setup_core_chart_of_accounts()

    def __setup_core_chart_of_accounts(self):
        coa = self.fy_coa
        coa.constants = {
            'period_pnl': 32,  # Period Profit and Loss - is a caculated item from trial balance
            'pnl_nc_start': 49  # Nominal codes greater than this are all profit and loss
        }
        coa.calc_pnl = 32  # This is virtual nominal code as it is the balance of the P&L items for use in
        # balance sheet reports
        coa.sales = [50]
        coa.material_costs_name = 'Cost of Sales'
        coa.material_costs = [60]
        coa.variable_costs = []
        coa.fixed_production_costs = []
        coa.admin_costs = [80]
        coa.selling_costs = []
        coa.fixed_asset = [10]
        coa.current_asset = [12]
        coa.short_term_liabilities = [20]
        coa.long_term_liabilities = [21]
        coa.owners_equity = [30, 31, 32]
        coa.optional_accounts = []  # These nominal codes should only be present in the report if non zero
        coa.tax_control_account = 91  # This is a balancing account for tax that is carried forward
        coa.year_corporation_tax = [91]

    def copy_trial_balance(self, period, old_prefix, new_prefix):
        """This is a datatabase level copy"""
        conn = sqlite3.connect(self.dbname)
        try:
            cursor = conn.cursor()
            sql = """DELETE FROM trial_balance WHERE period = '{1}{0}'""".format(period, new_prefix)
            cursor.execute(sql)
            sql = """insert into trial_balance
    (period, code, balance)
    select '{2}{0}', code, balance from trial_balance WHERE period = '{1}{0}'""".format(period, old_prefix, new_prefix)
            cursor.execute(sql)
            conn.commit()
        finally:
            conn.close()

    def periods(self):
        """Returns a list of all the names of the trial balance periods that have been stored."""
        conn = sqlite3.connect(self.dbname)
        try:
            sql = 'SELECT DISTINCT period FROM trial_balance ORDER BY period'
            df = pd.read_sql(sql, conn)
        finally:
            conn.close()
        result = list(df['period'])
        result.sort()
        return result

class CoreDrummonds(Core):

    def __init__(self, file_name = 'historic_trial_balances.db'):
        super(CoreDrummonds, self).__init__(file_name = file_name)
        self.base_chart_of_accounts_name = 'drummonds'
        with chart_of_accounts_from_db(self.dbname) as coa_s:
            self.coa = coa_s.get_chart_of_account(self.base_chart_of_accounts_name)
            self.fy_detail_coa = coa_s.get_chart_of_account('FY_Detail_Summary')
        for coa in (self.coa, self.fy_coa, self.fy_detail_coa):
            self.initialise_chart_of_accounts(coa)
        self.__setup_core_chart_of_accounts()  # This is just to abstract all the details
        self.__setup_core_detail_chart_of_accounts()
        self.converter = TrialBalanceConversion(self.coa)
        self.converter.add_conversion(DRUMMONDS_TO_FY_SUMMARY, self.coa, self.fy_coa)

    def initialise_chart_of_accounts(self, coa):
        """This is a generic setup for all chart of accounts that belong to Drummonds."""
        coa.company_name = 'Drummonds.net Limited'
        coa.company_number = '05759862'

    def __setup_core_chart_of_accounts(self):
        coa = self.coa
        coa.constants = {
            'period_pnl': 4200,  # Period Profit and Loss - is a caculated item from trial balance
            'pnl_nc_start': 4999  # Nominal codes greater than this are all profit and loss
        }
        coa.calc_pnl = 4300  # This is virtual nominal code as it is the balance of the P&L items for use in
        # balance sheet reports
        coa.sales = [5000, 5100]
        coa.material_costs_name = 'Cost of Sales'
        coa.material_costs = [6000, 6100, 6200]
        coa.variable_costs = [7000]
        coa.fixed_production_costs = [7001, 7002, 7100, 7205, 7300]
        coa.admin_costs = [8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010, 8011, 8012, 8013,
                           8014, 8015, 8016, 8017, 8018, 8019, 8020, 8100, 8900]
        coa.selling_costs = []
        coa.fixed_asset = [100]
        coa.current_asset = [1200, 1205, 1250, 2200]
        coa.short_term_liabilities = [2000]
        coa.long_term_liabilities = []
        coa.owners_equity = [4100, 4200, 4300]
        coa.optional_accounts = []  # These nominal codes should only be present in the report if non zero
        coa.tax_control_account = 9500  # This is a balancing account for tax that is carried forward
        coa.year_corporation_tax = [9510]

    def __setup_core_detail_chart_of_accounts(self):
        coa = self.fy_detail_coa
        coa.constants = {
            'period_pnl': 320,  # Period Profit and Loss - is a caculated item from trial balance
            'pnl_nc_start': 490  # Nominal codes greater than this are all profit and loss
        }
        coa.calc_pnl = 320  # This is virtual nominal code as it is the balance of the P&L items for use in
        # balance sheet reports
        coa.sales = [500]
        coa.material_costs_name = 'Cost of Sales'
        coa.material_costs = [600]
        coa.variable_costs = []
        coa.fixed_production_costs = []
        coa.admin_costs = [800]
        coa.selling_costs = []
        coa.fixed_asset = [100]
        coa.current_asset = [120]
        coa.short_term_liabilities = [200]
        coa.long_term_liabilities = [210]
        coa.owners_equity = [300, 310, 320]
        coa.optional_accounts = []  # These nominal codes should only be present in the report if non zero
        coa.tax_control_account = 910  # This is a balancing account for tax that is carried forward
        coa.year_corporation_tax = [910]


class CoreSlumberfleece(Core):

    def __init__(self, file_name = 'historic_trial_balances.db'):
        super(CoreSlumberfleece, self).__init__(file_name = file_name)
        self.base_chart_of_accounts_name = 'SLF-MA'
        with chart_of_accounts_from_db(self.dbname) as coa_s:
            self.coa = coa_s.get_chart_of_account(self.base_chart_of_accounts_name)
            self.fy_coa = coa_s.get_chart_of_account('FY_Summary')
            self.sage_coa = coa_s.get_chart_of_account('SAGE')
        self.__setup_core_chart_of_accounts()
        self.converter = TrialBalanceConversion(self.coa)
        self.converter.add_conversion(SLF_MA_TO_FY_SUMMARY, self.coa, self.fy_coa)
        self.converter.add_conversion(SAGE_TO_SLF_MA, self.sage_coa, self.coa)

    def __setup_core_chart_of_accounts(self):
        coa = self.coa
        coa.company_name = 'Slumberfleece Limited'
        coa.company_number = '123'
        coa.constants = {
            'period_pnl': 2125,  # Period to date Profit and Loss
            'pnl_nc_start': 3000  # Nominal codes greater than this are all profit and loss
            }
        coa.calc_pnl = 2126  # This is virtual nominal code as it is the balance of the P&L items for use in
        # balance sheet reports
        coa.sales = [4000]
        coa.material_costs_name = 'Total Material Cost'
        coa.material_costs = [5000, 5001]
        coa.variable_costs = [7000, 7100, 7103, 7102, 7105, 7006]
        coa.fixed_production_costs = [7200, 7202, 7204, 7206]
        coa.admin_costs = [7020, 8100, 8200, 8204, 8300, 7906, 8310, 8400, 8402, 8405, 8201,
                           8433, 8408, 8410, 8414, 8420, 8424, 8426, 8430, 8435, 8440]
        coa.selling_costs = [4905, 6100, 6200, 6201, 4009]
        coa.fixed_asset = [10]
        coa.current_asset = [1001, 1100, 1102, 1115, 1103, 2105, 2104, 1200, 1202, 1203, 1204]
        coa.short_term_liabilities = [2100, 2106, 2107, 2108, 2109, 2110]
        coa.long_term_liabilities = [2103]
        coa.owners_equity = [2120, 2125, 2126]
        coa.optional_accounts = [5001]  # These nominal codes should only be present in the report if non zero
