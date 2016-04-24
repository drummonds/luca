import datetime as dt
import os
import pandas as pd
import sys
from xlsxwriter.utility import xl_rowcol_to_cell

from .utils import p


class ExcelReportPage:

    def __init__(self, report_data):
        self.rep = report_data  ## report_data

    @property
    def sheetname(self):
        return 'Blank'

    def format_page(self, excel_base, worksheet):
        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        # Demo header
        ws.set_column('B:B', 30)
        xlb.add_standard_formats()
        xlb.line_number=0
        cell_location = xl_rowcol_to_cell(2, 2)
        ws.write(cell_location, 'Blank Page', self.bold_fmt)


class ExcelManagementReport2():
    """This is a generalised managment report for produce proift and loss statements as well as balance sheets."""

    def report_filename(self):
        return '{} {}.xlsx'.format(self.file_name, dt.datetime.today().strftime('%Y-%m-%dT%H_%M_%S'))

    def __init__(self, file_name = 'Management Report'):
        # Setup
        self.col_list=(2, 3, 5, 6)
        self.file_name = file_name

    def write_row(self, ws, entries):
        # Add titles
        for i,column in enumerate(self.col_list):
            # Determine where we will place the formula
            cell_location = xl_rowcol_to_cell(self.line_number, column)
            ws.write(cell_location, entries[i], self.bold_fmt)
        self.line_number += 1

    def get_value(self, tb, nominal_code, sign):
        """This gets a reporting value.  EG Liabilities and Assets will be both shown as positive numbers"""
        # TODO move this code into the TrialBalance data
        try:
            value = tb[nominal_code] * sign
        except (KeyError, IndexError, TypeError):
            # There is a name value so presumably some data but just none in this series
            value = 0
        return value

    def all_values_zero(self, nominal_code, sign):
        all_zero = True
        for tb in self.rep.trial_balances:
            if self.get_value(tb, nominal_code, sign) != p(0):
                all_zero = False
        return all_zero

    def should_print_line(self, nominal_code, sign):
        should_print = True
        if nominal_code in self.rep.chart_of_accounts.optional_accounts and self.all_values_zero(nominal_code, sign):
            should_print = False
        return should_print

    def write_block(self, ws, sum_list, acct_list, title, sign = 1):
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
        # The acct_list is the simple list of account nominal codes that are to be included in this block
        for nc in acct_list:
            # If there no row then ignore error
            try:
                if self.should_print_line(nc, sign):
                    name = self.rep.chart_of_accounts[nc]
                    cell_location = xl_rowcol_to_cell(self.line_number, 0)
                    ws.write(cell_location, nc, self.nc_fmt)
                    cell_location = xl_rowcol_to_cell(self.line_number, 1)
                    ws.write(cell_location, name, fmt_left)
                    for j, tb in enumerate(self.rep.trial_balances):
                        cell_location = xl_rowcol_to_cell(self.line_number, self.col_list[j])
                        value=self.get_value(tb, nc, sign)
                        ws.write(cell_location, value, fmt)
                        block_sum[j] += p(value)
                    self.line_number += 1
            except KeyError:
                # This is where there is no data in the name
                print("Missing data for account {}. Error {}".format(nc, sys.exc_info()))
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
        block_sum = [p(0)] * 2
        single_row = len(acct_list) == 1 and not sub_total
        if single_row:  # Single row so no summary row
            fmt = self.bold_fmt
            fmt_left = self.bold_left_fmt
            # Write title
            ws.write(xl_rowcol_to_cell(self.line_number, 0), acct_list[0], self.nc_fmt)
            ws.write(xl_rowcol_to_cell(self.line_number, 1), title, self.bold_left_fmt)
            for col, index in ((3, 0,), (6, 1,)):
                tb = self.rep.trial_balances[index]
                # Write values
                value = self.get_value(tb, acct_list[0], sign)
                ws.write(xl_rowcol_to_cell(self.line_number, col + indent),
                         value, self.bold_left_fmt)
                block_sum[index] += p(value)
            self.line_number += 1
        else:
            # Write title
            ws.write(xl_rowcol_to_cell(self.line_number, 1), title, self.bold_left_fmt)
            self.line_number += 1  # Blank line seperator
            # Set up the formats
            fmt = self.fmt
            fmt_left = self.left_fmt
            # The acct_list is the simple list of account nominal codes that are to be included in this block
            for nc in acct_list:
                # If there no row then ignore error
                try:
                    name = self.rep.chart_of_accounts[nc]
                    ws.write(xl_rowcol_to_cell(self.line_number, 0), nc, self.nc_fmt)
                    ws.write(xl_rowcol_to_cell(self.line_number, 1), name, fmt_left)
                    for col, index in ((2, 0,), (5, 1,)):
                        tb = self.rep.trial_balances[index]
                        # Write values
                        value = self.get_value(tb, nc, sign)
                        ws.write(xl_rowcol_to_cell(self.line_number, col), value, fmt)
                        block_sum[index] += p(value)
                    self.line_number += 1
                except KeyError:
                    # This is where there is no data in the name
                    print("Missing data for account {}".format(nc))
            # Add a sub total line if required
            self.write_bs_sum(ws, block_sum, 'TOTAL ' + title, indent=indent)
        # Aggregate the local sum into the bigger sum
        for i, e in enumerate(block_sum):
            sum_list[i] += e
        self.line_number += 1  # Blank line seperator

    def write_sum(self, ws, sum_list, title):
        cell_location = xl_rowcol_to_cell(self.line_number, 1)
        ws.write(cell_location, title, self.bold_left_fmt)
        for i, tb in enumerate(self.rep.trial_balances):
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

    def add_standard_formats(self):
        wb = self.workbook  # Done for each workbook
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

    def write_merged_header_row(self, ws, header_list):
        # Add titles
        fmt = self.wb.add_format({**self.base_format_dictionary, **{'underline': 1, 'bold': True}})
        self.line_number += 1
        ws.merge_range('C{0}:D{0}'.format(self.line_number), header_list[0], fmt)
        ws.merge_range('F{0}:G{0}'.format(self.line_number), header_list[1], fmt)

    def open(self):
        fn = os.getcwd() + '\\' + self.report_filename()
        if os.path.isfile(fn):
            os.remove(fn)
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        self.writer = pd.ExcelWriter(fn, engine='xlsxwriter')
        # Get the xlsxwriter objects from the dataframe writer object.
        self.workbook  = self.writer.book

    def close(self):
        self.writer.save()

    def add(self, new_page):
        worksheet = self.workbook.add_worksheet(new_page.sheetname)
        self.add_standard_formats()
        self.line_number=0
        new_page.format_page(self, worksheet)
