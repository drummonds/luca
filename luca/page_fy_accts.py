import datetime as dt
import os
import pandas as pd
import sys
from xlsxwriter.utility import xl_rowcol_to_cell

from .excel_report2 import ExcelReportPage
from .utils import p
from .metadata import version
from .tax_uk import uk_corporation_tax_rate


def _calc_block_sum(xlb, rep, acct_list, sign=1):
    "For a list of accounts calculates the sum and also if there is any data"
    block_sum = [p(0)] * 4
    has_data = False
    # The acct_list is the simple list of account nominal codes that are to be included in this block
    for nc in acct_list:
        # If there no row then ignore error
        try:
            for i, col in enumerate(xlb.col_list):
                tb = rep.trial_balances[i]
                value = xlb.get_value(tb, nc, sign)
                if p(value) != p(0):
                    has_data = True
                block_sum[i] += p(value)
        except KeyError:
            pass
    return block_sum, has_data

def _write_block(ws, xlb, rep, acct_list, title, sign=1, sum_for_one_entry = False):
    block_sum, has_data = _calc_block_sum(xlb, rep, acct_list, sign)
    if has_data:
        fmt = xlb.workbook.add_format(
            {**xlb.base_format_dictionary, **{'align': 'right'}})
        fmt_title = xlb.workbook.add_format(
            {**xlb.base_format_dictionary, **{'align': 'left', 'bold': True, 'font_size': 11}})
        fmt_left = xlb.workbook.add_format(
            {**xlb.base_format_dictionary, **{'align': 'left'}})
        fmt_underline = xlb.workbook.add_format(
            {**xlb.base_format_dictionary, **{'align': 'right', 'bottom': 1}})
        fmt_double_underline = xlb.workbook.add_format(
            {**xlb.base_format_dictionary, **{'align': 'right', 'bottom': 6}})
       # Do the title
        cell_location = xl_rowcol_to_cell(xlb.line_number, 1)
        ws.write(cell_location, title, fmt_title)
        xlb.line_number += 1
        # The acct_list is the simple list of account nominal codes that are to be included in this block
        for j, nc in enumerate(acct_list):
            # If there no row then ignore error
            try:
                name = rep.chart_of_accounts[nc]
                cell_location = xl_rowcol_to_cell(xlb.line_number, 1)
                ws.write(cell_location, name, fmt_left)
                if (j+1) == len(acct_list) and (len(acct_list) > 1):  # Last entry
                    cell_fmt = fmt_underline
                elif (j + 1) == len(acct_list) and (len(acct_list) == 1):  # Last entry
                        cell_fmt = fmt_double_underline
                else:
                    cell_fmt = fmt
                for i, col in enumerate(xlb.col_list):
                    tb = rep.trial_balances[i]
                    cell_location = xl_rowcol_to_cell(xlb.line_number, col)
                    value = xlb.get_value(tb, nc, sign)
                    ws.write(cell_location, value, cell_fmt)
                xlb.line_number += 1
            except KeyError:
                # This is where there is no data in the name
                print("Missing data for account {}. Error {}".format(nc, sys.exc_info()))
                pass
        # Add a sub total line if required
        if (len(acct_list) != 1) or (sum_for_one_entry):
            for i, c in enumerate(xlb.col_list):
                cell_location = xl_rowcol_to_cell(xlb.line_number, c)
                ws.write(cell_location, block_sum[i], fmt_double_underline)
            xlb.line_number += 1
        xlb.line_number += 1  # Blank line seperator

