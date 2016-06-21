import sys
from xlsxwriter.utility import xl_rowcol_to_cell

from .utils import p

from .excel_report2 import ExcelReportPage


class SLF_Mgmt_Cover(ExcelReportPage):
    """The aim of this report is to document what the pnl and reports are composed of."""

    @property
    def sheetname(self):
        return 'Cover '+ self.rep.datestring

    def format_page(self, excel_base, worksheet):
        def col(at_col):
            return xl_rowcol_to_cell(xlb.line_number, at_col)

        def title(message):
            xlb.write_merged_header(ws, message, cols='A:C', underline=0)

        def sub_title(text):
            ws.write(col(0), text, xlb.bold_left_fmt)
            xlb.line_number += 1

        def note(title, text):
            ws.write(col(1), title, xlb.fmt)
            ws.write(col(2), text, xlb.fmt)
            xlb.line_number += 1

        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        reg_fmt = xlb.workbook.add_format({**xlb.base_format_dictionary,  **{
            'bold' : True, 'italic' : True, 'align': 'right'}})
        title_fmt = xlb.workbook.add_format({**xlb.base_format_dictionary,  **{
            'bold' : True, 'font_size' : 18, 'align': 'center'}})
        # Nominal code info columns
        for range, width in [('A:A', 10), ('B:B', 15), ('C:C', 55),]:
            ws.set_column(range, width)
        title('Cover sheet for Slumberfleece Management accounts')
        note('Chart of Accounts name', str(coa.name))
        for title, name in zip(['MTD', 'MTD prior', 'YTD', 'YTD prior'], rep.period_names):
            note(title, name)
        note('Registration number', str(coa.company_number))
        xlb.format_print_area(ws, 'COVER SHEET', hide_gridlines = True)


class SLF_Mgmt_PnL(ExcelReportPage):

    @property
    def sheetname(self):
        return 'P&L ' + self.rep.datestring

    def format_page(self, excel_base, worksheet):
        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        #-----
        # Nominal code info columns
        for range, width in [('A:A', 8.5), ('B:B', 30), ('C:D', 11.5), ('E:E', 7), ('F:G', 11.5)]:
            ws.set_column(range, width)
        xlb.write_row(ws, [xlb.rep.datestring, xlb.rep.prev_datestring, xlb.rep.datestring, xlb.rep.prev_datestring])
        ws.write('A2', 'From End of Year ({})'.format(xlb.rep.year_start_string), xlb.bold_left_italic_fmt)
        xlb.write_row(ws, ['PERIOD', 'PERIOD', 'YTD', 'YTD'])
        xlb.write_row(ws, ['£', '£', '£', '£'])
        zero = [p(0)] * 4
        profit_list = zero.copy()
        expense_list = zero.copy()
        xlb.line_number=4
        xlb.write_block(ws, profit_list, [4000], 'Sales', sign=-1)
        xlb.write_block(ws, expense_list, [5000, 5001], 'Total Material Cost')
        xlb.write_block(ws, expense_list, [7000, 7100, 7103, 7102, 7105, 7006], 'Variable Works Expense')
        xlb.write_block(ws, expense_list, [7200, 7202, 7204, 7206], 'Fixed Works Expenses')
        xlb.write_block(ws, expense_list, [7020, 8100, 8200, 8204, 8300, 7906, 8310, 8400, 8402, 8405, 8201,
                                                8433, 8408, 8410, 8414, 8420, 8424, 8426, 8430, 8435, 8440], 'Admin Expenses')
        xlb.write_block(ws, expense_list, [4905, 6100, 6200, 6201, 4009], 'Selling Expenses')
        xlb.write_sum(ws, expense_list, 'TOTAL EXPENSES')
        # Calculate profit and Loss
        profit_loss = [0, 0, 0, 0]
        for i,e in enumerate(profit_list):
            profit_loss[i]+=e
        for i,e in enumerate(expense_list):
            profit_loss[i]-=e
        xlb.write_sum(ws, profit_loss, 'PROFIT/(LOSS)')
        xlb.format_print_area(ws, 'PROFIT & LOSS ACCOUNT')


class SLF_Mgmt_BS(ExcelReportPage):

    @property
    def sheetname(self):
        return 'BS ' + self.rep.datestring

    def format_page(self, excel_base, worksheet):
        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        #-----
        # Nominal code info columns
        for range, width in [('A:A', 5.5), ('B:B', 46), ('C:D', 10), ('E:E', 6), ('F:G', 10)]:
            ws.set_column(range, width)
        xlb.write_merged_header_row(ws, [xlb.rep.datestring, xlb.rep.prev_datestring])
        ws.write('A2', 'From End of Year ({})'.format(xlb.rep.year_start_string), xlb.bold_left_italic_fmt)
        xlb.write_row(ws, ['£', '£', '£', '£'])
        zero = [p(0)] * 4
        fixed_assets = zero.copy()
        current_assets = zero.copy()
        short_term_liabilities = zero.copy()
        long_term_liabilities = zero.copy()
        net_current_assets = zero.copy()
        total_net_assets = zero.copy()
        owners_equity = zero.copy()
        xlb.line_number = 4
        xlb.write_bs_block(ws, fixed_assets, [10], 'FIXED ASSETS')
        xlb.write_bs_block(ws, current_assets, [1001, 1100, 1102, 1115, 1103, 2105, 2104, 1200, 1202, 1203, 1204],
                            'CURRENT ASSETS', indent=-1)
        xlb.write_bs_block(ws, short_term_liabilities, [2100, 2106, 2107, 2108, 2109, 2110],
                            'CREDITORS PAYABLE WITHIN 1 YEAR', sign=-1, indent=-1)
        net_current_assets = [ca - stl for ca, stl in zip(current_assets, short_term_liabilities)]
        xlb.write_bs_sum(ws, net_current_assets, 'NET CURRENT ASSETS', gap=2)
        xlb.write_bs_block(ws, long_term_liabilities, [2103], 'CREDITORS DUE AFTER MORE THAN 1 YEAR',
                            sub_total=True, sign=-1)
        total_net_assets = [fa + nca - ltl for fa, nca, ltl in
                            zip(fixed_assets, net_current_assets, long_term_liabilities)]
        xlb.write_bs_sum(ws, total_net_assets, 'TOTAL NET ASSETS', gap = 3)
        # Owners equity side of balance sheet
        xlb.write_bs_block(ws, owners_equity, [2120, 2125, 2126], "SHAREHOLDERS' FUNDS", sign=-1)
        xlb.format_print_area(ws, 'BALANCE SHEET')
