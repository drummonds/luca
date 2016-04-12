import datetime as dt
import pandas as pd
import unittest

from luca import JournalEntry, p


class TestTB(unittest.TestCase):

    def test_empty_trial_balance(self):
        je = JournalEntry('AAA')
        assert len(je) == 0
        assert not je.is_valid()  # Is empty
        assert je.coa == 'AAA'

    def test_trial_balance_1(self):
        je = JournalEntry('SLF-MA')
        je.add_dict({1200:100, 2120:p(-100)})
        assert len(je) == 2
        assert je.is_valid()
