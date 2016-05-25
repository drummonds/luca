import unittest

from luca import ChartOfAccounts
from luca import chart_of_accounts_from_db, LucaError


class TestChartOfAccounts(unittest.TestCase):

    def test_simple_chart_off_accounts(self):
        coa = ChartOfAccounts('Test')
        # TODO this is now a rubbish test as Test has a predefined chart of accounts rather than blank
        coa.add_dict({2120: 'Share Capital', 1200: 'Bank'})
        assert coa[1200] == 'Bank'
        assert coa[2120] == 'Share Capital'
        assert set(coa.names).intersection({'Bank', 'Share Capital'}) ==  {'Bank', 'Share Capital'}

    def test_db_chart_of_accounts(self):
        chart_of_accounts_name = 'SLF-MA'
        with chart_of_accounts_from_db('test_historic_trial_balances00.db') as coa_s:
            coa = coa_s.get_chart_of_account(chart_of_accounts_name)
        print(coa.names)
        assert 'Bank Current Account' in coa.names
        print(coa.nominal_codes)
        assert 1200 in coa.nominal_codes


    def test_virtual_nominal_codes(self):
        # Note that having virtual codes inside ranges could be problematical
        # TODO add extra depth to virtual nominal codes
        coa = ChartOfAccounts('Test')
        coa.add_virtual_nominal_code(37, [31], overwrite=False)
        coa.add_virtual_nominal_code(38, [], overwrite=True)  # Test adding blank
        coa.add_virtual_nominal_code(38, [32], overwrite=True)
        self.assertRaises(LucaError, coa.add_virtual_nominal_code, 37, [33], overwrite=False)

        #asserterror coa.add_virtual_nominal_code(81, 'Other admin', overwrite=False)