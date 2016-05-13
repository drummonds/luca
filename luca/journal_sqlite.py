"""This is some code to help load journal entires from a standardised
SQLITE database.  THis can be useful for storing trial balances or any
set of accounts."""
from contextlib import contextmanager
import math
import pandas as pd
import sqlite3

from .utils import LucaError, p
from .journal_entry import JournalEntry


class JournalSqlite:

    def __init__(self, dbname, coa, journal_entry_class=JournalEntry):
        self.dbname = dbname
        self.coa=coa
        self.conn = sqlite3.connect(self.dbname)
        self.journal_entry_class=journal_entry_class

    def close(self):
        self.conn.close()

    def get_entry(self, period):
        je = self.journal_entry_class(self.coa)
        sql = "SELECT code as Code, balance as TB FROM trial_balance WHERE period = '{}'".format(period)
        df = pd.read_sql(sql, self.conn, index_col='Code')
        if len(df) != 0:
            je.add_dict(df.to_dict()['TB'])
            return je
        else:  # Prevents error of getting nothing back because you have got the period name wrong
            raise LucaError('Getting Journal Entries from db {} for period {} but no data'.format(self.dbname, period))


@contextmanager
def journal_from_db(dbname, coa, journal_entry_class=JournalEntry):
    js = JournalSqlite(dbname, coa, journal_entry_class)
    try:
        yield js
    finally:
        js.close()


class LoadDatabaseError(Exception):
    pass

class LoadDatabase():
    """Does not have the ability to create a database or chart of acconts if they don't exist."""

    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.commit()
        self.close()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def empty(self, period):
        """Check if no data for Balance sheet period is in database"""
        count=self.cursor.execute("SELECT COUNT(*) FROM trial_balance WHERE period='{}' and code < 4000".
                                  format(period)).fetchone()[0]
        return count==0

    def get_coa(self, coa):
        sql = "SELECT code as Code, name as NC_Name, category as Category  FROM chart_of_accounts WHERE chart = '{}'".\
            format(coa)
        return  pd.read_sql(sql, self.conn, index_col='Code')

    def load_tb_to_database(self, trial_balance, period, overwrite = False):
        """The chart of accounts in trial_balance defines how the name is to be laoded.
         The period is a tag that describes the data."""
        # TODO build the Period label suffix from the data in the transaction data
        trial_balance.chart_of_accounts.assert_valid_name()
        if self.empty(period) or overwrite:
            if overwrite:
                    self.cursor.execute("DELETE FROM trial_balance WHERE period = '{}'".format(period))
            coa=trial_balance.chart_of_accounts
            # TODO would be better if checked that the COA is accurate before posting the data
            for nominal_code, value in trial_balance.to_series().iteritems():
                if value == '-' or math.isnan(value):  # Not sure this check is necessary any longer
                    value = p(0)
                try:
                    sql = "INSERT INTO trial_balance (period, code, balance) VALUES ('{}', {}, {})".\
                        format(period, nominal_code, value)
                    self.cursor.execute(sql)
                except:  # Todo make more specific
                    print('Trying to insert code {} into database {} for period {} with value {}'. \
                        format(nominal_code, coa.name, period, value))

        else:
            raise LoadDatabaseError('{} already is in management report database'.format(period))

class JournalSqlite:

    def __init__(self, dbname, coa, journal_entry_class=JournalEntry):
        self.dbname = dbname
        self.coa=coa
        self.conn = sqlite3.connect(self.dbname)
        self.journal_entry_class=journal_entry_class

    def close(self):
        self.conn.close()

    def get_entry(self, period):
        je = self.journal_entry_class(self.coa)
        sql = "SELECT code as Code, balance as TB FROM trial_balance WHERE period = '{}'".format(period)
        df = pd.read_sql(sql, self.conn, index_col='Code')
        if len(df) != 0:
            je.add_dict(df.to_dict()['TB'])
            return je
        else:  # Prevents error of getting nothing back because you have got the period name wrong
            raise LucaError('Getting Journal Entries from db {} for period {} but no data'.format(self.dbname, period))


def is_period_data_available(dbname, period):
    """To test if a period is available in the database."""
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    sql = "SELECT count(*) FROM trial_balance WHERE period = '{}'".format(period)
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.close()
    return result[0]



