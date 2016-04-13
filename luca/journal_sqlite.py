"""This is some code to help load journal entires from a standardised
SQLITE database.  THis can be useful for storing trial balances or any
set of accounts."""
from contextlib import contextmanager
import pandas as pd
import sqlite3

from .utils import LucaError
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
            raise LucaError('Getting Journal Entries from db {} for period () but no data'.format(self.dbname, period))


@contextmanager
def journal_from_db(dbname, coa, journal_entry_class=JournalEntry):
    js = JournalSqlite(dbname, coa, journal_entry_class)
    try:
        yield js
    finally:
        js.close()


def get_coa(self, coa):
    sql = "SELECT code as Code, name as NC_Name, category as Category  FROM chart_of_accounts WHERE chart = '{}'".format(
        coa)
    return pd.read_sql(sql, self.con, index_col='Code')
