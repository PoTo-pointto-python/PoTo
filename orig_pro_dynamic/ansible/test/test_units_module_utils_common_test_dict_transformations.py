from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from ansible.module_utils.common.dict_transformations import _camel_to_snake, _snake_to_camel, camel_dict_to_snake_dict, dict_merge
EXPECTED_SNAKIFICATION = {'alllower': 'alllower', 'TwoWords': 'two_words', 'AllUpperAtEND': 'all_upper_at_end', 'AllUpperButPLURALs': 'all_upper_but_plurals', 'TargetGroupARNs': 'target_group_arns', 'HTTPEndpoints': 'http_endpoints', 'PLURALs': 'plurals'}
EXPECTED_REVERSIBLE = {'TwoWords': 'two_words', 'AllUpperAtEND': 'all_upper_at_e_n_d', 'AllUpperButPLURALs': 'all_upper_but_p_l_u_r_a_ls', 'TargetGroupARNs': 'target_group_a_r_ns', 'HTTPEndpoints': 'h_t_t_p_endpoints', 'PLURALs': 'p_l_u_r_a_ls'}

class CamelToSnakeTestCase(unittest.TestCase):

    def test_camel_to_snake(self):
        for (k, v) in EXPECTED_SNAKIFICATION.items():
            self.assertEqual(_camel_to_snake(k), v)

    def test_reversible_camel_to_snake(self):
        for (k, v) in EXPECTED_REVERSIBLE.items():
            self.assertEqual(_camel_to_snake(k, reversible=True), v)

class SnakeToCamelTestCase(unittest.TestCase):

    def test_snake_to_camel_reversed(self):
        for (k, v) in EXPECTED_REVERSIBLE.items():
            self.assertEqual(_snake_to_camel(v, capitalize_first=True), k)

class CamelToSnakeAndBackTestCase(unittest.TestCase):

    def test_camel_to_snake_and_back(self):
        for (k, v) in EXPECTED_REVERSIBLE.items():
            self.assertEqual(_snake_to_camel(_camel_to_snake(k, reversible=True), capitalize_first=True), k)

class CamelDictToSnakeDictTestCase(unittest.TestCase):

    def test_ignore_list(self):
        camel_dict = dict(Hello=dict(One='one', Two='two'), World=dict(Three='three', Four='four'))
        snake_dict = camel_dict_to_snake_dict(camel_dict, ignore_list='World')
        self.assertEqual(snake_dict['hello'], dict(one='one', two='two'))
        self.assertEqual(snake_dict['world'], dict(Three='three', Four='four'))

class DictMergeTestCase(unittest.TestCase):

    def test_dict_merge(self):
        base = dict(obj2=dict(), b1=True, b2=False, b3=False, one=1, two=2, three=3, obj1=dict(key1=1, key2=2), l1=[1, 3], l2=[1, 2, 3], l4=[4], nested=dict(n1=dict(n2=2)))
        other = dict(b1=True, b2=False, b3=True, b4=True, one=1, three=4, four=4, obj1=dict(key1=2), l1=[2, 1], l2=[3, 2, 1], l3=[1], nested=dict(n1=dict(n2=2, n3=3)))
        result = dict_merge(base, other)
        self.assertTrue('one' in result)
        self.assertTrue('two' in result)
        self.assertEqual(result['three'], 4)
        self.assertEqual(result['four'], 4)
        self.assertTrue('obj1' in result)
        self.assertTrue('key1' in result['obj1'])
        self.assertTrue('key2' in result['obj1'])
        self.assertEqual(result['l1'], [2, 1])
        self.assertTrue('l2' in result)
        self.assertEqual(result['l3'], [1])
        self.assertTrue('l4' in result)
        self.assertTrue('obj1' in result)
        self.assertEqual(result['obj1']['key1'], 2)
        self.assertTrue('key2' in result['obj1'])
        self.assertTrue('b1' in result)
        self.assertTrue('b2' in result)
        self.assertTrue(result['b3'])
        self.assertTrue(result['b4'])

class AzureIncidentalTestCase(unittest.TestCase):

    def test_dict_merge_invalid_dict(self):
        """ if b is not a dict, return b """
        res = dict_merge({}, None)
        self.assertEqual(res, None)

    def test_merge_sub_dicts(self):
        """merge sub dicts """
        a = {'a': {'a1': 1}}
        b = {'a': {'b1': 2}}
        c = {'a': {'a1': 1, 'b1': 2}}
        res = dict_merge(a, b)
        self.assertEqual(res, c)

def test_CamelToSnakeTestCase_test_camel_to_snake():
    ret = CamelToSnakeTestCase().test_camel_to_snake()

def test_CamelToSnakeTestCase_test_reversible_camel_to_snake():
    ret = CamelToSnakeTestCase().test_reversible_camel_to_snake()

def test_SnakeToCamelTestCase_test_snake_to_camel_reversed():
    ret = SnakeToCamelTestCase().test_snake_to_camel_reversed()

def test_CamelToSnakeAndBackTestCase_test_camel_to_snake_and_back():
    ret = CamelToSnakeAndBackTestCase().test_camel_to_snake_and_back()

def test_CamelDictToSnakeDictTestCase_test_ignore_list():
    ret = CamelDictToSnakeDictTestCase().test_ignore_list()

def test_DictMergeTestCase_test_dict_merge():
    ret = DictMergeTestCase().test_dict_merge()

def test_AzureIncidentalTestCase_test_dict_merge_invalid_dict():
    ret = AzureIncidentalTestCase().test_dict_merge_invalid_dict()

def test_AzureIncidentalTestCase_test_merge_sub_dicts():
    ret = AzureIncidentalTestCase().test_merge_sub_dicts()