import pandas as pd
import unittest

from luca import JournalSqlite, journal_from_db, p, ChartOfAccounts, chart_of_accounts_from_db


class ChartOfAccountsSqliteTest(unittest.TestCase):

    def test_db_basic(self):
        with chart_of_accounts_from_db("test_historic_trial_balances00.db") as coa_s:
            coa = coa_s.get_chart_of_account('SLF-MA')
            assert coa[4000] == 'Sales'
            assert coa.name_of(4000) == 'Sales'
