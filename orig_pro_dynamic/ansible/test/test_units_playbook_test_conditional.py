from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from units.mock.loader import DictDataLoader
from units.compat.mock import MagicMock
from ansible.template import Templar
from ansible import errors
from ansible.playbook import conditional

class TestConditional(unittest.TestCase):

    def setUp(self):
        self.loader = DictDataLoader({})
        self.cond = conditional.Conditional(loader=self.loader)
        self.templar = Templar(loader=self.loader, variables={})

    def _eval_con(self, when=None, variables=None):
        when = when or []
        variables = variables or {}
        self.cond.when = when
        ret = self.cond.evaluate_conditional(self.templar, variables)
        return ret

    def test_false(self):
        when = [u'False']
        ret = self._eval_con(when, {})
        self.assertFalse(ret)

    def test_true(self):
        when = [u'True']
        ret = self._eval_con(when, {})
        self.assertTrue(ret)

    def test_true_boolean(self):
        self.cond.when = [True]
        m = MagicMock()
        ret = self.cond.evaluate_conditional(m, {})
        self.assertTrue(ret)
        self.assertFalse(m.is_template.called)

    def test_false_boolean(self):
        self.cond.when = [False]
        m = MagicMock()
        ret = self.cond.evaluate_conditional(m, {})
        self.assertFalse(ret)
        self.assertFalse(m.is_template.called)

    def test_undefined(self):
        when = [u'{{ some_undefined_thing }}']
        self.assertRaisesRegexp(errors.AnsibleError, "The conditional check '{{ some_undefined_thing }}' failed", self._eval_con, when, {})

    def test_defined(self):
        variables = {'some_defined_thing': True}
        when = [u'{{ some_defined_thing }}']
        ret = self._eval_con(when, variables)
        self.assertTrue(ret)

    def test_dict_defined_values(self):
        variables = {'dict_value': 1, 'some_defined_dict': {'key1': 'value1', 'key2': '{{ dict_value }}'}}
        when = [u'some_defined_dict']
        ret = self._eval_con(when, variables)
        self.assertTrue(ret)

    def test_dict_defined_values_is_defined(self):
        variables = {'dict_value': 1, 'some_defined_dict': {'key1': 'value1', 'key2': '{{ dict_value }}'}}
        when = [u'some_defined_dict.key1 is defined']
        ret = self._eval_con(when, variables)
        self.assertTrue(ret)

    def test_dict_defined_multiple_values_is_defined(self):
        variables = {'dict_value': 1, 'some_defined_dict': {'key1': 'value1', 'key2': '{{ dict_value }}'}}
        when = [u'some_defined_dict.key1 is defined', u'some_defined_dict.key2 is not undefined']
        ret = self._eval_con(when, variables)
        self.assertTrue(ret)

    def test_dict_undefined_values(self):
        variables = {'dict_value': 1, 'some_defined_dict_with_undefined_values': {'key1': 'value1', 'key2': '{{ dict_value }}', 'key3': '{{ undefined_dict_value }}'}}
        when = [u'some_defined_dict_with_undefined_values is defined']
        self.assertRaisesRegexp(errors.AnsibleError, "The conditional check 'some_defined_dict_with_undefined_values is defined' failed.", self._eval_con, when, variables)

    def test_nested_hostvars_undefined_values(self):
        variables = {'dict_value': 1, 'hostvars': {'host1': {'key1': 'value1', 'key2': '{{ dict_value }}'}, 'host2': '{{ dict_value }}', 'host3': '{{ undefined_dict_value }}'}, 'some_dict': {'some_dict_key1': '{{ hostvars["host3"] }}'}}
        when = [u"some_dict.some_dict_key1 == hostvars['host3']"]
        self.assertRaisesRegexp(errors.AnsibleError, "The conditional check 'some_dict.some_dict_key1 == hostvars\\['host3'\\]' failed", self._eval_con, when, variables)

    def test_dict_undefined_values_bare(self):
        variables = {'dict_value': 1, 'some_defined_dict_with_undefined_values': {'key1': 'value1', 'key2': '{{ dict_value }}', 'key3': '{{ undefined_dict_value }}'}}
        when = [u'some_defined_dict_with_undefined_values']
        self.assertRaisesRegexp(errors.AnsibleError, "The conditional check 'some_defined_dict_with_undefined_values' failed.", self._eval_con, when, variables)

    def test_dict_undefined_values_is_defined(self):
        variables = {'dict_value': 1, 'some_defined_dict_with_undefined_values': {'key1': 'value1', 'key2': '{{ dict_value }}', 'key3': '{{ undefined_dict_value }}'}}
        when = [u'some_defined_dict_with_undefined_values is defined']
        self.assertRaisesRegexp(errors.AnsibleError, "The conditional check 'some_defined_dict_with_undefined_values is defined' failed.", self._eval_con, when, variables)

    def test_is_defined(self):
        variables = {'some_defined_thing': True}
        when = [u'some_defined_thing is defined']
        ret = self._eval_con(when, variables)
        self.assertTrue(ret)

    def test_is_undefined(self):
        variables = {'some_defined_thing': True}
        when = [u'some_defined_thing is undefined']
        ret = self._eval_con(when, variables)
        self.assertFalse(ret)

    def test_is_undefined_and_defined(self):
        variables = {'some_defined_thing': True}
        when = [u'some_defined_thing is undefined', u'some_defined_thing is defined']
        ret = self._eval_con(when, variables)
        self.assertFalse(ret)

    def test_is_undefined_and_defined_reversed(self):
        variables = {'some_defined_thing': True}
        when = [u'some_defined_thing is defined', u'some_defined_thing is undefined']
        ret = self._eval_con(when, variables)
        self.assertFalse(ret)

    def test_is_not_undefined(self):
        variables = {'some_defined_thing': True}
        when = [u'some_defined_thing is not undefined']
        ret = self._eval_con(when, variables)
        self.assertTrue(ret)

    def test_is_not_defined(self):
        variables = {'some_defined_thing': True}
        when = [u'some_undefined_thing is not defined']
        ret = self._eval_con(when, variables)
        self.assertTrue(ret)

    def test_is_hostvars_quotes_is_defined(self):
        variables = {'hostvars': {'some_host': {}}, 'compare_targets_single': "hostvars['some_host']", 'compare_targets_double': 'hostvars["some_host"]', 'compare_targets': {'double': '{{ compare_targets_double }}', 'single': '{{ compare_targets_single }}'}}
        when = [u"hostvars['some_host'] is defined", u'hostvars["some_host"] is defined', u'{{ compare_targets.double }} is defined', u'{{ compare_targets.single }} is defined']
        ret = self._eval_con(when, variables)
        self.assertTrue(ret)

    def test_is_hostvars_quotes_is_defined_but_is_not_defined(self):
        variables = {'hostvars': {'some_host': {}}, 'compare_targets_single': "hostvars['some_host']", 'compare_targets_double': 'hostvars["some_host"]', 'compare_targets': {'double': '{{ compare_targets_double }}', 'single': '{{ compare_targets_single }}'}}
        when = [u"hostvars['some_host'] is defined", u'hostvars["some_host"] is defined', u'{{ compare_targets.triple }} is defined', u'{{ compare_targets.quadruple }} is defined']
        self.assertRaisesRegexp(errors.AnsibleError, "The conditional check '{{ compare_targets.triple }} is defined' failed", self._eval_con, when, variables)

    def test_is_hostvars_host_is_defined(self):
        variables = {'hostvars': {'some_host': {}}}
        when = [u"hostvars['some_host'] is defined"]
        ret = self._eval_con(when, variables)
        self.assertTrue(ret)

    def test_is_hostvars_host_undefined_is_defined(self):
        variables = {'hostvars': {'some_host': {}}}
        when = [u"hostvars['some_undefined_host'] is defined"]
        ret = self._eval_con(when, variables)
        self.assertFalse(ret)

    def test_is_hostvars_host_undefined_is_undefined(self):
        variables = {'hostvars': {'some_host': {}}}
        when = [u"hostvars['some_undefined_host'] is undefined"]
        ret = self._eval_con(when, variables)
        self.assertTrue(ret)

    def test_is_hostvars_host_undefined_is_not_defined(self):
        variables = {'hostvars': {'some_host': {}}}
        when = [u"hostvars['some_undefined_host'] is not defined"]
        ret = self._eval_con(when, variables)
        self.assertTrue(ret)

