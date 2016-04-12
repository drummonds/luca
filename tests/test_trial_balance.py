import datetime as dt
import pandas as pd
import unittest

from h3_yearend import p

from luca import TrialBalance


class TestTB(unittest.TestCase):

    def test_empty_trial_balance(self):
        tb = TrialBalance('AAA')
        assert len(tb.series) == 0
        assert len(tb) == 0
        assert tb.is_valid()
        assert tb.coa == 'AAA'

    def test_trial_balance_1(self):
        tb = TrialBalance('SLF-MA')
        tb.add_dict({1200:100, 2120:p(-100)})
        assert len(tb.series) == 2
        assert len(tb) == 0
        assert tb.is_valid()
