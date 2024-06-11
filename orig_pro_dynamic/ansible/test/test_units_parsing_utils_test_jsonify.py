from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from ansible.parsing.utils.jsonify import jsonify

class TestJsonify(unittest.TestCase):

    def test_jsonify_simple(self):
        self.assertEqual(jsonify(dict(a=1, b=2, c=3)), '{"a": 1, "b": 2, "c": 3}')

    def test_jsonify_simple_format(self):
        res = jsonify(dict(a=1, b=2, c=3), format=True)
        cleaned = ''.join([x.strip() for x in res.splitlines()])
        self.assertEqual(cleaned, '{"a": 1,"b": 2,"c": 3}')

    def test_jsonify_unicode(self):
        self.assertEqual(jsonify(dict(toshio=u'くらとみ')), u'{"toshio": "くらとみ"}')

    def test_jsonify_empty(self):
        self.assertEqual(jsonify(None), '{}')

def test_TestJsonify_test_jsonify_simple():
    ret = TestJsonify().test_jsonify_simple()

def test_TestJsonify_test_jsonify_simple_format():
    ret = TestJsonify().test_jsonify_simple_format()

def test_TestJsonify_test_jsonify_unicode():
    ret = TestJsonify().test_jsonify_unicode()

def test_TestJsonify_test_jsonify_empty():
    ret = TestJsonify().test_jsonify_empty()