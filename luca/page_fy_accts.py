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
        reg_fmt = self.workbook.add_format({**self.base_format_dictionary,  **{
            'bold' : True, 'italic' : True, 'align': 'right'}})
        title_fmt = self.workbook.add_format({**self.base_format_dictionary,  **{
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
        xlb.write_fy_row(ws, cost_of_sales, 'Cost of sales', cell_format={'bottom': 1}, row_height=22)
        gross_profit = [x[0]-x[1] for x in zip(turnover, cost_of_sales)]
        xlb.write_fy_row(ws, gross_profit, 'Gross profit', row_height=22)
        admin_expenses = xlb.sum(coa.variable_costs
                                 + coa.fixed_production_costs
                                 + coa.admin_costs,  sign = -1)
        xlb.write_fy_row(ws, admin_expenses, 'Administrative expenses', cell_format={'bottom': 1}, row_height=22)
        operating_profit = [x[0]+x[1] for x in zip(gross_profit, admin_expenses)]
        xlb.write_fy_row(ws, operating_profit, 'Operating (loss)/profit', note='2',
                         cell_format={'bottom': 1}, row_height=22)
        xlb.write_fy_row(ws, operating_profit, '(Loss)/profit on ordinary activities before taxation', row_height=22)
        corporation_tax = xlb.sum(coa.year_corporation_tax)
        xlb.write_fy_row(ws, corporation_tax, 'Tax on (loss)/profit on ordinary activities', note='3',
                         cell_format={'bottom': '1'}, row_height=22)
        profit_or_loss= [x[0]+x[1] for x in zip(operating_profit, corporation_tax)]
        xlb.write_fy_row(ws, profit_or_loss, '(Loss)/profit for the financial year', note='10',
                         cell_format={'bottom': 6}, row_height = 22)
        ws.write('C38', 'The notes on pages 6 to 8 form an integral part of these financial statemeents.', xlb.fmt)
        xlb.line_number = 39
        xlb.format_print_area(ws, 'PROFIT & LOSS ACCOUNT', hide_gridlines = True,
                              show_footer = False, show_header = False)
        ws.set_footer('The notes on pages 6 to 8 form an integral part fo these financial statements statements.\n' +
                      'Page {}'.format(xlb.page_number))


class FYBSPage(ExcelReportPage):

    @property
    def sheetname(self):
        return '{}FY BS '.format(self.sheetname_prefix) + self.rep.datestring

    def format_page(self, excel_base, worksheet):

        def header(title):
            xlb.write_merged_header(ws, title, cols='B:E', underline=0)

        def sub_title(text):
            ws.write('B{0}'.format(xlb.line_number+1), text, xlb.bold_left_fmt)
            xlb.line_number += 1

        def note(text):
            ws.merge_range('A{0}:E{0}'.format(xlb.line_number+1), text, xlb.para_fmt)
            xlb.line_number +=1

        def write_row(data, title, note = '', bottom = 0):
            xlb.write_fy_row(ws, data, title, cell_format={'bottom': bottom}, row_height=15)

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
        write_row(fixed_assets, 'Tangible fixed assets', note = 4, bottom = 1)
        #**********************
        sub_title('Current assets')
        debtors= xlb.sum(coa.debtors)
        write_row(debtors, 'Debtors', note = 5)
        cash_at_bank = xlb.sum(coa.cash_at_bank)
        write_row(cash_at_bank, 'Cash at bank and in hand', bottom = 1)
        current_assets = [x[0]-x[1] for x in zip(debtors, cash_at_bank)]
        write_row(current_assets, '', bottom = 1)
        #**********************
        sub_title('Capital and reserves')
        #**********************
        note('These accounts have been prepared in accordance with the provisions applicable to companies subject ' +
             'to the small companies regime and in accordance with teh Financial Reporting Standard for Smaller Entities ' +
             '(effective 2008).')
        note('For the year ending {} the company was entitle to exemption under '.format(rep.full_datestring) +
             'section 477 of the Companies Act 2006 relating to small companies.')
        note('The members have not required the company to obatin an audit in accordance with section 476 of the ' +
             'Companies Act 2006.')
        note('The director acknowledges his reponsibilities for complying with the requirements of the Act with ' +
             'respect to accounting records and the preperation of accounts.')
        xlb.line_number +=3
        note('Approved by the director on ().')
        xlb.line_number +=3
        note('Dr Humphrey Drummond')
        note('Director')
        xlb.format_print_area(ws, 'Balance Sheet', hide_gridlines=True,
                              show_footer=False, show_header=False)
        ws.set_footer('The notes on pages 6 to 8 form an integral part fo these financial statements statements.\n' +
                      'Page {}'.format(xlb.page_number))


class FYDetailPnLPage(ExcelReportPage):

    @property
    def sheetname(self):
        return '{}FY Detail P&L '.format(self.sheetname_prefix) + self.rep.datestring

    def format_page(self, excel_base, worksheet):

        def write_block(acct_list, title, sign=1):
            block_sum = [p(0)] * 4
            fmt = xlb.workbook.add_format(
                {**xlb.base_format_dictionary,  **{'align': 'right'}})
            fmt_title = xlb.workbook.add_format(
                {**xlb.base_format_dictionary,  **{'align': 'left', 'font_size': 11}})
            fmt_left = xlb.workbook.add_format(
                {**xlb.base_format_dictionary,  **{'align': 'left'}})
            fmt_underline = xlb.workbook.add_format(
                {**xlb.base_format_dictionary,  **{'align': 'right', 'bottom': 1}})
            fmt_double_underline = xlb.workbook.add_format(
                {**xlb.base_format_dictionary,  **{'align': 'right', 'bottom': 6}})
            # Do the title
            cell_location = xl_rowcol_to_cell(xlb.line_number, 1)
            ws.write(cell_location, title, fmt_title)
            xlb.line_number += 1
            # The acct_list is the simple list of account nominal codes that are to be included in this block
            for nc in acct_list:
                # If there no row then ignore error
                try:
                    name = rep.chart_of_accounts[nc]
                    cell_location = xl_rowcol_to_cell(xlb.line_number, 1)
                    ws.write(cell_location, name, fmt_left)
                    for i, col in enumerate(xlb.col_list):
                        tb = rep.trial_balances[i]
                        cell_location = xl_rowcol_to_cell(xlb.line_number, col)
                        value = xlb.get_value(tb, nc, sign)
                        ws.write(cell_location, value, fmt)
                        block_sum[i] += p(value)
                    xlb.line_number += 1
                except KeyError:
                    # This is where there is no data in the name
                    print("Missing data for account {}. Error {}".format(nc, sys.exc_info()))
                    pass
            # Add a sub total line if required
            if len(acct_list) != 1:
                for i, c in enumerate(xlb.col_list):
                    cell_location = xl_rowcol_to_cell(xlb.line_number, c)
                    ws.write(cell_location, block_sum[i], fmt_double_underline)
                xlb.line_number += 1
            xlb.line_number += 1  # Blank line seperator

        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        # Nominal code info columns
        for range, width in [('B:B', 80),  # Description
                             ('C:D', 20)]: # Cols
            ws.set_column(range, width)
        xlb.col_list=(2, 3, )  # Two column report
        xlb.write_merged_header(ws, coa.company_name, cols='B:E')
        xlb.write_merged_header(ws, 'Profit and Loss Account for the Year Ended {}'.format(rep.full_datestring),
                                cols='B:E')
        xlb.write_row(ws, rep.datestrings)
        xlb.write_row(ws, ['£']*2)
        xlb.line_number = 5
        profit = [p(0)] * 4
        write_block(coa.sales, 'Turnover', sign=-1)
        write_block(coa.material_costs, 'Cost of Sale')
        write_block(coa.employment_costs, 'Employment Costs')
        write_block(coa.establishment_costs, 'Establishment Costs')
        write_block(coa.variable_costs + coa.fixed_production_costs + coa.admin_costs,
                    'General administrative expenses')
        write_block(coa.finance_charges, 'Finance Charges')
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

        def title(text):
            # Merge whole row
            ws.merge_range('A{0}:E{0}'.format(xlb.line_number), text, xlb.title_fmt)
            xlb.line_number +=1

        def note_title(text):
            self.note_number += 1
            ws.write('A{0}'.format(xlb.line_number), '{} {}'.format(self.note_number, text), xlb.bold_left_fmt)
            xlb.line_number += 2

        def sub_title(text):
            xlb.line_number +=1
            ws.write('A{0}'.format(xlb.line_number), text, xlb.bold_left_fmt)
            xlb.line_number +=1

        def note(text):
            ws.merge_range('A{0}:E{0}'.format(xlb.line_number), text, xlb.para_fmt)
            xlb.line_number +=1

        def row_title(a, b):
            cell_location = xl_rowcol_to_cell(xlb.line_number, xlb.col_list[0])
            ws.write(cell_location, a, xlb.fmt)
            cell_location = xl_rowcol_to_cell(xlb.line_number, xlb.col_list[1])
            ws.write(cell_location, b, xlb.fmt)

        def row(title, a, b, bottom = 0):
            cell_fmt = self.workbook.add_format({**self.base_format_dictionary, **{'bottom': bottom, 'align': 'right'}})
            cell_location = xl_rowcol_to_cell(xlb.line_number, 0)
            ws.write(cell_location, title, xlb.fmt)
            cell_location = xl_rowcol_to_cell(xlb.line_number, xlb.col_list[0])
            ws.write(cell_location, a, cell_fmt)
            cell_location = xl_rowcol_to_cell(xlb.line_number, xlb.col_list[1])
            ws.write(cell_location, b, cell_fmt)


        ws = worksheet
        xlb = excel_base
        xlb.rep = self.rep
        rep = self.rep
        coa = rep.coa
        self.note_number = 0
        xlb.col_list=(3, 4, )  # Two column report
        # Nominal code info columns
        for range, width in [('A:E', 20)]:
            ws.set_column(range, width)
        title(coa.company_name)
        xlb.line_number +=1
        title('Notes to the Financial Statements for the Year Ended {}'.format(rep.full_datestring))
        xlb.line_number +=2
        note_title('Accounting Policies')
        sub_title('Basis of Preperation')
        note("'The financial statements have been prepared under the historical cost convention and in " +
             "accordance with the Financial Report Standard for Smaller Entities (Effective April 2008).")
        sub_title('Turnover')
        note("'Turnover represents amounts chargeable, net of value added tax, in respect of the sale of goods " +
             "and services to customers.")
        sub_title('Depreciation')
        note("'Depreciation is provided on tangle fixed assets so as to write off the cost or valuation, less any " +
             "estimated residual value, over their expected useful econominc life as follows:")
        sub_title('Financial Instruments')
        note("'Financial instruments are classified and acounted for, according to the substance of the contractual " +
             "arrangement, as financial assets, financial liabilities or equity instruments.  An equity instrument " +
             "is any contract that evidences a residual interest in the assets of the company after deducting all " +
             "of its liabilities.  Where shares are issued, any component that creates a financial liability of the " +
             "company is presented as a liability in the balance sheet.  The corresponding dividens relating to the " +
             "liability component are charged as interest expense in the profit and loss account.")
        note_title('Operating (loss)/profit')
        note_title('Taxation')
        note_title('Tangible Fixed Assets')
        row_title('Office Euipment', 'Total')
        row_title('£', '£')
        sub_title('Cost or Valuation')
        # Todo Generalise to a list of nominal codes
        prev_cost = rep.list_get_cost(rep.trial_balances[3], coa.office_equipment_cost)
        this_cost = rep.list_get_cost(rep.trial_balances[2], coa.office_equipment_cost)
        additions = this_cost - prev_cost  # Todo not sure this is a general solution
        row('At {}'.format(rep.full_year_start_string), prev_cost, prev_cost)
        row('Additions', additions, additions, bottom=1)
        row('At {}'.format(rep.full_datestring), this_cost, this_cost, bottom=1)
        sub_title('Depreciation')
        prev_depreciation = rep.list_get_depreciation(rep.trial_balances[3], coa.office_equipment_depreciation)
        this_depreciation = rep.list_get_depreciation(rep.trial_balances[2], coa.office_equipment_depreciation)
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

        note_title('Debtors')
        note_title('Creditors: Amount falling due within one year')
        note_title('Creditors: Amount falling due after more than one year')
        note_title('Share Capital')
        note_title('Dividends')
        note_title('Reserves')
        note_title('Control')
        note("The company is controlled by the director who owns 100% of the called up share capital.")
        xlb.format_print_area(ws, 'Director''s Report', hide_gridlines=True,
                              show_footer=False, show_header=False)


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

