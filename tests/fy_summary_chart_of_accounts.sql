DELETE FROM chart_of_accounts WHERE chart='FY_Summary'
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Summary', 50, 'Turnover', 'Income');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Summary', 60, 'Cost of sales', 'Expense');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Summary', 80, 'Administrative Expenses', 'Expense');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Summary', 91, 'Tax on(loss)/profit on ordinary acitivies', 'Expense');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Summary', 10, 'Tangible fixed assets', 'Asset');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Summary', 11, 'Debtors', 'Asset');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Summary', 12, 'Cash at bank and in hand', 'Asset');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Summary', 20, 'Creditors: Amounts falling due within one year', 'Liability');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Summary', 21, 'Creditors: Amounts falling due after more than one year', 'Liability');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Summary', 30, 'Profit and Loss Account', 'Equity');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Summary', 31, 'Called up share capital', 'Equity');