def _write_block_sum(ws, xlb, rep, acct_list, title, sign=1):
    block_sum = [p(0)] * 4
    fmt_title = xlb.workbook.add_format(
        {**xlb.base_format_dictionary, **{'align': 'left', 'font_size': 11}})
    fmt_double_underline = xlb.workbook.add_format(
        {**xlb.base_format_dictionary, **{'align': 'right', 'bottom': 6}})
    # Do the title
    cell_location = xl_rowcol_to_cell(xlb.line_number, 1)
    ws.write(cell_location, title, fmt_title)
    # The acct_list is the simple list of account nominal codes that are to be included in this block
    for nc in acct_list:
        # If there no row then ignore error
        try:
            for i, col in enumerate(xlb.col_list):
                tb = rep.trial_balances[i]
                value = xlb.get_value(tb, nc, sign)
                block_sum[i] += p(value)
        except KeyError:
            pass
    # write out summary
    for i, c in enumerate(xlb.col_list):
        cell_location = xl_rowcol_to_cell(xlb.line_number, c)
        ws.write(cell_location, block_sum[i], fmt_double_underline)
    xlb.line_number += 1


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
        reg_fmt = xlb.workbook.add_format({**xlb.base_format_dictionary,  **{
            'bold' : True, 'italic' : True, 'align': 'right'}})
        title_fmt = xlb.workbook.add_format({**xlb.base_format_dictionary,  **{
            'bold' : True, 'font_size' : 18, 'align': 'center'}})
        # Nominal code info columns
        for range, width in [('A:A', 5.5), ('B:B', 46), ('C:D', 10), ('E:E', 6), ('F:G', 10)]:
            ws.set_column(range, width)
        ws.write('G1', 'Registration number: {}'.format(coa.company_number), reg_fmt)
        ws.write('C10', '{}'.format(coa.company_name), title_fmt)
        ws.write('C11', 'Annual Report and Unaudited Financial Statements', xlb.fmt)
        ws.write('C12', 'for the Year Ended {}'.format(rep.full_datestring), xlb.fmt)
        xlb.format_print_area(ws, 'COVER SHEET', hide_gridlines = True,
                              show_footer = False, show_header = False)
        ws.set_footer('Page {}'.format(xlb.page_number))


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
            ('A7', 'The director who held office during the year was as follows:'),
            ('A8', 'Dr Humphrey Drummond'),
            ('A11', 'This report has been prepared in accordance with the smal companies regime under the Companies Act 2006.'),
            ('A14', 'Approved by the board on the {} and signed on its behalf by.'.format(rep.report_date_full_string)),
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
        cost_of_sales = xlb.sum(coa.material_costs, sign = -1)
        xlb.write_fy_row(ws, cost_of_sales, 'Cost of sales', cell_format={'bottom': 1}, row_height=22)
        gross_profit = [x[0]+x[1] for x in zip(turnover, cost_of_sales)]
        xlb.write_fy_row(ws, gross_profit, 'Gross profit', row_height=22)
        admin_nc = coa.variable_costs + coa.fixed_production_costs + coa.admin_costs\
            + coa.depeciation_costs + coa.amortisation_costs + coa.finance_costs
        admin_expenses = xlb.sum(admin_nc ,  sign = -1)
        xlb.write_fy_row(ws, admin_expenses, 'Administrative expenses', cell_format={'bottom': 1}, row_height=22)
        operating_profit = [x[0]+x[1] for x in zip(gross_profit, admin_expenses)]
        xlb.write_fy_row(ws, operating_profit, 'Operating (loss)/profit', note='2',
                         cell_format={'bottom': 1}, row_height=22)
        xlb.write_fy_row(ws, operating_profit, '(Loss)/profit on ordinary activities before taxation', row_height=22)
        corporation_tax = xlb.sum(coa.year_corporation_tax)
        xlb.write_fy_row(ws, corporation_tax, 'Tax on (loss)/profit on ordinary activities', note='3',
                         cell_format={'bottom': '1'}, row_height=22, sign=-1)
        profit_or_loss= [x[0]-x[1] for x in zip(operating_profit, corporation_tax)]
        xlb.write_fy_row(ws, profit_or_loss, '(Loss)/profit for the financial year', note='10',
                         cell_format={'bottom': 6}, row_height = 22)
        # Check used all nominal codes
        nc_PAT = set(coa.PAT)
        nc_calc = set(coa.sales + coa.material_costs + admin_nc + coa.year_corporation_tax)
        assert nc_PAT == nc_calc, 'PAT = {} and sum = {} diff = {}'.format(nc_PAT, nc_calc, nc_PAT ^ nc_calc)
        xlb.format_print_area(ws, 'PROFIT & LOSS ACCOUNT', hide_gridlines = True,
                              show_footer = False, show_header = False)
        ws.set_footer('The notes on pages 5 to 7 form an integral part of these financial statements statements.\n' +
                      'Page {}'.format(xlb.page_number))


