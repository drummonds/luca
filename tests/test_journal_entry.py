import unittest

from luca import ChartOfAccounts, JournalEntry, TrialBalance, p


class TestTB(unittest.TestCase):

    def test_empty_trial_balance(self):
        coa = ChartOfAccounts('Test')
        coa.add_dict({1200: 'Bank', 2120: 'Share Capital'})
        je = JournalEntry(coa)
        assert len(je) == 0
        assert not je.is_valid()  # Is empty
        assert je.chart_of_accounts.name == 'Test'

    def test_trial_balance_1(self):
        """Test basic trial balance as a default journal entry"""
        coa = ChartOfAccounts('Test')
        coa.add_dict({1200: 'Bank', 2120: 'Share Capital'})
        je = JournalEntry(coa)
        je.add_dict({1200: 100, 2120: -100})
        assert len(je) == 2
        assert je.is_valid()
        assert je.sum() == 0
        assert len(je.chart_of_accounts) == 2

    def test_trial_balance_2(self):
        """Try out the predefined type"""
        coa = ChartOfAccounts('Test')
        coa.add_dict({1200: 'Bank', 2120: 'Share Capital', 8405: 'Admin Expenses'})
        tb = TrialBalance(coa)
        tb.add_dict({1200:50, 2120:-100, 8405:50})
        assert len(tb) == 3
        assert tb.is_valid()
        assert tb.profit_and_loss == p(50)


    def test_trial_balance_add(self):
        """Try out the predefined type"""
        coa = ChartOfAccounts('Test')
        coa.add_dict({1200: 'Bank', 2120: 'Share Capital'})
        je = JournalEntry(coa)
        je.add_dict({1200: 100, 2120: -100})
        je2 = je + je
        assert len(je2) == 2
        assert je2.is_valid()
        assert je2.sum() == 0
        assert len(je2.chart_of_accounts) == 2
        assert je2[1200]  == p(200)
