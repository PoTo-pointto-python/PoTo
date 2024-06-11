from __future__ import absolute_import, division, print_function
__metaclass__ = type
import jinja2
from units.compat import unittest
from ansible.template import AnsibleUndefined, _escape_backslashes, _count_newlines_from_end

class TestBackslashEscape(unittest.TestCase):
    test_data = (dict(template=u"{{ 'test2 %s' | format('\\1') }}", intermediate=u"{{ 'test2 %s' | format('\\\\1') }}", expectation=u'test2 \\1', args=dict()), dict(template=u"Test 2\\3: {{ '\\1 %s' | format('\\2') }}", intermediate=u"Test 2\\3: {{ '\\\\1 %s' | format('\\\\2') }}", expectation=u'Test 2\\3: \\1 \\2', args=dict()), dict(template=u"Test 2\\3: {{ 'test2 %s' | format('\\1') }}; \\done", intermediate=u"Test 2\\3: {{ 'test2 %s' | format('\\\\1') }}; \\done", expectation=u'Test 2\\3: test2 \\1; \\done', args=dict()), dict(template=u"{{ 'test2 %s' | format(var1) }}", intermediate=u"{{ 'test2 %s' | format(var1) }}", expectation=u'test2 \\1', args=dict(var1=u'\\1')), dict(template=u"Test 2\\3: {{ var1 | format('\\2') }}", intermediate=u"Test 2\\3: {{ var1 | format('\\\\2') }}", expectation=u'Test 2\\3: \\1 \\2', args=dict(var1=u'\\1 %s')))

    def setUp(self):
        self.env = jinja2.Environment()

    def test_backslash_escaping(self):
        for test in self.test_data:
            intermediate = _escape_backslashes(test['template'], self.env)
            self.assertEqual(intermediate, test['intermediate'])
            template = jinja2.Template(intermediate)
            args = test['args']
            self.assertEqual(template.render(**args), test['expectation'])

class TestCountNewlines(unittest.TestCase):

    def test_zero_length_string(self):
        self.assertEqual(_count_newlines_from_end(u''), 0)

    def test_short_string(self):
        self.assertEqual(_count_newlines_from_end(u'The quick\n'), 1)

    def test_one_newline(self):
        self.assertEqual(_count_newlines_from_end(u'The quick brown fox jumped over the lazy dog' * 1000 + u'\n'), 1)

    def test_multiple_newlines(self):
        self.assertEqual(_count_newlines_from_end(u'The quick brown fox jumped over the lazy dog' * 1000 + u'\n\n\n'), 3)

    def test_zero_newlines(self):
        self.assertEqual(_count_newlines_from_end(u'The quick brown fox jumped over the lazy dog' * 1000), 0)

    def test_all_newlines(self):
        self.assertEqual(_count_newlines_from_end(u'\n' * 10), 10)

    def test_mostly_newlines(self):
        self.assertEqual(_count_newlines_from_end(u'The quick brown fox jumped over the lazy dog' + u'\n' * 1000), 1000)

class TestAnsibleUndefined(unittest.TestCase):

    def test_getattr(self):
        val = AnsibleUndefined()
        self.assertIs(getattr(val, 'foo'), val)
        self.assertRaises(AttributeError, getattr, val, '__UNSAFE__')

def test_TestBackslashEscape_setUp():
    ret = TestBackslashEscape().setUp()

def test_TestBackslashEscape_test_backslash_escaping():
    ret = TestBackslashEscape().test_backslash_escaping()

def test_TestCountNewlines_test_zero_length_string():
    ret = TestCountNewlines().test_zero_length_string()

def test_TestCountNewlines_test_short_string():
    ret = TestCountNewlines().test_short_string()

def test_TestCountNewlines_test_one_newline():
    ret = TestCountNewlines().test_one_newline()

def test_TestCountNewlines_test_multiple_newlines():
    ret = TestCountNewlines().test_multiple_newlines()

def test_TestCountNewlines_test_zero_newlines():
    ret = TestCountNewlines().test_zero_newlines()

def test_TestCountNewlines_test_all_newlines():
    ret = TestCountNewlines().test_all_newlines()

def test_TestCountNewlines_test_mostly_newlines():
    ret = TestCountNewlines().test_mostly_newlines()

def test_TestAnsibleUndefined_test_getattr():
    ret = TestAnsibleUndefined().test_getattr()