class FYBSPage(ExcelReportPage):

    @property
    def sheetname(self):
        return '{}FY BS '.format(self.sheetname_prefix) + self.rep.datestring

    def format_page(self, excel_base, worksheet):

        def header(title):
            xlb.write_merged_header(ws, title, cols='A:F', underline=0)

        def sub_title(text):
            ws.write('B{0}'.format(xlb.line_number+1), text, xlb.bold_left_fmt)
            xlb.line_number += 1

        def note(text):
            ws.merge_range('B{0}:F{0}'.format(xlb.line_number+1), text, xlb.para_fmt)
            xlb.line_number +=1

        def write_row(data, title, note = '', bottom = 0):
            xlb.write_fy_row(ws, data, title, cell_format={'bottom': bottom}, row_height=15, note=note)

        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        # Nominal code info columns
        for range, width in [('A:A', 1),  # Margin
                             ('B:B', 44.5),  # Description
                             ('C:C', 10),  # Note
                             ('D:D', 12),
                             ('E:E', 0.5),
                             ('F:F', 12),

                             ]:  # Dates
            ws.set_column(range, width)
        xlb.col_list=(3, 5, )  # Two column report
        header(coa.company_name)
        header('(Registration number: {})'.format(coa.company_number))
        header('Balance sheet at {}'.format(rep.full_datestring))
        xlb.line_number += 1
        cell_location = xl_rowcol_to_cell(xlb.line_number, 3)
        ws.write(cell_location, 'Note', xlb.bold_fmt)
        xlb.write_row(ws, rep.datestrings)
        xlb.write_row(ws, ['£']*2)
        xlb.line_number += 1
        #**********************
        sub_title('Fixed assets')
        fixed_assets = xlb.sum(coa.fixed_assets)
        write_row(fixed_assets, 'Tangible fixed assets', note=4, bottom=1)
        #**********************
        xlb.line_number += 1
        sub_title('Current assets')
        debtors= xlb.sum(coa.debtors)
        write_row(debtors, 'Debtors', note=5)
        cash_at_bank = xlb.sum(coa.cash_at_bank)
        write_row(cash_at_bank, 'Cash at bank and in hand', bottom=1)
        current_assets = [x[0]+x[1] for x in zip(debtors, cash_at_bank)]
        write_row(current_assets, '', bottom = 1) # Todo
        xlb.line_number += 1
        creditors_short_term = xlb.sum(coa.short_term_liabilities)
        write_row(creditors_short_term, 'Creditors: Amounts falliing due within one year', note=6, bottom=1)
        net_current_assets = [x[0]+x[1] for x in zip(current_assets, creditors_short_term)]
        write_row(net_current_assets, 'Net current assets', bottom = 1)
        total_assets= [x[0]+x[1] for x in zip(fixed_assets, net_current_assets)]
        write_row(total_assets, 'Total assets less liabilities')
        creditors_long_term= xlb.sum(coa.long_term_liabilities)
        write_row(creditors_long_term, 'Creditors: Amounts falliing due after more than one year', note=7, bottom=1)
        net_assets= [x[0]+x[1] for x in zip(total_assets, creditors_long_term)]
        write_row(net_assets, 'Net Assets', bottom = 6)
        #**********************
        xlb.line_number += 1
        sub_title('Capital and reserves')
        xlb.line_number += 1
        called_up_share_capital = xlb.sum(coa.called_up_capital, sign = -1)
        write_row(called_up_share_capital, 'Called up share capital', note = 8)
        profit_and_loss_account = xlb.sum(coa.profit_and_loss_account + coa.retained_capital, sign = -1)
        write_row(profit_and_loss_account, 'Profit and loss account', note = 10, bottom = 1)
        shareholders_funds = [x[0]+x[1] for x in zip(called_up_share_capital, profit_and_loss_account)]
        write_row(shareholders_funds, 'Shareholders'' funds', bottom = 6)
        #**********************
        xlb.line_number += 2
        note('These accounts have been prepared in accordance with the provisions applicable to companies subject ')
        note('to the small companies regime and in accordance with the Financial Reporting Standard for Smaller Entities ')
        note('(effective 2008).')
        xlb.line_number += 1
        note('For the year ending {} the company was entitle to exemption under '.format(rep.full_datestring))
        note('section 477 of the Companies Act 2006 relating to small companies.')
        xlb.line_number += 1
        note('The members have not required the company to obatin an audit in accordance with section 476 of the ')
        note('Companies Act 2006.')
        xlb.line_number += 1
        note('The director acknowledges his reponsibilities for complying with the requirements of the Act with ')
        note('respect to accounting records and the preperation of accounts.')
        xlb.line_number +=3
        note('Approved by the director on {}.'.format(rep.report_date_full_string))
        xlb.line_number +=3
        note('Dr Humphrey Drummond')
        note('Director')
        xlb.format_print_area(ws, 'Balance Sheet', hide_gridlines=True,
                              show_footer=False, show_header=False)
        ws.set_footer('The notes on pages 5 to 7 form an integral part of these financial statements statements.\n' +
                      'Page {}'.format(xlb.page_number))