def test_TestConditional_setUp():
    ret = TestConditional().setUp()

def test_TestConditional__eval_con():
    ret = TestConditional()._eval_con()

def test_TestConditional_test_false():
    ret = TestConditional().test_false()

def test_TestConditional_test_true():
    ret = TestConditional().test_true()

def test_TestConditional_test_true_boolean():
    ret = TestConditional().test_true_boolean()

def test_TestConditional_test_false_boolean():
    ret = TestConditional().test_false_boolean()

def test_TestConditional_test_undefined():
    ret = TestConditional().test_undefined()

def test_TestConditional_test_defined():
    ret = TestConditional().test_defined()

def test_TestConditional_test_dict_defined_values():
    ret = TestConditional().test_dict_defined_values()

def test_TestConditional_test_dict_defined_values_is_defined():
    ret = TestConditional().test_dict_defined_values_is_defined()

def test_TestConditional_test_dict_defined_multiple_values_is_defined():
    ret = TestConditional().test_dict_defined_multiple_values_is_defined()

def test_TestConditional_test_dict_undefined_values():
    ret = TestConditional().test_dict_undefined_values()

def test_TestConditional_test_nested_hostvars_undefined_values():
    ret = TestConditional().test_nested_hostvars_undefined_values()

def test_TestConditional_test_dict_undefined_values_bare():
    ret = TestConditional().test_dict_undefined_values_bare()

