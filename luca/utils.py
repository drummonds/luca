__author__ = 'Humphrey'

from decimal import Decimal, InvalidOperation
import pandas as pd
from sys import exc_info

class LucaError(Exception):
    pass

one_pence = Decimal('0.01')

def p(value):
    "Convert `value` to Decimal pence implementing AIS rounding (up) or cents"
    # TODO think about Decimal(-0.00) == Decmial(0.00) which is true.  Should I try and convert -0 to +0?
    # I think probably better yes
    try:
        #If user_or_username is a User object
        test =  Decimal(Decimal(float(value)) * Decimal(100)).quantize(one_pence)
        i, d = divmod(test, 1)
        if abs(d) == Decimal(0.50):
            # Implement rounding
            if value > 0:
                result =  (Decimal(value) + Decimal(0.0025)).quantize(one_pence)
            else:
                result =  (Decimal(value) - Decimal(0.0025)).quantize(one_pence)
            # print('p Rounding |{}| to {}'.format(value, result))
        else:
            result =  Decimal(float(value)).quantize(one_pence)
    except InvalidOperation:
        print('Invalid Operation Val = |{}|'.format(value))
        t, v, tb = exc_info()
        raise v.with_traceback(tb)
    except TypeError:   #Oops -- didn't works.  ask forgiveness ;-)
        t, v, tb = exc_info()
        if isinstance(value, pd.Series):
            result = [p(x) for  x in value]
        else:
            print('Type Error Val = |{}|, {}'.format(value, type(value)))
            raise v.with_traceback(tb)
    return result