class FYDetailPnLPageSummary(ExcelReportPage):

    @property
    def sheetname(self):
        return '{}FY Detail P&L Summary'.format(self.sheetname_prefix) + self.rep.datestring

    def format_page(self, excel_base, worksheet):
        def col(at_col):
            return xl_rowcol_to_cell(xlb.line_number, at_col)

        def icol(index):  # Indexed column, index into data table
            return col(xlb.col_list[index])

        def write_block_sum(acct_list, title, col_increment=1, sign=1, bottom=0):
            block_sum, has_data = _calc_block_sum(xlb, rep, acct_list, sign)
            if has_data:
                fmt_title = xlb.workbook.add_format(
                    {**xlb.base_format_dictionary, **{'align': 'left', 'font_size': 11}})
                fmt_cell = xlb.workbook.add_format(
                    {**xlb.base_format_dictionary, **{'align': 'left', 'font_size': 11, 'bottom': bottom}})
                ws.write(col(0), '{}'.format(title), fmt_title)
                # write out summary
                cell_location = xl_rowcol_to_cell(xlb.line_number, xlb.col_list[0 + col_increment])
                ws.write(cell_location, block_sum[0], fmt_cell)
                cell_location = xl_rowcol_to_cell(xlb.line_number, xlb.col_list[2 + col_increment])
                ws.write(cell_location, block_sum[1], fmt_cell)
                xlb.line_number += 1

        def title(text):
            # Merge whole row
            ws.merge_range('A{0}:H{0}'.format(xlb.line_number), text, xlb.title_fmt)
            xlb.line_number += 1

        def note_title(text):
            self.note_number += 1
            xlb.line_number += 1
            ws.write(col(0), '{} {}'.format(self.note_number, text), xlb.bold_left_fmt)
            xlb.line_number += 1

        def sub_title(text, bold=True):
            if bold:
                ws.write(col(0), text, xlb.bold_left_fmt)
            else:
                ws.write(col(0), text, xlb.left_fmt)
            xlb.line_number +=1

        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        self.note_number = 0
        xlb.col_list=(1, 3, 5, 7, )  # Two column report
        # Nominal code info columns
        for range, width in [('A:A', 30), ('B:B', 12), ('C:C', 1), ('D:D', 12), ('E:E', 1), ('F:F', 12), ('G:G', 1),
                             ('H:H', 12)]:
            ws.set_column(range, width)
        title(coa.company_name)
        xlb.line_number +=1
        title('Detailed Profit and Loss Account for the Year Ended {}'.format(rep.full_datestring))
        cell_fmt = xlb.workbook.add_format({**xlb.base_format_dictionary, **{'align': 'right'}})
        ws.write(col(2), rep.year, xlb.bold_fmt)
        ws.write(col(6), rep.prior_year, xlb.bold_fmt)
        xlb.line_number += 1
        ws.write(col(1), '£', xlb.bold_fmt)
        ws.write(col(3), '£', xlb.bold_fmt)
        ws.write(col(5), '£', xlb.bold_fmt)
        ws.write(col(7), '£', xlb.bold_fmt)
        xlb.line_number += 1
        write_block_sum(coa.sales, 'Turnover (analysed below)', sign=-1, bottom=0)
        write_block_sum(coa.material_costs, 'Cost of sales (analysed below)', sign=-1, bottom=1)
        sum_gross_profit = coa.sales + coa.material_costs
        write_block_sum(sum_gross_profit, 'Gross Profit', sign=-1, bottom=1)
        # TODO write_block_sum(coa.sales, 'Gross profit (%)', sign=-1)
        sub_title('Administrative expenses')
        write_block_sum(coa.establishment_costs, 'Establishment costs (analysed below)', sign=-1, col_increment=0,
                        bottom = 0)
        sub_title('General administrative expenses', bold=False)
        write_block_sum(coa.admin_costs + coa.employment_costs + coa.staff_training_costs,
                        '(analysed below)', sign=-1, col_increment=0, bottom=0)
        write_block_sum(coa.bank_charges, 'Finance costs (analysed below)', sign=-1, col_increment=0, bottom=0)
        write_block_sum(coa.depreciation_costs, 'Depreciation costs (analysed below)', sign=-1, col_increment=0,
                        bottom = 1)
        write_block_sum(coa.amortisation_costs, 'Amortisation costs (analysed below)', sign=-1, col_increment=0,
                        bottom=1)
        write_block_sum(coa.finance_costs, 'Finance costs (analysed below)', sign=-1, col_increment=0,
                        bottom=1)
        xlb.line_number += 1
        sum_costs = coa.establishment_costs + coa.admin_costs + coa.bank_charges + coa.depreciation_costs \
                + coa.amortisation_costs + coa.finance_costs + coa.employment_costs + coa.staff_training_costs
        write_block_sum(sum_costs, '', sign=-1, col_increment=1, bottom=1)  # Sum admin
        sub_title('(Loss)/profit on ordinary activities', bold=False)
        nc_PBT = set(coa.PBT)
        nc_calc = set(sum_gross_profit + sum_costs)
        assert nc_PBT == nc_calc, 'PBT = {} and sum = {} diff = {}'.format(nc_PBT, nc_calc, nc_PBT ^ nc_calc)
        write_block_sum(coa.PBT, 'before taxation', sign=-1,
                        bottom=6)
        xlb.format_print_area(ws, 'PROFIT & LOSS ACCOUNT', hide_gridlines=True,
                              show_footer=False, show_header=False)
        ws.set_footer('This page does not form part of the statutory financial statements.\n' +
                  'Page {}'.format(xlb.page_number))


