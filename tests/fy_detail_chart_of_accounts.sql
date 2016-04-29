DELETE FROM chart_of_accounts WHERE chart='FY_Detail_Summary'
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Detail_Summary', 500, 'Turnover', 'Income');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Detail_Summary', 600, 'Cost of sales', 'Expense');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Detail_Summary', 800, 'Administrative Expenses', 'Expense');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Detail_Summary', 910, 'Tax on(loss)/profit on ordinary acitivies', 'Expense');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Detail_Summary', 100, 'Tangible fixed assets', 'Asset');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Detail_Summary', 110, 'Debtors', 'Asset');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Detail_Summary', 120, 'Cash at bank and in hand', 'Asset');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Detail_Summary', 200, 'Creditors: Amounts falling due within one year', 'Liability');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Detail_Summary', 210, 'Creditors: Amounts falling due after more than one year', 'Liability');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Detail_Summary', 300, 'Profit and Loss Account', 'Equity');
INSERT INTO chart_of_accounts (chart, code, name, category) VALUES ('FY_Detail_Summary', 310, 'Called up share capital', 'Equity');
