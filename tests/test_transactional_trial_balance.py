import datetime as dt
import pandas as pd
import unittest

from h3_yearend import p

from luca import TransactionalTrialBalance

class TestTTB(unittest.TestCase):

    def test_convert_trial_balance(self):
        s = pd.Series([p(4.99), p(5.01), p(6), p(-16)], index=[10, 30, 1200, 2125])
        case_1 = pd.DataFrame(s, columns=['TB'])
        ttb_converter = TransactionalTrialBalance()
        test_1 = ttb_converter.convert_trial_balance(case_1)
        self.assertEqual(case_1['TB'].sum(), p(0.0))
        self.assertEqual(case_1['TB'].sum(), p(0.0))

        self.assertEqual(type(test_1), type(pd.DataFrame()))
        self.assertEqual(test_1.ix[1200][0], p(6))
        self.assertEqual(test_1.ix[10][0], p(10.0))




