from __future__ import absolute_import, division, print_function
__metaclass__ = type
import json
import re
import textwrap
import types
from units.compat import unittest
from units.compat.mock import MagicMock
from ansible.plugins.callback import CallbackBase

class TestCallback(unittest.TestCase):

    def test_init(self):
        CallbackBase()

    def test_display(self):
        display_mock = MagicMock()
        display_mock.verbosity = 0
        cb = CallbackBase(display=display_mock)
        self.assertIs(cb._display, display_mock)

    def test_display_verbose(self):
        display_mock = MagicMock()
        display_mock.verbosity = 5
        cb = CallbackBase(display=display_mock)
        self.assertIs(cb._display, display_mock)

class TestCallbackResults(unittest.TestCase):

    def test_get_item_label(self):
        cb = CallbackBase()
        results = {'item': 'some_item'}
        res = cb._get_item_label(results)
        self.assertEqual(res, 'some_item')

    def test_get_item_label_no_log(self):
        cb = CallbackBase()
        results = {'item': 'some_item', '_ansible_no_log': True}
        res = cb._get_item_label(results)
        self.assertEqual(res, '(censored due to no_log)')
        results = {'item': 'some_item', '_ansible_no_log': False}
        res = cb._get_item_label(results)
        self.assertEqual(res, 'some_item')

    def test_clean_results_debug_task(self):
        cb = CallbackBase()
        result = {'item': 'some_item', 'invocation': 'foo --bar whatever [some_json]', 'a': 'a single a in result note letter a is in invocation', 'b': 'a single b in result note letter b is not in invocation', 'changed': True}
        cb._clean_results(result, 'debug')
        self.assertTrue('a' in result)
        self.assertTrue('b' in result)
        self.assertFalse('invocation' in result)
        self.assertFalse('changed' in result)

    def test_clean_results_debug_task_no_invocation(self):
        cb = CallbackBase()
        result = {'item': 'some_item', 'a': 'a single a in result note letter a is in invocation', 'b': 'a single b in result note letter b is not in invocation', 'changed': True}
        cb._clean_results(result, 'debug')
        self.assertTrue('a' in result)
        self.assertTrue('b' in result)
        self.assertFalse('changed' in result)
        self.assertFalse('invocation' in result)

    def test_clean_results_debug_task_empty_results(self):
        cb = CallbackBase()
        result = {}
        cb._clean_results(result, 'debug')
        self.assertFalse('invocation' in result)
        self.assertEqual(len(result), 0)

    def test_clean_results(self):
        cb = CallbackBase()
        result = {'item': 'some_item', 'invocation': 'foo --bar whatever [some_json]', 'a': 'a single a in result note letter a is in invocation', 'b': 'a single b in result note letter b is not in invocation', 'changed': True}
        expected_result = result.copy()
        cb._clean_results(result, 'ebug')
        self.assertEqual(result, expected_result)

class TestCallbackDumpResults(object):

    def test_internal_keys(self):
        cb = CallbackBase()
        result = {'item': 'some_item', '_ansible_some_var': 'SENTINEL', 'testing_ansible_out': 'should_be_left_in LEFTIN', 'invocation': 'foo --bar whatever [some_json]', 'some_dict_key': {'a_sub_dict_for_key': 'baz'}, 'bad_dict_key': {'_ansible_internal_blah': 'SENTINEL'}, 'changed': True}
        json_out = cb._dump_results(result)
        assert '"_ansible_' not in json_out
        assert 'SENTINEL' not in json_out
        assert 'LEFTIN' in json_out

    def test_exception(self):
        cb = CallbackBase()
        result = {'item': 'some_item LEFTIN', 'exception': ['frame1', 'SENTINEL']}
        json_out = cb._dump_results(result)
        assert 'SENTINEL' not in json_out
        assert 'exception' not in json_out
        assert 'LEFTIN' in json_out

    def test_verbose(self):
        cb = CallbackBase()
        result = {'item': 'some_item LEFTIN', '_ansible_verbose_always': 'chicane'}
        json_out = cb._dump_results(result)
        assert 'SENTINEL' not in json_out
        assert 'LEFTIN' in json_out

    def test_diff(self):
        cb = CallbackBase()
        result = {'item': 'some_item LEFTIN', 'diff': ['remove stuff', 'added LEFTIN'], '_ansible_verbose_always': 'chicane'}
        json_out = cb._dump_results(result)
        assert 'SENTINEL' not in json_out
        assert 'LEFTIN' in json_out

    def test_mixed_keys(self):
        cb = CallbackBase()
        result = {3: 'pi', 'tau': 6}
        json_out = cb._dump_results(result)
        round_trip_result = json.loads(json_out)
        assert len(round_trip_result) == 2
        assert '3' in round_trip_result
        assert 'tau' in round_trip_result
        assert round_trip_result['3'] == 'pi'
        assert round_trip_result['tau'] == 6

