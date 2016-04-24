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
        return 'Cover '+ self.rep.datestring

    def format_page(self, excel_base, worksheet):
        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        # Nominal code info columns
        for range, width in [('A:A', 5.5), ('B:B', 46), ('C:D', 10), ('E:E', 6), ('F:G', 10)]:
            ws.set_column(range, width)
        ws.write('G1', 'Registration number: {}'.format(coa.company_number), xlb.bold_left_italic_fmt)
        ws.write('C10', '{}'.format(coa.company_name), xlb.bold_fmt)
        ws.write('C11', 'Annual Report and Unaudited Financial Statements', xlb.fmt)
        ws.write('C12', 'for the Year Ended {}'.format(rep.full_datestring), xlb.fmt)
        xlb.format_print_area(ws, 'COVER SHEET')


class FYPnLPage(ExcelReportPage):

    @property
    def sheetname(self):
        return 'FY P&L '+ self.rep.datestring

    def format_page(self, excel_base, worksheet):
        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        # Nominal code info columns
        for range, width in [('B:B', 40),  # Description
                             ('C:C', 10),  # Note
                             ('D:E', 12),]:  # Dates
            ws.set_column(range, width)
        xlb.col_list=(4, 5, )  # Two column report
        xlb.write_merged_header(ws, coa.company_name, col_start='B', col_end='E')
        xlb.write_merged_header(ws, 'Profit and Loss Acocunt for the Year Ended {}'.format(rep.full_datestring), col_start='B', col_end='E')
        xlb.write_row(ws, rep.datestrings)
        ws.write('C5', 'Note', xlb.bold_fmt)
        xlb.write_row(ws, ['£']*2)
        ws.write('B6', 'Turnover', xlb.bold_fmt)
        ws.write('B7', 'Cost of sales', xlb.bold_fmt)
        ws.write('B8', 'Gross profit', xlb.bold_fmt)
        ws.write('B9', 'Administrative expenses', xlb.bold_fmt)
        ws.write('B10', 'Operating (loss)/profit', xlb.bold_fmt)
        ws.write('B11', '(Loss)/profit on ordinary activities before taxation', xlb.bold_fmt)
        ws.write('B12', 'Tax on (loss)/orifut on ordinary activities', xlb.bold_fmt)
        ws.write('B13', '(Loss)/profit for the financial year', xlb.bold_fmt)

        ws.write('C10', 'The notes on pages 6 to 8 form an integral part of these financial statemeents.', xlb.fmt)
        xlb.format_print_area(ws, 'PROFIT & LOSS ACCOUNT')


