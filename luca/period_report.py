import calendar
import pandas as pd
import sqlite3

from .utils import p

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
        # Get data from historic trial balance database
        with sqlite3.connect(dbname) as self.con:
            self.nc_names = self.get_coa('SLF-MA')
            period_string = self.period.strftime('%b-%y').upper()
            self.period_mtd = self.get_df('{}-{}'.format(period_mtd_prefix, period_string))  # MTD-FEB15
            self.period_ytd = self.get_df('{}-{}'.format(period_ytd_prefix, period_string))  # YTD-FEB15
            prior_period_string = self.prev_period.strftime('%b-%y').upper()
            self.prior_mtd = self.get_df('{}-{}'.format(prior_mtd_prefix, prior_period_string))  # MTD-FEB14
            self.prior_ytd = self.get_df('{}-{}'.format(prior_ytd_prefix, prior_period_string))  # YTD-FEB14
        self.changed_data()

    def get_df(self, period):
        sql = "SELECT code as Code, balance as TB FROM trial_balance WHERE period = '{}'".format(period)
        df = pd.read_sql(sql, self.con, index_col='Code')
        df['TB'] = p(df['TB'])
        return df

    def get_coa(self, coa):
        sql = "SELECT code as Code, name as NC_Name, category as Category  FROM chart_of_accounts WHERE chart = '{}'".format(coa)
        return  pd.read_sql(sql, self.con, index_col='Code')

    def changed_data(self):
        self.df_list = [self.period_mtd, self.prior_mtd, self.period_ytd, self.prior_ytd]

    @property
    def datestring(self, seperator=' '):
        return self.period.strftime('%b %y')

    @property
    def long_datestring(self, seperator=' '):
        return self.period.strftime('%B %y')

    @property
    def prev_datestring(self, seperator=' '):
        return self.prev_period.strftime('%b %y')

    @property
    def year_start_string(self, seperator=' '):
        return self.year_start.strftime('%b %y')