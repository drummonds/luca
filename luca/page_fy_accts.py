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
        xlb.col_list=(3, 4, )  # Two column report
        xlb.write_merged_header(ws, coa.company_name, cols='B:E')
        xlb.write_merged_header(ws, 'Profit and Loss Account for the Year Ended {}'.format(rep.full_datestring),
                                cols='B:E')
        xlb.write_row(ws, rep.datestrings)
        ws.write('C4', 'Note', xlb.bold_fmt)
        xlb.write_row(ws, ['£']*2)
        xlb.line_number = 5
        turnover = -xlb.sum(coa.sales)
        xlb.write_fy_row(ws, turnover, 'Turnover')
        cost_of_sales = xlb.sum(coa.material_costs)
        xlb.write_fy_row(ws, cost_of_sales, 'Cost of sales')
        gross_profit = [x[0]-x[1] for x in zip(turnover, cost_of_sales)]
        xlb.write_fy_row(ws, gross_profit, 'Gross profit')
        admin_expenses = xlb.sum(coa.variable_costs
                                 + coa.fixed_production_costs
                                 + coa.admin_costs )
        xlb.write_fy_row(ws, admin_expenses, 'Administrative expenses')
        operating_profit = [x[0]-x[1] for x in zip(gross_profit, admin_expenses)]
        xlb.write_fy_row(ws, operating_profit, 'Operating (loss)/profit')
        xlb.write_fy_row(ws, operating_profit, '(Loss)/profit on ordinary activities before taxation')
        ws.write('B12', 'Tax on (loss)/profit on ordinary activities', xlb.left_fmt)
        ws.write('B13', '(Loss)/profit for the financial year', xlb.left_fmt)

        ws.write('C38', 'The notes on pages 6 to 8 form an integral part of these financial statemeents.', xlb.fmt)
        xlb.format_print_area(ws, 'PROFIT & LOSS ACCOUNT')