def test_TestConditional_test_dict_undefined_values_is_defined():
    ret = TestConditional().test_dict_undefined_values_is_defined()

def test_TestConditional_test_is_defined():
    ret = TestConditional().test_is_defined()

def test_TestConditional_test_is_undefined():
    ret = TestConditional().test_is_undefined()

def test_TestConditional_test_is_undefined_and_defined():
    ret = TestConditional().test_is_undefined_and_defined()

def test_TestConditional_test_is_undefined_and_defined_reversed():
    ret = TestConditional().test_is_undefined_and_defined_reversed()

def test_TestConditional_test_is_not_undefined():
    ret = TestConditional().test_is_not_undefined()

def test_TestConditional_test_is_not_defined():
    ret = TestConditional().test_is_not_defined()

def test_TestConditional_test_is_hostvars_quotes_is_defined():
    ret = TestConditional().test_is_hostvars_quotes_is_defined()

def test_TestConditional_test_is_hostvars_quotes_is_defined_but_is_not_defined():
    ret = TestConditional().test_is_hostvars_quotes_is_defined_but_is_not_defined()

def test_TestConditional_test_is_hostvars_host_is_defined():
    ret = TestConditional().test_is_hostvars_host_is_defined()

def test_TestConditional_test_is_hostvars_host_undefined_is_defined():
    ret = TestConditional().test_is_hostvars_host_undefined_is_defined()

def test_TestConditional_test_is_hostvars_host_undefined_is_undefined():
    ret = TestConditional().test_is_hostvars_host_undefined_is_undefined()

def test_TestConditional_test_is_hostvars_host_undefined_is_not_defined():
    ret = TestConditional().test_is_hostvars_host_undefined_is_not_defined()