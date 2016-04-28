import unittest

from luca import ChartOfAccounts, JournalEntry, TrialBalance, p
from luca import chart_of_accounts_from_db


class TestChartOfAccounts(unittest.TestCase):

    def test_simple_chart_off_accounts(self):
        coa = ChartOfAccounts('Test')
        coa.add_dict({2120: 'Share Capital', 1200: 'Bank'})
        assert coa[1200] == 'Bank'
        assert coa[2120] == 'Share Capital'
        assert coa.names == ['Bank', 'Share Capital']

    def test_db_chart_of_accounts(self):
        chart_of_accounts_name = 'SLF-MA'
        with chart_of_accounts_from_db('test_historic_trial_balances00.db') as coa_s:
            coa = coa_s.get_chart_of_account(chart_of_accounts_name)
        print(coa.names)
        assert 'Bank Current Account' in coa.names