class TestCallbackDiff(unittest.TestCase):

    def setUp(self):
        self.cb = CallbackBase()

    def _strip_color(self, s):
        return re.sub('\x1b\\[[^m]*m', '', s)

    def test_difflist(self):
        difflist = [{'before': u'preface\nThe Before String\npostscript', 'after': u'preface\nThe After String\npostscript', 'before_header': u'just before', 'after_header': u'just after'}, {'before': u'preface\nThe Before String\npostscript', 'after': u'preface\nThe After String\npostscript'}, {'src_binary': 'chicane'}, {'dst_binary': 'chicanery'}, {'dst_larger': 1}, {'src_larger': 2}, {'prepared': u'what does prepared do?'}, {'before_header': u'just before'}, {'after_header': u'just after'}]
        res = self.cb._get_diff(difflist)
        self.assertIn(u'Before String', res)
        self.assertIn(u'After String', res)
        self.assertIn(u'just before', res)
        self.assertIn(u'just after', res)

    def test_simple_diff(self):
        self.assertMultiLineEqual(self._strip_color(self.cb._get_diff({'before_header': 'somefile.txt', 'after_header': 'generated from template somefile.j2', 'before': 'one\ntwo\nthree\n', 'after': 'one\nthree\nfour\n'})), textwrap.dedent('                --- before: somefile.txt\n                +++ after: generated from template somefile.j2\n                @@ -1,3 +1,3 @@\n                 one\n                -two\n                 three\n                +four\n\n            '))

    def test_new_file(self):
        self.assertMultiLineEqual(self._strip_color(self.cb._get_diff({'before_header': 'somefile.txt', 'after_header': 'generated from template somefile.j2', 'before': '', 'after': 'one\ntwo\nthree\n'})), textwrap.dedent('                --- before: somefile.txt\n                +++ after: generated from template somefile.j2\n                @@ -0,0 +1,3 @@\n                +one\n                +two\n                +three\n\n            '))

    def test_clear_file(self):
        self.assertMultiLineEqual(self._strip_color(self.cb._get_diff({'before_header': 'somefile.txt', 'after_header': 'generated from template somefile.j2', 'before': 'one\ntwo\nthree\n', 'after': ''})), textwrap.dedent('                --- before: somefile.txt\n                +++ after: generated from template somefile.j2\n                @@ -1,3 +0,0 @@\n                -one\n                -two\n                -three\n\n            '))

    def test_no_trailing_newline_before(self):
        self.assertMultiLineEqual(self._strip_color(self.cb._get_diff({'before_header': 'somefile.txt', 'after_header': 'generated from template somefile.j2', 'before': 'one\ntwo\nthree', 'after': 'one\ntwo\nthree\n'})), textwrap.dedent('                --- before: somefile.txt\n                +++ after: generated from template somefile.j2\n                @@ -1,3 +1,3 @@\n                 one\n                 two\n                -three\n                \\ No newline at end of file\n                +three\n\n            '))

    def test_no_trailing_newline_after(self):
        self.assertMultiLineEqual(self._strip_color(self.cb._get_diff({'before_header': 'somefile.txt', 'after_header': 'generated from template somefile.j2', 'before': 'one\ntwo\nthree\n', 'after': 'one\ntwo\nthree'})), textwrap.dedent('                --- before: somefile.txt\n                +++ after: generated from template somefile.j2\n                @@ -1,3 +1,3 @@\n                 one\n                 two\n                -three\n                +three\n                \\ No newline at end of file\n\n            '))

    def test_no_trailing_newline_both(self):
        self.assertMultiLineEqual(self.cb._get_diff({'before_header': 'somefile.txt', 'after_header': 'generated from template somefile.j2', 'before': 'one\ntwo\nthree', 'after': 'one\ntwo\nthree'}), '')

    def test_no_trailing_newline_both_with_some_changes(self):
        self.assertMultiLineEqual(self._strip_color(self.cb._get_diff({'before_header': 'somefile.txt', 'after_header': 'generated from template somefile.j2', 'before': 'one\ntwo\nthree', 'after': 'one\nfive\nthree'})), textwrap.dedent('                --- before: somefile.txt\n                +++ after: generated from template somefile.j2\n                @@ -1,3 +1,3 @@\n                 one\n                -two\n                +five\n                 three\n                \\ No newline at end of file\n\n            '))

    def test_diff_dicts(self):
        self.assertMultiLineEqual(self._strip_color(self.cb._get_diff({'before': dict(one=1, two=2, three=3), 'after': dict(one=1, three=3, four=4)})), textwrap.dedent('                --- before\n                +++ after\n                @@ -1,5 +1,5 @@\n                 {\n                +    "four": 4,\n                     "one": 1,\n                -    "three": 3,\n                -    "two": 2\n                +    "three": 3\n                 }\n\n            '))

    def test_diff_before_none(self):
        self.assertMultiLineEqual(self._strip_color(self.cb._get_diff({'before': None, 'after': 'one line\n'})), textwrap.dedent('                --- before\n                +++ after\n                @@ -0,0 +1 @@\n                +one line\n\n            '))

    def test_diff_after_none(self):
        self.assertMultiLineEqual(self._strip_color(self.cb._get_diff({'before': 'one line\n', 'after': None})), textwrap.dedent('                --- before\n                +++ after\n                @@ -1 +0,0 @@\n                -one line\n\n            '))

