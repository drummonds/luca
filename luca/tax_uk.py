"""Table of UK Corporation tax"""
from .utils import p

"""The UK Coporatio tax year starts on the 1st of April so if your year ends prior to that you should use the previous
years tax rate.
The Corporation tax is a list of
The main tax rate, then a list in order taxes on smaller profits.
Source 2016-05-29 https://www.gov.uk/government/publications/rates-and-allowances-corporation-tax/rates-and-allowances-corporation-tax
http://www.rossmartin.co.uk/companies/running-the-business/183-company-tax-rates-and-allowances"""
UK_CORPORATION_TAX = {
    2008: (0.28, [(0.21, 300000), (0.2975, 1500000)]),
    2009: (0.28, [(0.21, 300000), (0.2975, 1500000)]),
    2010: (0.28, [(0.21, 300000), (0.2975, 1500000)]),
    2011: (0.26, [(0.20, 300000), (0.2775, 1500000)]),
    2012: (0.24, [(0.20, 300000), (0.25, 1500000)]),
    2013: (0.23, [(0.20, 300000), (0.2375, 1500000)]),
    2014: (0.21, [(0.20, 300000), (0.2125, 1500000)]),
    2015: (0.20, []),
    2016: (0.20, []),
    2017: (0.19, []),
    2018: (0.19, []),
    2019: (0.19, []),
    2020: (0.17, []),
}

# TODO refactor to use margin relief system so as to match CT600 calculations

def uk_corporation_tax_rate(year, profit):
    """For a year and profit returns the effective tax rate and the tax amount,
    year = fiscal year from 1st April year to 31s of March year+1
    profit = Positive = loss, negative = profit (A-L+E-R-OE = 0, profit abs(R) > abs(E)"""
    main_rate, tax_list = UK_CORPORATION_TAX[year]
    tax = p(0)
    if profit > 0:  # Loss
        return main_rate, p(0)
    else:  # profit
        abs_profit = p(abs(profit))
        lower_limit = p(0)
        upper_limit = p(0)  # Deals with case of empty tax_list
        for rate, upper_limit in tax_list:
            if abs_profit > lower_limit:
                if abs_profit > upper_limit:
                    tax += p(rate * float((upper_limit - lower_limit)))
                else:
                    tax += p(rate * float((abs_profit - lower_limit)))
            lower_limit = upper_limit
        if abs_profit > upper_limit:
            tax += p(main_rate * float((abs_profit - upper_limit)))
        effective_rate = tax / abs_profit
        return effective_rate, tax