class FYDetailPnLPage(ExcelReportPage):

    @property
    def sheetname(self):
        return '{}FY Detail P&L '.format(self.sheetname_prefix) + self.rep.datestring

    def format_page(self, excel_base, worksheet):

        def write_block(acct_list, title, sign=1, sum_for_one_entry = False):
            _write_block(ws, xlb, rep, acct_list, title, sign=sign, sum_for_one_entry=sum_for_one_entry)

        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        # Nominal code info columns
        for range, width in [('A:A', 1),  # Margin
                             ('B:B', 49),  # Description
                             ('C:C', 15),  # Cols
                             ('D:D', 1),  # Spacer
                             ('E:E', 15),  # Cols
                             ('F:F', 1),  # Margin
                             ]:
            ws.set_column(range, width)
        xlb.col_list=(2, 4, )  # Two column report
        xlb.write_merged_header(ws, coa.company_name, cols='B:E')
        xlb.write_merged_header(ws, 'Profit and Loss Account for the Year Ended {}'.format(rep.full_datestring),
                                cols='B:E')
        xlb.write_row(ws, rep.datestrings)
        xlb.write_row(ws, ['£']*2)
        xlb.line_number = 5
        profit = [p(0)] * 4
        write_block(coa.sales, 'Turnover', sign=-1, sum_for_one_entry = True)
        write_block(coa.material_costs, 'Cost of Sale')
        write_block(coa.employment_costs, 'Employment Costs')
        write_block(coa.establishment_costs, 'Establishment Costs')
        write_block(coa.variable_costs + coa.fixed_production_costs + coa.admin_costs,
                    'General administrative expenses')
        write_block(coa.bank_charges, 'Finance Charges')
        write_block(coa.depreciation_costs, 'Depreciation of office equipment')
        xlb.format_print_area(ws, 'DETAILED PROFIT & LOSS ACCOUNT', hide_gridlines = True,
                              show_footer=False, show_header=False)
        ws.set_footer('This page does not form part of the statutory financial statements.\n' +
                      'Page {}'.format(xlb.page_number))


