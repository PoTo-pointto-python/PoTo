from __future__ import absolute_import, division, print_function
__metaclass__ = type
import unittest
from ansible.utils.helpers import pct_to_int

class TestHelpers(unittest.TestCase):

    def test_pct_to_int(self):
        self.assertEqual(pct_to_int(1, 100), 1)
        self.assertEqual(pct_to_int(-1, 100), -1)
        self.assertEqual(pct_to_int('1%', 10), 1)
        self.assertEqual(pct_to_int('1%', 10, 0), 0)
        self.assertEqual(pct_to_int('1', 100), 1)
        self.assertEqual(pct_to_int('10%', 100), 10)

def test_TestHelpers_test_pct_to_int():
    ret = TestHelpers().test_pct_to_int()