class TestCallbackOnMethods(unittest.TestCase):

    def _find_on_methods(self, callback):
        cb_dir = dir(callback)
        method_names = [x for x in cb_dir if '_on_' in x]
        methods = [getattr(callback, mn) for mn in method_names]
        return methods

    def test_are_methods(self):
        cb = CallbackBase()
        for method in self._find_on_methods(cb):
            self.assertIsInstance(method, types.MethodType)

    def test_on_any(self):
        cb = CallbackBase()
        cb.v2_on_any('whatever', some_keyword='blippy')
        cb.on_any('whatever', some_keyword='blippy')

def test_TestCallback_test_init():
    ret = TestCallback().test_init()

def test_TestCallback_test_display():
    ret = TestCallback().test_display()

def test_TestCallback_test_display_verbose():
    ret = TestCallback().test_display_verbose()

def test_TestCallbackResults_test_get_item_label():
    ret = TestCallbackResults().test_get_item_label()

def test_TestCallbackResults_test_get_item_label_no_log():
    ret = TestCallbackResults().test_get_item_label_no_log()

def test_TestCallbackResults_test_clean_results_debug_task():
    ret = TestCallbackResults().test_clean_results_debug_task()

def test_TestCallbackResults_test_clean_results_debug_task_no_invocation():
    ret = TestCallbackResults().test_clean_results_debug_task_no_invocation()

def test_TestCallbackResults_test_clean_results_debug_task_empty_results():
    ret = TestCallbackResults().test_clean_results_debug_task_empty_results()

def test_TestCallbackResults_test_clean_results():
    ret = TestCallbackResults().test_clean_results()

def test_TestCallbackDumpResults_test_internal_keys():
    ret = TestCallbackDumpResults().test_internal_keys()

def test_TestCallbackDumpResults_test_exception():
    ret = TestCallbackDumpResults().test_exception()

def test_TestCallbackDumpResults_test_verbose():
    ret = TestCallbackDumpResults().test_verbose()

def test_TestCallbackDumpResults_test_diff():
    ret = TestCallbackDumpResults().test_diff()

def test_TestCallbackDumpResults_test_mixed_keys():
    ret = TestCallbackDumpResults().test_mixed_keys()

def test_TestCallbackDiff_setUp():
    ret = TestCallbackDiff().setUp()

def test_TestCallbackDiff__strip_color():
    ret = TestCallbackDiff()._strip_color()

def test_TestCallbackDiff_test_difflist():
    ret = TestCallbackDiff().test_difflist()

def test_TestCallbackDiff_test_simple_diff():
    ret = TestCallbackDiff().test_simple_diff()

def test_TestCallbackDiff_test_new_file():
    ret = TestCallbackDiff().test_new_file()

def test_TestCallbackDiff_test_clear_file():
    ret = TestCallbackDiff().test_clear_file()

def test_TestCallbackDiff_test_no_trailing_newline_before():
    ret = TestCallbackDiff().test_no_trailing_newline_before()

def test_TestCallbackDiff_test_no_trailing_newline_after():
    ret = TestCallbackDiff().test_no_trailing_newline_after()

def test_TestCallbackDiff_test_no_trailing_newline_both():
    ret = TestCallbackDiff().test_no_trailing_newline_both()

def test_TestCallbackDiff_test_no_trailing_newline_both_with_some_changes():
    ret = TestCallbackDiff().test_no_trailing_newline_both_with_some_changes()

def test_TestCallbackDiff_test_diff_dicts():
    ret = TestCallbackDiff().test_diff_dicts()

def test_TestCallbackDiff_test_diff_before_none():
    ret = TestCallbackDiff().test_diff_before_none()

def test_TestCallbackDiff_test_diff_after_none():
    ret = TestCallbackDiff().test_diff_after_none()

def test_TestCallbackOnMethods__find_on_methods():
    ret = TestCallbackOnMethods()._find_on_methods()

def test_TestCallbackOnMethods_test_are_methods():
    ret = TestCallbackOnMethods().test_are_methods()

def test_TestCallbackOnMethods_test_on_any():
    ret = TestCallbackOnMethods().test_on_any()