class FYNotes(ExcelReportPage):

    @property
    def sheetname(self):
        return '{}Notes '.format(self.sheetname_prefix) + self.rep.datestring

    def format_page(self, excel_base, worksheet):
        def col(at_col):
            return xl_rowcol_to_cell(xlb.line_number, at_col)

        def icol(index):  # Indexed column, index into data table
            return col(xlb.col_list[index])
        
        def write_block_sum(acct_list, title, sign=1):
            _write_block_sum(ws, xlb, rep, acct_list, title, sign=sign)

        def title(text):
            # Merge whole row
            ws.merge_range('A{0}:H{0}'.format(xlb.line_number), text, xlb.title_fmt)
            xlb.line_number +=1

        def note_title(text):
            self.note_number += 1
            xlb.line_number += 1
            ws.write(col(0), '{} {}'.format(self.note_number, text), xlb.bold_left_fmt)
            xlb.line_number += 1

        def sub_title(text):
            ws.write(col(0), text, xlb.bold_left_fmt)
            xlb.line_number +=1

        def note(text):
            ws.merge_range('A{0}:H{0}'.format(xlb.line_number+1), text, xlb.para_fmt)
            xlb.line_number +=1

        def row_title(a, b):
            ws.write(icol(0), a, xlb.bold_fmt)
            ws.write(icol(1), b, xlb.bold_fmt)
            xlb.line_number += 1

        def row(title, a, b, bottom = 0, sign=1):
            cell_fmt = xlb.workbook.add_format({**xlb.base_format_dictionary, **{'bottom': bottom, 'align': 'right'}})
            ws.write(col(0), title, xlb.fmt)
            ws.write(icol(0), a * sign, cell_fmt)
            ws.write(icol(1), b * sign, cell_fmt)
            xlb.line_number += 1

        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        self.note_number = 0
        xlb.col_list=(5, 7, )  # Two column report
        # Nominal code info columns
        for range, width in [('A:A', 23), ('B:B', 14), ('C:C', 1), ('D:D', 14), ('E:E', 1), ('F:F', 14), ('G:G', 1),
                             ('H:H', 14)]:
            ws.set_column(range, width)
        title(coa.company_name)
        xlb.line_number +=1
        title('Notes to the Financial Statements for the Year Ended {}'.format(rep.full_datestring))
        note_title('Accounting Policies')
        xlb.line_number +=1
        sub_title('Basis of Preparation')
        note("The financial statements have been prepared under the historical cost convention and in accordance with the Financial ")
        note("Report Standard for Smaller Entities (Effective April 2008).")
        xlb.line_number +=1
        sub_title('Turnover')
        note("Turnover represents amounts chargeable, net of value added tax, in respect of the sale of goods and services to ")
        note("customers.")
        xlb.line_number +=1
        sub_title('Depreciation')
        note("Depreciation is provided on tangle fixed assets so as to write off the cost or valuation, less any estimated residual ")
        note("value, over their expected useful econominc life as follows:")
        xlb.line_number += 1
        ws.merge_range('A{0}:B{0}'.format(xlb.line_number + 1), 'Asset class', xlb.bold_left_fmt)
        ws.merge_range('D{0}:H{0}'.format(xlb.line_number + 1), 'Depreciation method and rate', xlb.bold_left_fmt)
        xlb.line_number += 1
        ws.merge_range('A{0}:B{0}'.format(xlb.line_number + 1), 'Office Equipment', xlb.left_fmt)
        ws.merge_range('D{0}:H{0}'.format(xlb.line_number + 1), '25% straight line', xlb.left_fmt)
        xlb.line_number +=2
        sub_title('Financial Instruments')
        note("Financial instruments are classified and acounted for, according to the substance of the contractual arrangement, ")
        note("as financial assets, financial liabilities or equity instruments.  An equity instrument is any contract that ")
        note("evidences a residual interest in the assets of the company after deducting all of its liabilities.  Where shares ")
        note("are issued, any component that creates a financial liability of the company is presented as a liability in ")
        note("the balance sheet.  The corresponding dividends relating to the liability component are charged as interest ")
        note("expense in the profit and loss account.")
        note_title('Operating (loss)/profit')
        note('Operating (loss)/profit is stated after charging:')
        xlb.line_number += 1
        row_title(rep.year, rep.prior_year)
        row_title('£', '£')
        write_block_sum(coa.depreciation_costs, 'Depreciation of tangible fixed assets')
        #*********************************************************
        note_title('Taxation')
        xlb.line_number += 1
        sub_title('Tax on (loss)/profit on ordinary activities')
        row_title(rep.year, rep.prior_year)
        row_title('£', '£')
        sub_title('Current tax')
        write_block_sum(coa.year_corporation_tax, 'Corporation tax (credit)/ charge')
        xlb.line_number += 1
        xlb.line_number += 7  #  Manual Page break
        note_title('Tangible Fixed Assets')
        #*********************************************************
        row_title('Office Equipment', 'Total')
        row_title('£', '£')
        sub_title('Cost or Valuation')
        # Todo Generalise to a list of nominal codes
        prev_cost = xlb.list_get_value(rep.trial_balances[1], coa.office_equipment_cost)
        this_cost = xlb.list_get_value(rep.trial_balances[0], coa.office_equipment_cost)
        additions = this_cost - prev_cost  # Todo not sure this is a general solution
        row('At {}'.format(rep.full_year_start_string), prev_cost, prev_cost)
        row('Additions', additions, additions, bottom=1)
        row('At {}'.format(rep.full_datestring), this_cost, this_cost, bottom=1)
        sub_title('Depreciation')
        prev_depreciation = xlb.list_get_value(rep.trial_balances[1], coa.office_equipment_depreciation, sign=-1)
        this_depreciation = xlb.list_get_value(rep.trial_balances[0], coa.office_equipment_depreciation, sign=-1)
        charge = this_depreciation - prev_depreciation  # Todo not sure this is a general solution
                                          # Should check that this is equal to depreciation expense
        row('At {}'.format(rep.full_year_start_string), prev_depreciation, prev_depreciation)
        row('Additions', charge, charge, bottom=1)
        row('At {}'.format(rep.full_datestring), this_depreciation, this_depreciation, bottom=1)
        sub_title('Net book value')
        this_book_value = this_cost - this_depreciation
        prev_book_value = prev_cost - prev_depreciation
        row('At {}'.format(rep.full_datestring), this_book_value, this_book_value, bottom=6)
        row('At {}'.format(rep.full_year_start_string), prev_book_value, prev_book_value, bottom=6)
        #*********************************************************
        note_title('Debtors')
        xlb.line_number += 1
        row_title(rep.year, rep.prior_year)
        row_title('£', '£')
        write_block_sum(coa.debtors, 'Other debtors')
        xlb.line_number += 1
        #*********************************************************
        note_title('Creditors: Amount falling due within one year')
        xlb.line_number += 1
        row_title(rep.year, rep.prior_year)
        row_title('£', '£')
        write_block_sum(coa.short_term_liabilities, 'Corporation tax', sign=-1)
        xlb.line_number += 1
        #*********************************************************
        note_title('Creditors: Amount falling due after more than one year')
        xlb.line_number += 1
        row_title(rep.year, rep.prior_year)
        row_title('£', '£')
        write_block_sum(coa.long_term_liabilities, 'Other creditors', sign=-1)
        xlb.line_number += 1
        #*********************************************************
        note_title('Share Capital')
        xlb.line_number += 1
        sub_title('Allotted, called up and fully paid shares')  # TODO need to deal with partly paid up shares
        cell_fmt = xlb.workbook.add_format({**xlb.base_format_dictionary, **{'bottom': 6, 'align': 'right'}})
        ws.write(col(2), rep.year, xlb.bold_fmt)
        ws.write(col(6), rep.prior_year, xlb.bold_fmt)
        xlb.line_number += 1
        ws.write(col(1), 'No.', xlb.bold_fmt)
        ws.write(col(3), '£', xlb.bold_fmt)
        ws.write(col(5), 'No.', xlb.bold_fmt)
        ws.write(col(7), '£', xlb.bold_fmt)
        xlb.line_number += 2
        ws.write(col(0), 'Ordinary Shares of £1 each', xlb.left_fmt)
        called_up_share_capital = xlb.sum(coa.called_up_capital, sign = -1)
        # Todo need to find a place for the share capital
        ws.write(col(1), 2, cell_fmt)
        ws.write(col(3), called_up_share_capital[0], cell_fmt)
        ws.write(col(5), 2, cell_fmt)
        ws.write(col(7), called_up_share_capital[1], cell_fmt)
        xlb.line_number += 1
        #*********************************************************
        note_title('Dividends')
        xlb.line_number += 1
        row_title(rep.year, rep.prior_year)
        row_title('£', '£')
        sub_title('Dividends paid')
        write_block_sum(coa.dividends, 'Current year interim dividend paid')
        xlb.line_number += 1
        #*********************************************************
        note_title('Reserves')
        row_title('Profit and loss Account', 'Total')
        row_title('£', '£')
        prev_pnl = xlb.list_get_value(rep.trial_balances[1], coa.profit_and_loss_account + coa.retained_capital)
        this_pnl = xlb.list_get_value(rep.trial_balances[0], coa.profit_and_loss_account + coa.retained_capital)
        years_pnl = this_pnl  - prev_pnl  # Todo not sure this is a general solution
        row('At {}'.format(rep.full_year_start_string), prev_pnl, prev_pnl, sign=-1)
        row('Profit/(loss) for the year', years_pnl, years_pnl, bottom=1, sign=-1)
        row('At {}'.format(rep.full_datestring), this_pnl, this_pnl, bottom=1, sign=-1)
        #*********************************************************
        note_title('Control')
        xlb.line_number += 1
        note("The company is controlled by the director who owns 100% of the called up share capital.")
        xlb.format_print_area(ws, 'Director''s Report', hide_gridlines=True,
                              show_footer=False, show_header=False, last_col=7)


