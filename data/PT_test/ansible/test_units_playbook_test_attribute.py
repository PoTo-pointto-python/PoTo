from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from ansible.playbook.attribute import Attribute

class TestAttribute(unittest.TestCase):

    def setUp(self):
        self.one = Attribute(priority=100)
        self.two = Attribute(priority=0)

    def test_eq(self):
        self.assertTrue(self.one == self.one)
        self.assertFalse(self.one == self.two)

    def test_ne(self):
        self.assertFalse(self.one != self.one)
        self.assertTrue(self.one != self.two)

    def test_lt(self):
        self.assertFalse(self.one < self.one)
        self.assertTrue(self.one < self.two)
        self.assertFalse(self.two < self.one)

    def test_gt(self):
        self.assertFalse(self.one > self.one)
        self.assertFalse(self.one > self.two)
        self.assertTrue(self.two > self.one)

    def test_le(self):
        self.assertTrue(self.one <= self.one)
        self.assertTrue(self.one <= self.two)
        self.assertFalse(self.two <= self.one)

    def test_ge(self):
        self.assertTrue(self.one >= self.one)
        self.assertFalse(self.one >= self.two)
        self.assertTrue(self.two >= self.one)

def test_TestAttribute_setUp():
    ret = TestAttribute().setUp()

def test_TestAttribute_test_eq():
    ret = TestAttribute().test_eq()

def test_TestAttribute_test_ne():
    ret = TestAttribute().test_ne()

def test_TestAttribute_test_lt():
    ret = TestAttribute().test_lt()

def test_TestAttribute_test_gt():
    ret = TestAttribute().test_gt()

def test_TestAttribute_test_le():
    ret = TestAttribute().test_le()

def test_TestAttribute_test_ge():
    ret = TestAttribute().test_ge()