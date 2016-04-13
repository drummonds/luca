import pandas as pd
import unittest

from luca import JournalSqlite, journal_from_db, p, TrialBalance


class JournalSqliteTest(unittest.TestCase):
    def test_db_basic(self):
        with journal_from_db("test_historic_trial_balances00.db", 'SLF-MA') as js:
            je = js.get_entry('YTD-AUG-14')
            assert je[4000] == p(-781410.59)
            assert je.is_valid()

    def test_db_trial_balance(self):
        with journal_from_db("test_historic_trial_balances00.db", 'SLF-MA',
                             journal_entry_class=TrialBalance) as js:
            tb = js.get_entry('YTD-AUG-14')
            assert tb[4000] == p(-781410.59)
            assert tb.is_valid()
            assert isinstance(tb, TrialBalance)
