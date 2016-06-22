import unittest

from luca import ChartOfAccounts, JournalEntry, TrialBalance, p, LucaError


class TestTB(unittest.TestCase):

    def test_string_chart_of_accounts(self):
        self.assertRaises(LucaError, JournalEntry, 'Test')

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
        assert len(je.chart_of_accounts) == 18

    def test_trial_balance_2(self):
        """Try out the predefined type"""
        coa = ChartOfAccounts('Test')
        coa.add_dict({81: 'Extra Admin Expenses'})
        tb = TrialBalance(coa)
        tb.add_dict({12:50, 31:-100, 81:50})
        assert len(tb) == 3
        assert tb.is_valid()
        print(tb.profit_and_loss)
        assert tb.profit_and_loss == p(50)
        tb_closed = tb.close_period()
        assert tb[32] == p(50)

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
        assert len(je2.chart_of_accounts) == 18
        assert je2[1200]  == p(200)

    def test_trial_balance_get(self):
        """Try out the predefined type"""
        coa = ChartOfAccounts('Test')
        coa.add_dict({81: 'Extra Admin Expenses'})
        tb = TrialBalance(coa)
        tb.add_dict({12:50, 31:-100, 81:50})
        assert len(tb) == 3
        assert tb.is_valid()
        # Test direct access
        assert tb[12] == p(50)
        # Test using a string instead of an integer
        assert tb['32'] == p(50)
        assert tb['0032'] == p(50)
        # Test list access
        assert tb[[12, 31]] == p(-50)

