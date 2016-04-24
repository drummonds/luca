import datetime as dt
import os
import pandas as pd
import sys
from xlsxwriter.utility import xl_rowcol_to_cell

from .excel_report2 import ExcelReportPage
from .utils import p


class FYCoverPage(ExcelReportPage):

    @property
    def sheetname(self):
        return 'P&L '+ self.rep.datestring

    def format_page(self, excel_base, worksheet):
        ws = worksheet
        xlb = excel_base
        rep = xlb.rep
        coa = rep.coa
        #Todo move this to Chart of Accounts data
        rep.company_name = 'Drummonds.net Limited'
        rep.company_number = '05759862'
        rep.year_end_date = '31 March 2015'
        # Nominal code info columns
        for range, width in [('A:A', 5.5), ('B:B', 46), ('C:D', 10), ('E:E', 6), ('F:G', 10)]:
            ws.set_column(range, width)
        ws.write('G1', 'Registration number: {}'.format(xlb.rep.company_number), xlb.bold_left_italic_fmt)
        ws.write('C10', '{}'.format(xlb.rep.company_name), xlb.bold_fmt)
        ws.write('C11', 'Annual Rep Financial Statements', xlb.fmt)
        ws.write('C12', 'for the Year Ended {}'.format(xlb.rep.year_end_date), xlb.fmt)
        xlb.format_print_area(ws, 'COVER SHEET')
