from __future__ import absolute_import, division, print_function
__metaclass__ = type
import sys
from collections import defaultdict
from units.compat import unittest
from ansible.template.safe_eval import safe_eval

class TestSafeEval(unittest.TestCase):

    def test_safe_eval_usage(self):
        for locals_vars in (dict(), defaultdict(dict)):
            self.assertEqual(safe_eval('True', locals=locals_vars), True)
            self.assertEqual(safe_eval('False', locals=locals_vars), False)
            self.assertEqual(safe_eval('0', locals=locals_vars), 0)
            self.assertEqual(safe_eval('[]', locals=locals_vars), [])
            self.assertEqual(safe_eval('{}', locals=locals_vars), {})

    @unittest.skipUnless(sys.version_info[:2] >= (2, 7), 'Python 2.6 has no set literals')
    def test_set_literals(self):
        self.assertEqual(safe_eval('{0}'), set([0]))

def test_TestSafeEval_test_safe_eval_usage():
    ret = TestSafeEval().test_safe_eval_usage()

def test_TestSafeEval_test_set_literals():
    ret = TestSafeEval().test_set_literals()