import datetime as dt
import unittest

import luca

class PeriodReport(unittest.TestCase):

    def test_yearstart(self):
        rep = luca.PeriodReport(dt.datetime(2015, 1, 1), "test_historic_trial_balances00.db")
        self.assertEqual(rep.datestring, 'Jan 15')
        self.assertEqual(rep.prev_datestring, 'Jan 14')
        self.assertEqual(rep.year_start_string, 'Jan 14')
        self.assertEqual(len(rep.df_list), 4)
        self.assertEqual(len(rep.df_list[0]), 40)
        self.assertEqual(len(rep.df_list[1]), 40)
        self.assertEqual(len(rep.df_list[2]), 40)
        self.assertEqual(len(rep.df_list[3]), 40)

    def test_prev_yearstart(self):
        rep = luca.PeriodReport(dt.datetime(2014, 12, 1), "test_historic_trial_balances00.db")
        self.assertEqual(rep.datestring, 'Dec 14')
        self.assertEqual(rep.prev_datestring, 'Dec 13')
        self.assertEqual(rep.year_start_string, 'Jan 14')
        self.assertEqual(len(rep.df_list), 4)

    def test_leap_year_start(self):
        rep = luca.PeriodReport(dt.datetime(2016, 2, 29), "test_historic_trial_balances00.db")
        self.assertEqual(rep.datestring, 'Feb 16')
        self.assertEqual(rep.prev_datestring, 'Feb 15')
        self.assertEqual(rep.year_start_string, 'Jan 16')
        self.assertEqual(len(rep.df_list), 4)




if __name__ == '__main__':
    unittest.main()
