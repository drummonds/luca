import calendar
import pandas as pd
import sqlite3

from .utils import p
from .journal_entry import TrialBalance
from .journal_sqlite import journal_from_db
from .coa_sqlite import chart_of_accounts_from_db


class PeriodReport:
    """This holds the data for a single report.  This includees the historical and mtd figures as well as the
    P&L and Balance sheet data"""

    def __init__(self, period, dbname,
                 period_mtd_prefix='MTD',
                 period_ytd_prefix='YTD',
                 prior_mtd_prefix='MTD',
                 prior_ytd_prefix='YTD'):
        """Period is a datetime for which the year and month are used"""
        self.period = period
        try:
            self.prev_period = period.replace(year=period.year - 1)
            if calendar.isleap(self.prev_period.year) and self.prev_period.month == 2:
                self.prev_period = self.prev_period.replace(day = 29)
        except ValueError:  # Eg for leap year
            if self.period.month == 2 and self.period.day == 29:  # leap year
                self.prev_period = period.replace(year = period.year - 1, day = 28)
            else:
                raise
        if period.month == 1:
            self.year_start = period.replace(year = period.year - 1)
        else:
            self.year_start = period.replace(month =  1)
        # Set up the default chart of accounts
        with chart_of_accounts_from_db(dbname) as coa_s:
            coa = coa_s.get_chart_of_account('SLF-MA')
        # Get data from historic trial balance database and store as TrialBalances
        with journal_from_db(dbname, coa, journal_entry_class=TrialBalance) as js:
            period_string = self.period.strftime('%b-%y').upper()
            self.period_mtd = js.get_entry('{}-{}'.format(period_mtd_prefix, period_string))  # MTD-FEB-15
            self.period_ytd = js.get_entry('{}-{}'.format(period_ytd_prefix, period_string))  # YTD-FEB-15
            prior_period_string = self.prev_period.strftime('%b-%y').upper()
            self.prior_mtd = js.get_entry('{}-{}'.format(prior_mtd_prefix, prior_period_string))  # MTD-FEB-14
            self.prior_ytd = js.get_entry('{}-{}'.format(prior_ytd_prefix, prior_period_string))  # YTD-FEB-14
        self.changed_data()

    def changed_data(self):
        # Store a list of all the trial balances that are breing used
        self.tb_list = [self.period_mtd, self.prior_mtd, self.period_ytd, self.prior_ytd]

    @property
    def datestring(self, seperator=' '):
        return self.period.strftime('%b{}%y'.format(seperator))

    @property
    def long_datestring(self, seperator=' '):
        return self.period.strftime('%B{}%y'.format(seperator))

    @property
    def prev_datestring(self, seperator=' '):
        return self.prev_period.strftime('%b{}%y'.format(seperator))

    @property
    def year_start_string(self, seperator=' '):
        return self.year_start.strftime('%b{}%y'.format(seperator))