class FYCT600_Calcs(ExcelReportPage):

    @property
    def sheetname(self):
        return 'Tax Calcs '.format(self.sheetname_prefix) + self.rep.datestring

    def format_page(self, excel_base, worksheet):
        def col(at_col):
            return xl_rowcol_to_cell(xlb.line_number, at_col)

        def title(text):
            # Merge whole row
            ws.merge_range('A{0}:B{0}'.format(xlb.line_number), text, xlb.title_fmt)
            xlb.line_number += 1

        def write_item(number, title, param, sign=1):
            ws.write(col(0), '{} : {}'.format(number,title), xlb.bold_left_fmt)
            if isinstance(param, list):
                block_sum, has_data = _calc_block_sum(xlb, rep, param, sign)
                if has_data:
                    value = block_sum[0]
                else:
                    value = p(0)
                ws.write(col(1), value, xlb.fmt)
            else:
                if sign == 1:  # Allows text to be written out
                    ws.write(col(1), param, xlb.fmt)
                else:
                    ws.write(col(1), param * sign, xlb.fmt)
            xlb.line_number += 1

        def write(title, value):
            ws.write(col(0), title, xlb.bold_left_fmt)
            ws.write(col(1), value, xlb.fmt)
            xlb.line_number += 1

        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        self.note_number = 0
        xlb.col_list=(1, )  # Two column report
        # Nominal code info columns
        for range, width in [('A:A', 50), ('B:B', 30),]:
            ws.set_column(range, width)
        title(coa.company_name)
        xlb.line_number +=1
        title('Tax calculations for CT600 Account for the Year Ended {}'.format(rep.full_datestring))
        write('Company name', coa.company_name)
        write('Company number', coa.company_number)
        write('Tax reference', coa.tax_reference)
        write('Return for period from:', rep.full_year_start_string)
        write('Return for period to:', rep.full_datestring)
        xlb.line_number += 1
        write_item(1, 'Total Turnover', coa.sales, sign=-1)
        # next item is cardinal and needs to be calculated.  If there is a loss if a loss it is zero
        pnl = _calc_block_sum(xlb, rep, coa.PBT)[0][0]
        if pnl > p(0):  # Loss
            item_3 = p(0)
            item_122 = pnl
        else:
            item_3 = pnl
            item_122 = p(0)
        write_item(3, 'Trading and professional profits', item_3, sign=-1)
        # Calc Trading losses brought forward claimed against profits
        if pnl < 0:  # Made a profit
            trading_losses_brought_forward = _calc_block_sum(xlb, rep, coa.trading_losses)[0][0]
            assert trading_losses_brought_forward > p(0) # > 0 by definition
            if abs(trading_losses_brought_forward) > pnl:
                trading_losses_brought_forward_claimed = -pnl  # Claim only the PNL
            else:
                trading_losses_brought_forward_claimed = trading_losses_brought_forward # Use all the B/F losses
        else:  # made a lost so no brought forward loasses
            trading_losses_brought_forward_claimed = p(0)
        write_item(4, 'Trading losses brought forward claimed against profits', trading_losses_brought_forward_claimed)
        net_trading_and_professional_profits = item_3 + trading_losses_brought_forward_claimed
        write_item(5, 'Net trading and professional profits', net_trading_and_professional_profits)
        write_item(21, 'Profits before deductions and other reliefs', net_trading_and_professional_profits)
        write_item(37, 'Profits chargeable to corporation tax', net_trading_and_professional_profits)
        write_item(39, 'Number of associated companies in this period', '0')
        write_item(42, 'Claiming staring rate or small companies rate on any part of the profits', 'X')
        write_item(43, 'Financial Year', rep.prior_year)
        write_item(44, 'Amount of profit', net_trading_and_professional_profits)
        tax_rate, tax_in_year_calc = uk_corporation_tax_rate(rep.prior_year, net_trading_and_professional_profits)
        write_item(45, 'Rate of tax', tax_rate)
        corporation_tax = _calc_block_sum(xlb, rep, coa.year_corporation_tax)[0][0]
        if corporation_tax < 0:  # Loss rolled over tax
            tax_in_year = p(0)
        else:
            tax_in_year = corporation_tax
        write_item(46, 'Tax in year', tax_in_year)
        write_item(63, 'Corporation tax', tax_in_year)
        # TODO need to extract out marginal relief calculation
        write_item(64, 'Marginal rate relief', tax_in_year)
        write_item(65, 'Corporation tax net of marginal relief', tax_in_year)
        write_item(70, 'Corporation tax chargeable', tax_in_year)
        write_item(86, 'Tax Payable - self assessment of tax payable', tax_in_year)
        write_item(90, 'Tax already paid', 'Todo')  # TODO add code for the 109.39
        write_item(91, 'Tax outstanding', tax_in_year)
        write_item(172, 'Anual investment allowance', coa.annual_investment_allowance)  # Purchase
        write_item(107, 'Machinery and plant main pool', coa.machinery_and_plant_main_pool)
        write_item(122, 'Trading losses', item_122)
        xlb.line_number += 1
        write('Internal Version checking','')
        write('Luca software version', '{}'.format(version))
        ws.set_footer('This page does not form part of the statutory financial statements.\n' +
                      'Page {}'.format(xlb.page_number))


class PlaceHolder(ExcelReportPage):
    """This is page which is a place holder for one to be printined"""
    place_holder_number = 1

    @property
    def sheetname(self):
        return '#{}'.format(PlaceHolder.place_holder_number)

    def format_page(self, excel_base, worksheet):
        PlaceHolder.place_holder_number += 1
        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        # Nominal code info columns
        for range, width in [('A:A', 100)]:
            ws.set_column(range, width)
        for location, text in [
            ('A1', 'Place holder'),
            ('A3', 'Page Intentionally Blank'),
        ]:
            ws.write(location, text, xlb.title_fmt)
        xlb.format_print_area(ws, 'Place Holder', hide_gridlines=True,
                              show_footer=False, show_header=False)
        ws.set_footer('Page {}'.format(xlb.page_number))
