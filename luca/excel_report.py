import datetime as dt
import os
import pandas as pd
from xlsxwriter.utility import xl_rowcol_to_cell

from h3_yearend import p

class ExcelManagementReport():

    def report_filename(self):
        return 'Management Report {}.xlsx'.format(dt.datetime.today().strftime('%Y-%m-%dT%H_%M_%S'))

    def __init__(self):
        # Setup
        self.col_list=(2, 3, 5, 6)

    def write_row(self, ws, entries):
        # Add titles
        for i,column in enumerate(self.col_list):
            # Determine where we will place the formula
            cell_location = xl_rowcol_to_cell(self.line_number, column)
            ws.write(cell_location, entries[i], self.bold_fmt)
        self.line_number += 1

    def write_block(self, ws, sum_list, acct_list, title, sign = 1):

        def get_value(df, nominal_code):
            try:
                value=df.ix[nominal_code].TB * sign
            except (KeyError, IndexError) as e:
                # There is a name value so presumably some data but just none in this series
                value=0
            return value

        def all_values_zero(nominal_code):
            all_zero = True
            for df in self.rep.df_list:
                if p(get_value(df, nominal_code)) != p(0):
                    all_zero = False
            return all_zero


        def should_print_line(nominal_code):
            should_print = True
            if nominal_code in (5001, ) and all_values_zero(nominal_code):
                should_print = False
            return should_print

        block_sum = [p(0)] * 4
        # TODO The account list may have entries for which there is no data.  Under these circumstances
        # the aim is to leave out those columns in the reporting.
        # This will depend on how the trial balance is shown with no data.
        if len(acct_list) == 1: # Single row so no summary row
            fmt = self.bold_fmt
            fmt_left = self.bold_left_fmt
        else:
            fmt = self.fmt
            fmt_left = self.left_fmt

        for i, a in enumerate(acct_list):
            # If there no row then ignore error
            try:
                if should_print_line(a):
                    name = self.rep.nc_names.ix[acct_list[i]].NC_Name #Error will show up
                    cell_location = xl_rowcol_to_cell(self.line_number, 0)
                    ws.write(cell_location, acct_list[i], self.nc_fmt)
                    cell_location = xl_rowcol_to_cell(self.line_number, 1)
                    ws.write(cell_location, name, fmt_left)
                    for j, df in enumerate(self.rep.df_list):
                        cell_location = xl_rowcol_to_cell(self.line_number, self.col_list[j])
                        value=get_value(df, a)
                        ws.write(cell_location, value, fmt)
                        block_sum[j] += p(value)
                    self.line_number += 1
            except KeyError:
                # This is where there is no data in the name
                print("Missing data for account {}".format(acct_list[i]))
        # Add a sub total line if required
        if len(acct_list) != 1:
            cell_location = xl_rowcol_to_cell(self.line_number, 1)
            ws.write(cell_location, title, self.bold_left_fmt)
            for i,c in enumerate(self.col_list):
                cell_location = xl_rowcol_to_cell(self.line_number, c)
                ws.write(cell_location, block_sum[i], self.bold_fmt)
            self.line_number += 1
        # Aggregate the local sum into the bigger sum
        for i,e in enumerate(block_sum):
            sum_list[i]+=e
        self.line_number += 1  # Blank line seperator

    def write_bs_block(self, ws, sum_list, acct_list, title, sign=1, sub_total=False, indent=0):

        def get_value(df, nominal_code):
            if int(nominal_code) == 2126:
                value = -p(df[df.index > 3000].sum()[0])  # Profit and loss current year
            else:
                try:
                    value = df.ix[nominal_code].TB * sign
                except (KeyError, IndexError) as e:
                    # There is a name value so presumably some data but just none in this series
                    value = 0
            return value

        def all_values_zero(nominal_code):
            all_zero = True
            for df in self.rep.df_list:
                if p(get_value(df, nominal_code)) != p(0):
                    all_zero = False
            return all_zero

        block_sum = [p(0)] * 2
        single_row = len(acct_list) == 1 and not sub_total
        if single_row:  # Single row so no summary row
            fmt = self.bold_fmt
            fmt_left = self.bold_left_fmt
            # Write title
            ws.write(xl_rowcol_to_cell(self.line_number, 0), acct_list[0], self.nc_fmt)
            ws.write(xl_rowcol_to_cell(self.line_number, 1), title, self.bold_left_fmt)
            for df, col, index in ((self.rep.period_ytd, 3, 0,), (self.rep.prior_ytd, 6, 1,)):
                # Write values
                value = get_value(df, acct_list[0])
                ws.write(xl_rowcol_to_cell(self.line_number, col + indent),
                         value, self.bold_left_fmt)
                block_sum[index] += p(value)
            self.line_number += 1
        else:
            # Write title
            ws.write(xl_rowcol_to_cell(self.line_number, 1), title, self.bold_left_fmt)
            self.line_number += 1  # Blank line seperator
            fmt = self.fmt
            fmt_left = self.left_fmt
            for i, a in enumerate(acct_list):
                # If there no row then ignore error
                try:
                    name = self.rep.nc_names.ix[acct_list[i]].NC_Name  # Error will show up
                    ws.write(xl_rowcol_to_cell(self.line_number, 0), acct_list[i], self.nc_fmt)
                    ws.write(xl_rowcol_to_cell(self.line_number, 1), name, fmt_left)
                    for df, col, index in ((self.rep.period_ytd, 2, 0,), (self.rep.prior_ytd, 5, 1,)):
                        # Write values
                        value = get_value(df, a)
                        ws.write(xl_rowcol_to_cell(self.line_number, col), value, fmt)
                        block_sum[index] += p(value)
                    self.line_number += 1
                except KeyError:
                    # This is where there is no data in the name
                    print("Missing data for account {}".format(acct_list[i]))
            # Add a sub total line if required
            self.write_bs_sum(ws, block_sum, 'TOTAL ' + title, indent=indent)
        # Aggregate the local sum into the bigger sum
        for i, e in enumerate(block_sum):
            sum_list[i] += e
        self.line_number += 1  # Blank line seperator

    def write_sum(self, ws, sum_list, title):
        cell_location = xl_rowcol_to_cell(self.line_number, 1)
        ws.write(cell_location, title, self.bold_left_fmt)
        for i, df in enumerate(self.rep.df_list):
            cell_location = xl_rowcol_to_cell(self.line_number, self.col_list[i])
            ws.write(cell_location, sum_list[i], self.bold_fmt)
        self.line_number += 2

    def write_bs_sum(self, ws, sum_list, title, gap = 1, indent=0):
        # Write title
        ws.write(xl_rowcol_to_cell(self.line_number, 1), title, self.bold_left_fmt)
        # Write sums
        ws.write(xl_rowcol_to_cell(self.line_number, 3+indent), sum_list[0], self.bold_left_fmt)
        ws.write(xl_rowcol_to_cell(self.line_number, 6+indent), sum_list[1], self.bold_left_fmt)
        self.line_number += gap

    def add_standard_formats(self, wb):
        # Total formatting
        fmt = {'align': 'center', 'font_name': 'Arial', 'font_size': 10,
               'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"_);_(@_)'}
        self.base_format_dictionary = fmt
        self.fmt = wb.add_format(fmt)
        self.nc_fmt = wb.add_format({**fmt, **{'num_format': '0'}})
        self.left_fmt = wb.add_format({**fmt, **{'align': 'left'}})
        self.bold_fmt = wb.add_format({**fmt, **{'bold': True}})
        self.bold_left_fmt = wb.add_format({**fmt, **{'align': 'left', 'bold': True}})
        self.bold_left_italic_fmt = wb.add_format({**fmt, **{'align': 'left', 'bold': True, 'italic': True}})

    def format_print_area(self, ws, title):
        # Format for printing
        ws.print_area(0, 0, self.line_number, 6)
        header = '&LSLUMBERFLEECE' + '&C{}'.format(title) + '&R{}'.format(self.rep.long_datestring)
        footer = '&L&F' + '&R&D: &T'
        ws.set_header(header)
        ws.set_footer(footer)
        # Set A4 paper
        ws.set_paper(9)
        ws.hide_gridlines(0)
        ws.fit_to_pages(1, 1)  # Fit to one page

    def format_pnl(self, wb, ws):
        # Nominal code info columns
        ws.set_column('A:A', 8.5)
        # Description column
        ws.set_column('B:B', 30)
        # This years figures
        ws.set_column('C:D', 11.5)
        # Margin
        ws.set_column('E:E', 7)
        # Historic figures
        ws.set_column('F:G', 11.5)
        self.add_standard_formats(wb)
        self.line_number=0
        self.write_row(ws, [self.rep.datestring, self.rep.prev_datestring, self.rep.datestring, self.rep.prev_datestring])
        ws.write('A2', 'From End of Year ({})'.format(self.rep.year_start_string), self.bold_left_italic_fmt)
        self.write_row(ws, ['PERIOD', 'PERIOD', 'YTD', 'YTD'])
        self.write_row(ws, ['£', '£', '£', '£'])
        zero = [p(0)] * 4
        self.profit_list = zero.copy()
        self.expense_list = zero.copy()
        self.line_number=4
        self.write_block(ws, self.profit_list, [4000], 'Sales', sign=-1)
        self.write_block(ws, self.expense_list, [5000, 5001], 'Total Material Cost')
        self.write_block(ws, self.expense_list, [7000, 7100, 7103, 7102, 7105, 7006], 'Variable Works Expense')
        self.write_block(ws, self.expense_list, [7200, 7202, 7204, 7206], 'Fixed Works Expenses')
        self.write_block(ws, self.expense_list, [7020, 8100, 8200, 8204, 8300, 7906, 8310, 8400, 8402, 8405, 8201,
                                                8433, 8408, 8410, 8414, 8420, 8424, 8426, 8430, 8435, 8440], 'Admin Expenses')
        self.write_block(ws, self.expense_list, [4905, 6100, 6200, 6201, 4009], 'Selling Expenses')
        self.write_sum(ws, self.expense_list, 'TOTAL EXPENSES')
        # Calculate profit and Loss
        self.profit_loss = [0, 0, 0, 0]
        for i,e in enumerate(self.profit_list):
            self.profit_loss[i]+=e
        for i,e in enumerate(self.expense_list):
            self.profit_loss[i]-=e
        self.write_sum(ws, self.profit_loss, 'PROFIT/(LOSS)')
        self.format_print_area(ws, 'PROFIT & LOSS ACCOUNT')

    def write_merged_header_row(self, wb, ws, header_list):
        # Add titles
        fmt = wb.add_format({**self.base_format_dictionary, **{'underline': 1, 'bold': True}})
        self.line_number += 1
        ws.merge_range('C{0}:D{0}'.format(self.line_number), header_list[0], fmt)
        ws.merge_range('F{0}:G{0}'.format(self.line_number), header_list[1], fmt)

    def format_bs(self, wb, ws):
        # Nominal code info columns
        ws.set_column('A:A', 5.5)
        # Description column
        ws.set_column('B:B', 46)
        # This years figures
        ws.set_column('C:D', 10)
        # Margin
        ws.set_column('E:E', 6)
        # Historic figures
        ws.set_column('F:G', 10)
        self.add_standard_formats(wb)
        self.line_number = 0
        self.write_merged_header_row(wb, ws, [self.rep.datestring, self.rep.prev_datestring])
        ws.write('A2', 'From End of Year ({})'.format(self.rep.year_start_string), self.bold_left_italic_fmt)
        self.write_row(ws, ['£', '£', '£', '£'])
        zero = [p(0)] * 2
        fixed_assets = zero.copy()
        current_assets = zero.copy()
        short_term_liabilities = zero.copy()
        long_term_liabilities = zero.copy()
        net_current_assets = zero.copy()
        total_net_assets = zero.copy()
        owners_equity = zero.copy()
        self.line_number = 4
        self.write_bs_block(ws, fixed_assets, [10], 'FIXED ASSETS')
        self.write_bs_block(ws, current_assets, [1001, 1100, 1102, 1115, 1103, 2105, 2104, 1200, 1202, 1203, 1204],
                            'CURRENT ASSETS', indent=-1)
        self.write_bs_block(ws, short_term_liabilities, [2100, 2106, 2107, 2108, 2109, 2110],
                            'CREDITORS PAYABLE WITHIN 1 YEAR', sign=-1, indent=-1)
        for i in range(len(net_current_assets)):
            net_current_assets[i] = current_assets[i] - short_term_liabilities[i]
        self.write_bs_sum(ws, net_current_assets, 'NET CURRENT ASSETS', gap=2)
        self.write_bs_block(ws, long_term_liabilities, [2103], 'CREDITORS DUE AFTER MORE THAN 1 YEAR',
                            sub_total=True, sign=-1)
        # print('fixed = {}'.format(fixed_assets))
        # print('net current {}'.format(net_current_assets))
        # print('long_term_liabilities = {}'.format(long_term_liabilities))
        for i in range(len(total_net_assets)):
            total_net_assets[i] = fixed_assets[i] + net_current_assets[i] - long_term_liabilities[i]
        self.write_bs_sum(ws, total_net_assets, 'TOTAL NET ASSETS', gap = 3)
        # Owners equity side of balance sheet
        self.write_bs_block(ws, owners_equity, [2120, 2125, 2126], "SHAREHOLDERS' FUNDS", sign=-1)
        self.format_print_area(ws, 'BALANCE SHEET')

    def open(self):
        fn = os.getcwd() + '\\' + self.report_filename()
        if os.path.isfile(fn):
            os.remove(fn)
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        self.writer = pd.ExcelWriter(fn, engine='xlsxwriter')
        # Get the xlsxwriter objects from the dataframe writer object.
        self.workbook  = self.writer.book

    def add_sheet_pnl(self, rep):
        self.rep = rep
        sheetname = 'P&L '+ self.rep.datestring
        worksheet = self.workbook.add_worksheet(sheetname)
        self.format_pnl(self.workbook, worksheet)

    def add_sheet_bs(self, rep):
        self.rep = rep
        sheetname = 'BS ' + self.rep.datestring
        worksheet = self.workbook.add_worksheet(sheetname)
        self.format_bs(self.workbook, worksheet)

    def close(self):
        self.writer.save()

    def create_one_report(self, rep):
        self.open()
        self.add_sheet_pnl(rep)
        self.add_sheet_bs(rep)
        self.close()