import pandas as pd
import numpy as np
import unittest

from luca import p

class UtilsTest(unittest.TestCase):

    def test_p(self):
        assert p(0) == p(-0.004)
        assert p(1) == p(1.004)
        assert p(1) == p(0.996)
        assert p(-1) == p(-1.004)
        assert p(-1) == p(-0.996)
        assert -1 == int(p(-0.996))  # Make sure not something horrible NaN

    def test_p_series(self):
        s = pd.Series([-0.004, 1.004, 0.996, -1.004, -0.996])
        r1 = p(s)
        assert r1[0] == p(0)
        assert r1[1] == p(1)
        assert r1[2] == p(1)
        assert r1[3] == p(-1)
        assert r1[4] == p(-1)

    def test_p_series_2(self):
        """Testing some code which was percularily giving NaN"""
        s = pd.Series([-0.004, 1.004, 0.996, -1.004, -0.996])
        r1 = [p(x) for x in s]
        assert r1[0] == p(0)
        assert r1[1] == p(1)
        assert r1[2] == p(1)
        assert r1[3] == p(-1)
        assert r1[4] == p(-1)


    def test_p_types(self):
        """Testing some some types which used to fail"""
        x = np.array([1, 2, 3], dtype=np.int64)  # Used to fail but added catch all conversion to float
        assert p(x[0]) == p(1)
        # r1 = p(x)  # TODO Make p properly listable like mathematica
        # assert r1[0] == p(1)
        # assert r1[1] == p(2)
        # assert r1[2] == p(3)

