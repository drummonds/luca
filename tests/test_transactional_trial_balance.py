import datetime as dt
import pandas as pd
import unittest

from luca import TrialBalanceConversion, p, ChartOfAccounts, chart_of_accounts_from_db
from luca import TrialBalance
from luca import CoreSlumberfleece


class TestTTB(unittest.TestCase):

    def test_convert_trial_balance(self):
        # Data to convert from
        cs = CoreSlumberfleece(file_name="test_historic_trial_balances00.db")
        coa_from = cs.sage_coa
        case_1 = TrialBalance(coa_from)
        case_1.add_dict({1200: p(100), 2120: p(-100)})
        # Converting to
        coa_to = cs.coa
        ttb_converter = cs.converter
        # Now do the conversion
        test_1 = ttb_converter.convert_trial_balance(case_1)
        self.assertEqual(case_1.sum(), p(0.0))

        self.assertEqual(type(test_1), type(TrialBalance(coa_from)))
        self.assertEqual(test_1[1200], p(100))
        self.assertEqual(test_1[10], p(0.0))


