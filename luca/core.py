"""This is the core of the code that I am using for practicaly purpposes.
It is however system specific."""
import sqlite3

from .coa_sqlite import chart_of_accounts_from_db
from .trial_balance_conversion import TrialBalanceConversion

DRUMMONDS_TO_FY_SUMMARY = {
    50: (5000, 5100,),  # Turnover
    1001: (1001, 1004, 1254, 1256, 7906,),
    1100: (1100, 1101,),
    1102: (1102,),
    1103: (1103, 1110, 1120,),
    1115: (1104, 1115, 1117,),
    1200: (1200, 1205, 1240, 1250, 1260, 1262, 1263, 9998, 9999,),
    1202: (1207, 1210, 1212, 1252,),
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
    8440: (7503, 8440,),}

SAGE_TO_SLF_MA = {
    10: (10, 20, 21, 30, 31, 40, 41,),
    1001: (1001, 1004, 1254, 1256, 7906,),
    1100: (1100, 1101,),
    1102: (1102,),
    1103: (1103, 1110, 1120,),
    1115: (1104, 1115, 1117,),
    1200: (1200, 1205, 1240, 1250, 1260, 1262, 1263, 9998, 9999,),
    1202: (1207, 1210, 1212, 1252,),
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

    def copy_trial_balance(self, period, old_prefix, new_prefix):
        """This is a datatabase level cooy"""
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


class CoreDrummond(Core):

    def __init__(self, file_name = 'historic_trial_balances.db'):
        super(CoreDrummond, self).__init__(file_name = file_name)
        self.base_chart_of_accounts_name = 'drummonds'
        with chart_of_accounts_from_db(self.dbname) as coa_s:
            self.coa = coa_s.get_chart_of_account(self.base_chart_of_accounts_name)
        self.converter = TrialBalanceConversion(self.coa)
        self.converter.add_conversion(self, DRUMMONDS_TO_FY_SUMMARY, self.coa, self.fy_coa)


class CoreSlumberfleece(Core):

    def __init__(self, file_name = 'historic_trial_balances.db'):
        super(CoreSlumberfleece, self).__init__(file_name = file_name)
        self.base_chart_of_accounts_name = 'SLF-MA'
        with chart_of_accounts_from_db(self.dbname) as coa_s:
            self.coa = coa_s.get_chart_of_account(self.base_chart_of_accounts_name)
        self.converter = TrialBalanceConversion(self.coa)
        self.converter.add_conversion(SAGE_TO_SLF_MA, self.coa, self.fy_coa)


