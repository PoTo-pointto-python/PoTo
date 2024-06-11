from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from units.compat.mock import MagicMock
from ansible.template.vars import AnsibleJ2Vars

class TestVars(unittest.TestCase):

    def setUp(self):
        self.mock_templar = MagicMock(name='mock_templar')

    def test(self):
        ajvars = AnsibleJ2Vars(None, None)
        print(ajvars)

    def test_globals_empty_2_8(self):
        ajvars = AnsibleJ2Vars(self.mock_templar, {})
        res28 = self._dict_jinja28(ajvars)
        self.assertIsInstance(res28, dict)

    def test_globals_empty_2_9(self):
        ajvars = AnsibleJ2Vars(self.mock_templar, {})
        res29 = self._dict_jinja29(ajvars)
        self.assertIsInstance(res29, dict)

    def _assert_globals(self, res):
        self.assertIsInstance(res, dict)
        self.assertIn('foo', res)
        self.assertEqual(res['foo'], 'bar')

    def test_globals_2_8(self):
        ajvars = AnsibleJ2Vars(self.mock_templar, {'foo': 'bar', 'blip': [1, 2, 3]})
        res28 = self._dict_jinja28(ajvars)
        self._assert_globals(res28)

    def test_globals_2_9(self):
        ajvars = AnsibleJ2Vars(self.mock_templar, {'foo': 'bar', 'blip': [1, 2, 3]})
        res29 = self._dict_jinja29(ajvars)
        self._assert_globals(res29)

    def _dicts(self, ajvars):
        print(ajvars)
        res28 = self._dict_jinja28(ajvars)
        res29 = self._dict_jinja29(ajvars)
        print('res28: %s' % res28)
        print('res29: %s' % res29)
        return (res28, res29)

    def _dict_jinja28(self, *args, **kwargs):
        return dict(*args, **kwargs)

    def _dict_jinja29(self, the_vars):
        return dict(the_vars)

def test_TestVars_setUp():
    ret = TestVars().setUp()

def test_TestVars_test():
    ret = TestVars().test()

def test_TestVars_test_globals_empty_2_8():
    ret = TestVars().test_globals_empty_2_8()

def test_TestVars_test_globals_empty_2_9():
    ret = TestVars().test_globals_empty_2_9()

def test_TestVars__assert_globals():
    ret = TestVars()._assert_globals()

def test_TestVars_test_globals_2_8():
    ret = TestVars().test_globals_2_8()

def test_TestVars_test_globals_2_9():
    ret = TestVars().test_globals_2_9()

def test_TestVars__dicts():
    ret = TestVars()._dicts()

def test_TestVars__dict_jinja28():
    ret = TestVars()._dict_jinja28()

def test_TestVars__dict_jinja29():
    ret = TestVars()._dict_jinja29()