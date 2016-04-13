"""This is some code to help load journal entires from a standardised
SQLITE database.  THis can be useful for storing trial balances or any
set of accounts."""
from contextlib import contextmanager
import pandas as pd
import sqlite3

from .journal_entry import JournalEntry


class JournalSqlite:

    def __init__(self, dbname, coa):
        self.dbname = dbname
        self.coa=coa
        self.conn = sqlite3.connect(self.dbname)

    def close(self):
        self.conn.close()

    def get_entry(self, period):
        # TODO check that there actually is period data in database
        je = JournalEntry(self.coa)
        sql = "SELECT code as Code, balance as TB FROM trial_balance WHERE period = '{}'".format(period)
        df = pd.read_sql(sql, self.conn, index_col='Code')
        # tooo if df empty
        je.add_dict(df.to_dict()['TB'])
        return je


@contextmanager
def journal_from_db(dbname, coa):
    js = JournalSqlite(dbname, coa)
    try:
        yield js
    finally:
        js.close()
