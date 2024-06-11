from __future__ import absolute_import, division, print_function
__metaclass__ = type
import unittest
from ansible.utils.shlex import shlex_split

class TestSplit(unittest.TestCase):

    def test_trivial(self):
        self.assertEqual(shlex_split('a b c'), ['a', 'b', 'c'])

    def test_unicode(self):
        self.assertEqual(shlex_split(u'a b č'), [u'a', u'b', u'č'])

    def test_quoted(self):
        self.assertEqual(shlex_split('"a b" c'), ['a b', 'c'])

    def test_comments(self):
        self.assertEqual(shlex_split('"a b" c # d', comments=True), ['a b', 'c'])

    def test_error(self):
        self.assertRaises(ValueError, shlex_split, 'a "b')

def test_TestSplit_test_trivial():
    ret = TestSplit().test_trivial()

def test_TestSplit_test_unicode():
    ret = TestSplit().test_unicode()

def test_TestSplit_test_quoted():
    ret = TestSplit().test_quoted()

def test_TestSplit_test_comments():
    ret = TestSplit().test_comments()

def test_TestSplit_test_error():
    ret = TestSplit().test_error()