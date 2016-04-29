import unittest

from luca import CoreSlumberfleece


class TestCore(unittest.TestCase):

    def test_convert_trial_balance(self):
        # Data to convert from
        cs = CoreSlumberfleece(file_name="test_historic_trial_balances00.db")
        periods = cs.periods()
        print(periods)
        assert 'YTD-JAN-15' in periods
