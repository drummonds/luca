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
        xlb.format_print_area(ws, 'COVER SHEET', hide_gridlines = True)


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
        xlb.line_number = 12
        xlb.format_print_area(ws, 'COVER SHEET', hide_gridlines = True)


class FYDirectorsReport(ExcelReportPage):

    @property
    def sheetname(self):
        return 'DirRep ' + self.rep.datestring

    def format_page(self, excel_base, worksheet):
        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        # Nominal code info columns
        for range, width in [('A:A', 100)]:
            ws.set_column(range, width)
        for location, text in [
            ('A1', coa.company_name),
            ('A3', 'Director'' Report for the Year Ended {}'.format(rep.full_datestring)),
            ]:
            ws.write(location, text, xlb.title_fmt)
        for location, text in [
            ('A4', 'The director presents his report and the unaudited financial statements for the year ended {}.'.format(rep.full_datestring)),
            ('A7', 'The direcotr who held office during the year was as follows:'),
            ('A8', 'Dr Humphrey Drummond'),
            ('A11', 'This report has been prepared in accordance with the smal companies regime under the Companies Act 2006.'),
            ('A14', 'Approved by the board on the 30 April 2016 and signed on its behalf by.'),
            ('A20', '...............................................................'),
            ('A21', 'Dr Humphrey Drummond'),
            ('A22', 'Director'),
            ]:
            ws.write(location, text, xlb.left_fmt)
        for location, text in [
            ('A6', 'Director of the Company'),
            ('A10', 'Small Company Provision'),
            ]:
            ws.write(location, text, xlb.bold_left_fmt)
        xlb.format_print_area(ws, 'Director''s Report', hide_gridlines=True)


class FYPnLPage(ExcelReportPage):

    @property
    def sheetname(self):
        return '{}FY P&L '.format(self.sheetname_prefix) + self.rep.datestring

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
        turnover = xlb.sum(coa.sales, sign = -1)
        xlb.write_fy_row(ws, turnover, 'Turnover', row_height=22)
        cost_of_sales = xlb.sum(coa.material_costs)
        xlb.write_fy_row(ws, cost_of_sales, 'Cost of sales', cell_format={'bottom': '1'}, row_height=22)
        gross_profit = [x[0]-x[1] for x in zip(turnover, cost_of_sales)]
        xlb.write_fy_row(ws, gross_profit, 'Gross profit')
        admin_expenses = xlb.sum(coa.variable_costs
                                 + coa.fixed_production_costs
                                 + coa.admin_costs,  sign = -1)
        xlb.write_fy_row(ws, admin_expenses, 'Administrative expenses', cell_format={'bottom': '1'}, row_height=22)
        operating_profit = [x[0]+x[1] for x in zip(gross_profit, admin_expenses)]
        xlb.write_fy_row(ws, operating_profit, 'Operating (loss)/profit', cell_format={'bottom': '1'}, row_height=22)
        xlb.write_fy_row(ws, operating_profit, '(Loss)/profit on ordinary activities before taxation')
        corporation_tax = xlb.sum(coa.year_corporation_tax)
        xlb.write_fy_row(ws, corporation_tax, 'Tax on (loss)/profit on ordinary activities',
                         cell_format={'bottom': '1'}, row_height=22)
        profit_or_loss= [x[0]+x[1] for x in zip(operating_profit, corporation_tax)]
        xlb.write_fy_row(ws, profit_or_loss, '(Loss)/profit for the financial year', cell_format={'bottom': '6'},
                         row_height = 22)
        ws.write('C38', 'The notes on pages 6 to 8 form an integral part of these financial statemeents.', xlb.fmt)
        xlb.line_number = 39
        xlb.format_print_area(ws, 'PROFIT & LOSS ACCOUNT', hide_gridlines = True)


class FYNotes(ExcelReportPage):

    @property
    def sheetname(self):
        return '{}Notes '.format(self.sheetname_prefix) + self.rep.datestring

    def format_page(self, excel_base, worksheet):
        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        # Nominal code info columns
        for range, width in [('A:A', 100)]:
            ws.set_column(range, width)
        for location, text in [
            ('A1', coa.company_name),
            ('A3', 'Notes to the Financial Statements for the Year Ended {}'.format(rep.full_datestring)),
            ]:
            ws.write(location, text, xlb.title_fmt)
        for location, text in [
            ('A9', """The financial statements have been prepared under the historical cost convention and in accordance
            with the Financial Report Standard for Smaller Entities (Effective April 2008)"""),
            ]:
            ws.write(location, text, xlb.left_fmt)
        for location, text in [
            ('A6', 'Accounting Policies'),
            ('A8', 'Basis of Preperation'),
            ]:
            ws.write(location, text, xlb.bold_left_fmt)
        xlb.format_print_area(ws, 'Director''s Report', hide_gridlines=True)


