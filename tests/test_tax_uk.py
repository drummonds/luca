from decimal import Decimal
import unittest

from luca import p, uk_corporation_tax_rate


class TaxUKTest(unittest.TestCase):

    def test_corporation_taxcalc(self):
        assert uk_corporation_tax_rate(2014, -11000) == (p(0.20), p(2200))
        assert uk_corporation_tax_rate('2014', -11000) == (p(0.20), p(2200))
        assert uk_corporation_tax_rate(2014, -300000) == (p(0.20), p(60000))
        assert uk_corporation_tax_rate(2014, -600000) == (Decimal('0.20625'), p(123750))
        assert uk_corporation_tax_rate(2014, -1500000) == (p(0.21), p(315000))
        assert uk_corporation_tax_rate(2014, -3000000) == (p(0.21), p(630000))

