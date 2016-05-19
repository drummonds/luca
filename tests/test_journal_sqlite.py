import pandas as pd
import unittest

from luca import JournalSqlite, journal_from_db, p, TrialBalance, chart_of_accounts_from_db


class JournalSqliteTest(unittest.TestCase):

    def test_db_basic(self):
        chart_of_accounts_name = 'SLF-MA'
        with chart_of_accounts_from_db('test_historic_trial_balances00.db') as coa_s:
            coa = coa_s.get_chart_of_account(chart_of_accounts_name)
        with journal_from_db("test_historic_trial_balances00.db", coa) as js:
            je = js.get_entry('YTD-AUG-14')
            assert je[4000] == p(-781410.59)
            assert je.is_valid()

    def test_db_trial_balance(self):
        chart_of_accounts_name = 'SLF-MA'
        with chart_of_accounts_from_db('test_historic_trial_balances00.db') as coa_s:
            coa = coa_s.get_chart_of_account(chart_of_accounts_name)
        with journal_from_db("test_historic_trial_balances00.db", coa,
                             journal_entry_class=TrialBalance) as js:
            tb = js.get_entry('YTD-AUG-14')
            assert tb[4000] == p(-781410.59)
            assert tb.is_valid()
            assert isinstance(tb, TrialBalance)
