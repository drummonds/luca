import datetime as dt
import os
import pandas as pd
import sys
from xlsxwriter.utility import xl_rowcol_to_cell

from .excel_report2 import ExcelReportPage
from .utils import p


class ManagementPnLPage(ExcelReportPage):

    @property
    def sheetname(self):
        return 'P&L '+ self.rep.datestring

    def format_page(self, excel_base, worksheet):
        ws = worksheet
        xlb = excel_base
        rep = self.rep
        coa = rep.coa
        # Nominal code info columns
        for range, width in [('A:A', 8.5), ('B:B', 30), ('C:D', 11.5), ('E:E', 7), ('F:G', 11.5)]:
            ws.set_column(range, width)
        xlb.col_list=(2, 3, 5, 6)
        xlb.write_row(ws, rep.datastrings)
        ws.write('A2', 'From End of Year ({})'.format(self.rep.year_start_string), self.bold_left_italic_fmt)
        xlb.write_row(ws, ['PERIOD', 'PERIOD', 'YTD', 'YTD'])
        xlb.write_row(ws, ['£']*4)
        zero = [p(0)] * 4
        profit_list = zero.copy()
        expense_list = zero.copy()
        xlb.line_number=4
        xlb.write_block(ws, profit_list, coa.sales, 'Sales', sign=-1)
        xlb.write_block(ws, expense_list, coa.material_costs, coa.material_costs_name)
        xlb.write_block(ws, expense_list, coa.variable_costs, 'Variable Works Expense')
        xlb.write_block(ws, expense_list, coa.fixed_production_costs, 'Fixed Works Expenses')
        xlb.write_block(ws, expense_list, coa.admin_costs, 'Admin Expenses')
        xlb.write_block(ws, expense_list, coa.selling_costs, 'Selling Expenses')
        self.write_sum(ws, expense_list, 'TOTAL EXPENSES')
        # Calculate profit and Loss
        profit_loss = [0, 0, 0, 0]
        for i,e in enumerate(profit_list):
            profit_loss[i]+=e
        for i,e in enumerate(expense_list):
            profit_loss[i]-=e
        xlb.write_sum(ws, profit_loss, 'PROFIT/(LOSS)')
        xlb.format_print_area(ws, 'PROFIT & LOSS ACCOUNT')


class ManagementBSPage(ExcelReportPage):

    @property
    def sheetname(self):
        return 'BS '+ self.rep.datestring

    def format_page(self, excel_base, worksheet):
        ws = worksheet
        xlb = excel_base
        rep = self.rep
        coa = rep.coa
        # Nominal code info columns
        for range, width in [('A:A', 5.5), ('B:B', 46), ('C:D', 10), ('E:E', 6), ('F:G', 10)]:
            ws.set_column(range, width)
        xlb.col_list=(2, 3, 5, 6)
        xlb.add_standard_formats()
        xlb.line_number=0
        xlb.write_merged_header_row(ws, rep.datastrings)
        ws.write('A2', 'From End of Year ({})'.format(self.rep.year_start_string), self.bold_left_italic_fmt)
        self.write_row(ws, ['£']*4)
        zero = [p(0)] * 2
        fixed_assets = zero.copy()
        current_assets = zero.copy()
        short_term_liabilities = zero.copy()
        long_term_liabilities = zero.copy()
        net_current_assets = zero.copy()
        total_net_assets = zero.copy()
        owners_equity = zero.copy()
        xlb.line_number = 4
        xlb.write_bs_block(ws, fixed_assets, coa.fixed_asset, 'FIXED ASSETS')
        xlb.write_bs_block(ws, current_assets, coa.current_asset, 'CURRENT ASSETS', indent=-1)
        xlb.write_bs_block(ws, short_term_liabilities, coa.short_term_liabilities,
                        'CREDITORS PAYABLE WITHIN 1 YEAR', sign=-1, indent=-1)
        for i in range(len(net_current_assets)):
            net_current_assets[i] = current_assets[i] - short_term_liabilities[i]
        xlb.write_bs_sum(ws, net_current_assets, 'NET CURRENT ASSETS', gap=2)
        xlb.write_bs_block(ws, long_term_liabilities, coa.long_term_liabilities,
                        'CREDITORS DUE AFTER MORE THAN 1 YEAR', sub_total=True, sign=-1)
        for i in range(len(total_net_assets)):
            total_net_assets[i] = fixed_assets[i] + net_current_assets[i] - long_term_liabilities[i]
            xlb.write_bs_sum(ws, total_net_assets, 'TOTAL NET ASSETS', gap=3)
        # Owners equity side of balance sheet
        xlb.write_bs_block(ws, owners_equity, self.rep.coa.owners_equity, "SHAREHOLDERS' FUNDS", sign=-1)
        xlb.format_print_area(ws, 'BALANCE SHEET')
