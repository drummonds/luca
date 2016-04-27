"""This is some code to help load chart of account entries from a standardised
SQLITE database.  THis can be useful for storing trial balances or any
set of accounts."""
from contextlib import contextmanager
import pandas as pd
import sqlite3

from .utils import LucaError
from .chart_of_accounts import ChartOfAccounts


class ChartOfAccountsSqlite:

    def __init__(self, dbname):
        self.dbname = dbname
        # TODO check that there actually is a database and not creating one in error
        self.conn = sqlite3.connect(self.dbname)

    def close(self):
        self.conn.close()

    def get_chart_of_account(self, chart_of_account_name):
        coa = ChartOfAccounts(chart_of_account_name)
        sql = "SELECT code as Code, name as NC_Name, category as Category  FROM chart_of_accounts WHERE chart = '{}'".\
            format(chart_of_account_name)
        df = pd.read_sql(sql, self.conn, index_col='Code')
        if len(df) != 0:
            for index, row in df.iterrows():
                coa.append(index, row['NC_Name'], row['Category'])
            return coa
        else:  # Prevents error of getting nothing back because you have got the period name wrong
            raise LucaError('Getting Chart of Account entries from db {} for  () but no data'.format(self.dbname, period))


@contextmanager
def chart_of_accounts_from_db(dbname):
    coa_s = ChartOfAccountsSqlite(dbname)
    try:
        yield coa_s
    finally:
        coa_s.close()

