import calendar
from dateutil.relativedelta import relativedelta
import pandas as pd
import sqlite3

from .utils import p
from .journal_entry import TrialBalance
from .journal_sqlite import journal_from_db
from .coa_sqlite import chart_of_accounts_from_db


class PeriodReport2:
    """This holds the trial balance data for a single report. It also describes the periods over which the data is
being collected.  This collects the data from the database and stores it as TrialBalance data.
All the data will be for a single chart of accounts.
There will be a period data.  There may be a prior_year period which allows year to year comparison.
This might be an additional period.  So the first might be MTD and the second YTD.
    P&L and Balance sheet data
TODO remove the coa spec which should come from the database
TODO the duration of the period should also come from the database"""

    def __init__(self, dbname, coa, period_date, period_1, period_1_prior='', period_2='', period_2_prior='',
                 prior_period_date=None, year_start_date=None):
        self.period_date = period_date
        if prior_period_date == None:
            self.prior_period_date = period_date - relativedelta(years=1)
        else:
            self.prior_period_date - prior_period_date
        self.year_start_date = year_start_date
        self._coa = coa
        self.period_names = [period_1, period_1_prior, period_2, period_2_prior]
        # Get data from historic trial balance database and store as TrialBalances
        self.trial_balances = [None]*len(self.period_names)
        with journal_from_db(dbname, coa, journal_entry_class=TrialBalance) as js:
            for i, name in enumerate(self.period_names):
                if name != '':
                    self.trial_balances[i] = js.get_entry(name)  # MTD-FEB-15 or FY-2014

    @property
    def datestring(self, seperator=' '):
        return self.period_date.strftime('%b{}%y'.format(seperator))

    @property
    def long_datestring(self, seperator=' '):
        return self.period_date.strftime('%B{}%y'.format(seperator))

    @property
    def full_datestring(self):
        return self.period_date.strftime('%d %B %Y')

    @property
    def prev_datestring(self, seperator=' '):
        if self.prior_period_date:
            return self.prior_period_date.strftime('%b{}%y'.format(seperator))
        else:
            return 'NoDate'

    @property
    def datestrings(self):
        return [self.datestring, self.prev_datestring, self.datestring, self.prev_datestring]

    @property
    def year_start_string(self, seperator=' '):
        if self.year_start_date:
            return self.year_start_date.strftime('%b{}%y'.format(seperator))
        else:
            return 'NoDate'

    @property
    def coa(self):
        return self._coa

    @property
    def chart_of_accounts(self):
        return self.coa

    @property
    def company_name(self):
        try:
            return self.coa.company_name
        except AtributeError:
            return ''