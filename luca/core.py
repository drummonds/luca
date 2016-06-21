"""This is the core of the code that I am using for practicaly purpposes.
It is however system specific."""
import pandas as pd
import sqlite3

from .coa_sqlite import chart_of_accounts_from_db
from .trial_balance_conversion import TrialBalanceConversion

DRUMMONDS_TO_FY_SUMMARY = {
    10: (100, 102, 103, 150, 151, 162, 163 ),  # Tangible fixed assets
    11: (1100, ),  # Debtors
    12: (1200, 1205, 1250, 7205),  # Cash at bank and in hand
    20: (2100, 2200),  # Creditors: Amounts falling due within one year
    21: (3100, ),  # Creditors: Amounts falling due after more than one year
    30: (4100, ),  # Called up share capital
    31: (4200, 4350, 4351),  # Profit and Loss Account, 4300 is virtual
    # 32 Retained Earnings for period virtual
    50: (5000, 5100),  # Turnover
    60: (6000, 6100, 6200, 7010),  # Cost of sales
    80: (7000, 7001, 7002, 7100, 7300, 7500, 8000, 8001, 8002, 8003, 8005, 8006, 8007,
         8008, 8009, 8010, 8011, 8012, 8013, 8014,
         8017, 8018, 8019, 8020, 8021, 8100, 8300, 8900),  # Administrative Expenses
    91: (9100, ),  # Depreciation
    92: (9200, ),  # Amortisation
    93: (9300, ),  # Interest
    94: (9400, 9450, 9451, 9500, 9510),  # Tax on(loss)/profit on ordinary activities
    96: (9600, ),  # Dividends
    }

DRUMMONDS_TO_FY_DETAIL = {
    100: (100, 150, 151, 162, 163 ),  # Tangible fixed assets
    102: (102, ),  # Office Equipment cost
    103: (103, ),  # Office Equipment depreciation
    110: (1100, ),  # Debtors
    120: (1200, 1205, 7205, 1250),  # Cash at bank and in hand TODO Check 7205 smart user payment
    200: (2100, 2200),  # Creditors: Amounts falling due within one year
    210: (3100, ),  # Creditors: Amounts falling due after more than one year
    300: (4100, ),  # Called up share capital
    310: (4200, 4350, 4351),  # Profit and Loss Account 4300 is virtual and calculated
    500: (5000, 5100),  # Turnover
    600: (6000, 7010),  # Purchase
    610: (6100, 6200), # Subcontract cost
    700: (8300, ), # Home office costs
    750: (7100, 7300 ), # Employment costs TODO Check POYE/NI
    760: (8012, ),  # Staff training
    800: (7500, 8003, 8008, 8011, 8018, 8021),  # Sundry expense TODO check 8002 computer hardware capex
    810: (8005, 8006),  # Telephone and fax
    815: (8007, 8017, 8019, 8900), # Office Expense
    820: (7001, 7002, 8002, 8009, 8013, ),  # Computer software and maintenance costs
    825: (8001, 8014, 8020),  # Printing postage and stationery
    830: (8000, ),  # Accountancy Fees
    835: (8100, ),  # Legal and professional Fees
    840: (8010, ),  # Travel and subsistence
    890: (7000, ),  # Bank charges
    910: (9100, ),  # Depreciation
    920: (9200, ),  # Amortisation
    930: (9300, ),  # Interest
    940: (9400, 9450, 9451, 9500, 9510),  # Tax on(loss)/profit on ordinary activities
    960: (9600, ),  # Dividends
    }

