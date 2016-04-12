import datetime as dt
import numpy as np
import pandas as pd
import pyodbc

from h3_yearend import p

class SageDataError(Exception):
    pass


class SageData:
    """Getting data from Sage and createing a data frame to store it in."""

    def date_convert(x):
        if x is None:
            result = np.nan
        elif type(x) is dt.date:
            result = np.datetime64(x)
        elif x.dtype == np.object:
            result = x.astype('datetime64')
        else:
            result = np.nan
        return result

    def __init__(self, year):
        if year == 2014:
            connection_string = "DSN=Slumberfleece2014;UID=h3;PWD=h3"
        elif year == 2015:
            connection_string = "DSN=Slumberfleece2015;UID=h3"
        else:
            raise SageDataError('No SAGE ODBC connection for year = {}'.format(year))
        sql= """
SELECT
    aj.TRAN_NUMBER, aj.type, aj.DATE, nl.account_ref, aj.ACCOUNT_REF as ALT_REF, aj.INV_REF, aj.DETAILS, AJ.TAX_CODE,
    aj.AMOUNT, aj.FOREIGN_AMOUNT, aj.BANK_FLAG, ah.DATE_BANK_RECONCILED
FROM
NOMINAL_LEDGER nl, AUDIT_HEADER ah
LEFT OUTER JOIN AUDIT_JOURNAL aj ON nl.ACCOUNT_REF = aj.NOMINAL_CODE
WHERE
aj.HEADER_NUMBER = ah.HEADER_NUMBER AND
aj.DATE > '2000-01-01' AND aj.DELETED_FLAG = 0
"""
        # JOIN AUDIT_HEADER ah ON aj.HEADER_NUMBER = ah.HEADER_NUMBER

        with pyodbc.connect(connection_string) as cnxn:
            self.df = df = pd.read_sql(sql, cnxn)
        if df['DATE'].dtype == np.object:
            df['DATE'] = df['DATE'].astype('datetime64')
        # Conversion of Date_Bank_Reconciled more complicated due to missing data
        df['DATE_BANK_RECONCILED'] = [SageData.date_convert(x) for x in df['DATE_BANK_RECONCILED']]
        # if sqldata['DATE_BANK_RECONCILED'].dtype == np.object:
        #    sqldata['DATE_BANK_RECONCILED'] = sqldata['DATE_BANK_RECONCILED'].astype('datetime64')
        if df['ACCOUNT_REF'].dtype != np.int:
            df['ACCOUNT_REF'] = df['ACCOUNT_REF'].astype('int')


    def transactional_trial_balance(self, start_date, end_date):
        df = self.df
        rec = df[(df['DATE'] >= start_date)
                 & (df['DATE'] <= end_date)][['ACCOUNT_REF', 'AMOUNT']]
        tb = pd.pivot_table(rec, index=["ACCOUNT_REF"], aggfunc=np.sum)
        tb1 = tb.apply(lambda x: p(x['AMOUNT']), axis=1)  # equiv to df.sum(1)
        return tb1
    