SLF_MA_TO_FY_SUMMARY = {
    10: (10, ),  # 20, 21, 30, 31, 40, 41,),
    11: (1100, ),
    12: (1001, 1102, 1115, 1103, 2105, 2104, 1200, 1202, 1203, 1204),
    20: (2100, 2107, 2108, 2109, 2110, ),
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
    1102: (1102, ),
    1103: (1103, 1110, 1120,),
    1115: (1104, 1115, 1117,),
    1200: (1200, 1205, 1240, 1250, 1260, 1262, 1270, 1271, 1263, 9998, 9999,),
    1202: (1202, 1207, 1210, 1212, 1252,),
    1203: (1203, 1220,),
    1204: (1204, 1230, 1232,),
    2100: (2100, 2220,),
    2103: (2103, 2101,),
    2104: (2104, 2102,),
    2105: (2105, ),
    2106: (2106, 2320,),
    2107: (2107, 2210, 2211,),
    2108: (2200, 2201, 2202, 2204,),
    2109: (2109, 1105),
    2110: (2108, ),
    2120: (2120, 3000,),
    2125: (2125, 3200,),
    2126: (2126, 3210,),
    4000: (4000, 4200),
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
        # TODO the whole chart of accounts should be stored in the database including all the lists etc
        with chart_of_accounts_from_db(self.dbname) as coa_s:
            self.fy_coa = coa_s.get_chart_of_account('FY_Summary')
        self.__setup_core_chart_of_accounts()

    def __setup_core_chart_of_accounts(self):
        coa = self.fy_coa
        # balance sheet items
        coa.fixed_assets = [10]
        coa.debtors = [11]
        coa.cash_at_bank = [12]
        coa.current_asset = [12]
        coa.short_term_liabilities = [20]
        coa.long_term_liabilities = [21]
        coa.owners_equity = [30, 31, 32]
        coa.called_up_capital = [30]
        coa.retained_capital = [31]
        coa.profit_and_loss_account = [32]  # Period Profit and Loss - is a calculated item from trial balance
        coa.pnl_nc_start = 49  # Nominal codes greater than this are all profit and loss
        coa.sales = [50]
        coa.material_costs_name = 'Cost of Sales'
        coa.material_costs = [60]
        coa.variable_costs = []
        coa.fixed_production_costs = []
        coa.admin_costs = [80]
        coa.selling_costs = []
        coa.optional_accounts = []  # These nominal codes should only be present in the report if non zero
        coa.depeciation_costs = [91]
        coa.amortisation_costs = [92]
        coa.finance_costs = [93]
        coa.year_corporation_tax = [94]
        coa.dividends = [96]
        coa.gross_profit = [nc for nc, v in coa.dict.items() if nc >49 and nc < 80]
        coa.EBITDA = coa.gross_profit + [80]  # Earnings Before Interest, Taxes, Depreciation, and Amortization
        coa.PBIT = coa.EBIT = coa.EBITDA + [91, 92]
        coa.PBT = coa.EBT = coa.PBIT + [93]  # Earnings Before Taxes (EBT)/ Net Profit Before Tax equals sales
        coa.PAT = coa.EAT = coa.PBT + [94]  # Earnings After Tax/ Net Profit After Tax equal sales revenue
        coa.retained_profit = coa.retained_earnings = coa.PAT + [96]  # Earnings After Tax/ Net Profit After Tax
        coa.add_virtual_nominal_code(coa.profit_and_loss_account, coa.retained_profit)

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
        self.converter.add_conversion(DRUMMONDS_TO_FY_DETAIL, self.coa, self.fy_detail_coa)

    def initialise_chart_of_accounts(self, coa):
        """This is a generic setup for all chart of accounts that belong to Drummonds."""
        coa.company_name = 'Drummonds.net Limited'
        coa.company_number = '05759862'

    def __setup_core_chart_of_accounts(self):
        coa = self.coa
        coa.tax_reference = '846 85030 18478'
        coa.fixed_assets = [10]
        coa.office_equipment_cost = [102]
        coa.office_equipment_depreciation = [103]
        coa.annual_investment_allowance = [150]
        coa.machinery_and_plant_main_pool = [162]
        coa.cash_at_bank = [1200, 1205, 1250]
        coa.current_asset = [1200, 1205, 1250]
        coa.debtors = [1100]
        coa.short_term_liabilities = [2100, 2200]
        coa.long_term_liabilities = [3100]
        coa.owners_equity = [4100, 4200, 4300]
        coa.called_up_capital = [4100]
        coa.retained_capital = [4200]
        coa.profit_and_loss_account = [4300]   # This is virtual nominal code as it is the balance of the P&L items
        coa.trading_losses = [4350]
        coa.pnl_nc_start = 4999  # Nominal codes greater than this are all profit and loss
        # balance sheet reports
        coa.sales = [5000, 5100]
        coa.material_costs_name = 'Cost of Sales'
        coa.material_costs = [6000, 6100, 6200]
        coa.variable_costs = [7000]
        coa.fixed_production_costs = [7001, 7002, 7100, 7205, 7300]
        coa.admin_costs = [8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010, 8011, 8012, 8013,
                           8014, 8015, 8016, 8017, 8018, 8019, 8020, 8100, 8900]
        coa.depreciation_costs = [9100]
        coa.amortisation_costs = [9200]
        coa.finance_costs = [9300]
        coa.selling_costs = []
        coa.dividends = [9600]
        coa.optional_accounts = []  # These nominal codes should only be present in the report if non zero
        coa.tax_control_account = 9500  # This is a balancing account for tax that is carried forward
        coa.year_corporation_tax = [9400]
        coa.gross_profit = [nc for nc, v in coa.dict.items() if nc >4999 and nc < 8000]
        coa.EBITDA = coa.gross_profit + [nc for nc, v in coa.dict.items() if nc >=8000 and nc < 9000]
        coa.PBIT = coa.EBIT = coa.EBITDA + [9100, 9200]
        coa.PBT = coa.EBT = coa.PBIT + [9300]  # Earnings Before Taxes (EBT)/ Net Profit Before Tax equals sales
        coa.PAT = coa.EAT = coa.PBT + [9400]  # Earnings After Tax/ Net Profit After Tax equal sales revenue
        coa.retained_profit = coa.retained_earnings = coa.PAT + [9600]  # Earnings After Tax/ Net Profit After Tax
        coa.add_virtual_nominal_code(coa.profit_and_loss_account, coa.retained_profit)

    def __setup_core_detail_chart_of_accounts(self):
        coa = self.fy_detail_coa
        # balance sheet reports
        coa.fixed_assets = [100]
        coa.office_equipment_cost = [102]
        coa.office_equipment_depreciation = [103]
        coa.debtors = [110]
        coa.cash_at_bank = [120]
        coa.current_asset = [11, 120]
        coa.short_term_liabilities = [200]
        coa.long_term_liabilities = [210]
        coa.owners_equity = [300, 310, 320]
        coa.called_up_capital = [300]
        coa.retained_capital = [310]
        coa.profit_and_loss_account = [320]  # Virtual NC
        coa.pnl_nc_start = 499  # Nominal codes greater than this are all profit and loss
        coa.sales = [500]
        coa.material_costs_name = 'Cost of Sales'
        coa.material_costs = [600, 610]
        coa.variable_costs = []
        coa.fixed_production_costs = []
        coa.admin_costs = [810, 815, 820, 825, 800, 830, 835, 840]
        coa.selling_costs = []
        coa.establishment_costs = [700]
        coa.employment_costs = [750]
        coa.staff_training_costs = [760]
        coa.bank_charges = [890]
        coa.optional_accounts = []  # These nominal codes should only be present in the report if non zero
        coa.depreciation_costs = [910]
        coa.amortisation_costs = [920]
        coa.finance_costs = [930]
        coa.year_corporation_tax = [940]
        coa.tax_control_account = 950  # This is a balancing account for tax that is carried forward
        coa.dividends = [960]
        coa.gross_profit = [nc for nc, v in coa.dict.items() if nc >499 and nc < 800]
        coa.EBITDA = coa.gross_profit + [nc for nc, v in coa.dict.items() if nc >=800 and nc < 900]
        coa.PBIT = coa.EBIT = coa.EBITDA + [910, 920]
        coa.PBT = coa.EBT = coa.PBIT + [930]  # Earnings Before Taxes (EBT)/ Net Profit Before Tax equals sales
        coa.PAT = coa.EAT = coa.PBT + [940]  # Earnings After Tax/ Net Profit After Tax equal sales revenue
        coa.retained_profit = coa.retained_earnings = coa.PAT + [960]  # Earnings After Tax/ Net Profit After Tax
        coa.add_virtual_nominal_code(coa.profit_and_loss_account, coa.retained_profit)

class CoreSlumberfleece(Core):

    def __init__(self, file_name = 'historic_trial_balances.db'):
        super(CoreSlumberfleece, self).__init__(file_name = file_name)
        self.base_chart_of_accounts_name = 'SLF-MA'
        with chart_of_accounts_from_db(self.dbname) as coa_s:
            self.coa = coa_s.get_chart_of_account(self.base_chart_of_accounts_name)
            self.fy_coa = coa_s.get_chart_of_account('FY_Summary')
            self.sage_coa = coa_s.get_chart_of_account('SAGE')
        self.__setup_core_chart_of_accounts()
        self.__setup_sage_chart_of_accounts()
        self.converter = TrialBalanceConversion(self.coa)
        self.converter.add_conversion(SLF_MA_TO_FY_SUMMARY, self.coa, self.fy_coa)
        self.converter.add_conversion(SAGE_TO_SLF_MA, self.sage_coa, self.coa)

    def __setup_core_chart_of_accounts(self):
        coa = self.coa
        coa.company_name = 'Slumberfleece Limited'
        coa.company_number = '123'
        # balance sheet reports
        coa.fixed_asset = [10]
        coa.current_asset = [1001, 1100, 1102, 1115, 1103, 2105, 2104, 2111, 2112, 1200, 1202, 1203, 1204]
        coa.short_term_liabilities = [2100, 2106, 2107, 2108, 2109, 2110]
        coa.long_term_liabilities = [2103]
        coa.owners_equity = [2120, 2125, 2126]
        coa.called_up_capital = [2120]
        coa.retained_capital = [2125]
        coa.profit_and_loss_account = [2126]   # This is virtual nominal code as it is the balance of the P&L items
        coa.pnl_nc_start = 3000  # Nominal codes greater than this are all profit and loss
        coa.sales = [4000]
        coa.material_costs_name = 'Total Material Cost'
        coa.material_costs = [5000, 5001]
        coa.variable_costs = [7000, 7100, 7103, 7102, 7105, 7006]
        coa.fixed_production_costs = [7200, 7202, 7204, 7206]
        coa.admin_costs = [7020, 8100, 8200, 8204, 8300, 7906, 8310, 8400, 8402, 8405, 8201,
                           8433, 8408, 8410, 8414, 8420, 8424, 8426, 8430, 8435, 8440]
        coa.selling_costs = [4905, 6100, 6200, 6201, 4009]
        coa.optional_accounts = [5001]  # These nominal codes should only be present in the report if non zero
        coa.gross_profit = [nc for nc, v in coa.dict.items() if nc >4999 and nc < 8000]
        coa.EBITDA = coa.gross_profit + [nc for nc, v in coa.dict.items() if nc >=8000 and nc < 9000]
        coa.PBIT = coa.EBIT = coa.EBITDA + [9100, 9200]
        coa.PBT = coa.EBT = coa.PBIT + [9300]  # Earnings Before Taxes (EBT)/ Net Profit Before Tax equals sales
        coa.PAT = coa.EAT = coa.PBT + [9400]  # Earnings After Tax/ Net Profit After Tax equal sales revenue
        coa.retained_profit = coa.retained_earnings = coa.PAT + [9600]  # Earnings After Tax/ Net Profit After Tax
        coa.add_virtual_nominal_code(coa.profit_and_loss_account, coa.retained_profit)

    def __setup_sage_chart_of_accounts(self):
        """Almost identical to SLF-MA"""
        coa = self.sage_coa
        coa.company_name = 'Slumberfleece Limited'
        coa.company_number = '123'
        # balance sheet reports
        coa.fixed_asset = [10]
        coa.current_asset = [1001, 1100, 1102, 1115, 1103, 2105, 2104, 2111, 2112, 1200, 1202, 1203, 1204]
        coa.short_term_liabilities = [2100, 2106, 2107, 2108, 2109, 2110]
        coa.long_term_liabilities = [2103]
        coa.owners_equity = [3000, 3210, 3200]
        coa.called_up_capital = [3000]
        coa.retained_capital = [3200]
        coa.profit_and_loss_account = [3210]   # This is virtual nominal code as it is the balance of the P&L items
        coa.pnl_nc_start = 3999  # Nominal codes greater than this are all profit and loss
        coa.sales = [4000]
        coa.material_costs_name = 'Total Material Cost'
        coa.material_costs = [5000, 5001]
        coa.optional_accounts = [5001]  # These nominal codes should only be present in the report if non zero
        coa.variable_costs = [7000, 7100, 7103, 7102, 7105, 7006]
        coa.fixed_production_costs = [7200, 7202, 7204, 7206]
        coa.admin_costs = [7020, 8100, 8200, 8204, 8300, 7906, 8310, 8400, 8402, 8405, 8201,
                           8433, 8408, 8410, 8414, 8420, 8424, 8426, 8430, 8435, 8440]
        coa.selling_costs = [4905, 6100, 6200, 6201, 4009]
        coa.gross_profit = [nc for nc, v in coa.dict.items() if nc >4999 and nc < 8000]
        coa.EBITDA = coa.gross_profit + [nc for nc, v in coa.dict.items() if nc >=8000 and nc < 9000]
        coa.PBIT = coa.EBIT = coa.EBITDA + [9100, 9200]
        coa.PBT = coa.EBT = coa.PBIT + [9300]  # Earnings Before Taxes (EBT)/ Net Profit Before Tax equals sales
        coa.PAT = coa.EAT = coa.PBT + [9400]  # Earnings After Tax/ Net Profit After Tax equal sales revenue
        coa.retained_profit = coa.retained_earnings = coa.PAT + [9600]  # Earnings After Tax/ Net Profit After Tax
        coa.add_virtual_nominal_code(coa.profit_and_loss_account, coa.retained_profit)


