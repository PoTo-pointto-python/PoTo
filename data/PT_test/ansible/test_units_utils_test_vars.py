from __future__ import absolute_import, division, print_function
__metaclass__ = type
from collections import defaultdict
from units.compat import mock, unittest
from ansible.errors import AnsibleError
from ansible.utils.vars import combine_vars, merge_hash

class TestVariableUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    combine_vars_merge_data = (dict(a=dict(a=1), b=dict(b=2), result=dict(a=1, b=2)), dict(a=dict(a=1, c=dict(foo='bar')), b=dict(b=2, c=dict(baz='bam')), result=dict(a=1, b=2, c=dict(foo='bar', baz='bam'))), dict(a=defaultdict(a=1, c=defaultdict(foo='bar')), b=dict(b=2, c=dict(baz='bam')), result=defaultdict(a=1, b=2, c=defaultdict(foo='bar', baz='bam'))))
    combine_vars_replace_data = (dict(a=dict(a=1), b=dict(b=2), result=dict(a=1, b=2)), dict(a=dict(a=1, c=dict(foo='bar')), b=dict(b=2, c=dict(baz='bam')), result=dict(a=1, b=2, c=dict(baz='bam'))), dict(a=defaultdict(a=1, c=dict(foo='bar')), b=dict(b=2, c=defaultdict(baz='bam')), result=defaultdict(a=1, b=2, c=defaultdict(baz='bam'))))

    def test_combine_vars_improper_args(self):
        with mock.patch('ansible.constants.DEFAULT_HASH_BEHAVIOUR', 'replace'):
            with self.assertRaises(AnsibleError):
                combine_vars([1, 2, 3], dict(a=1))
            with self.assertRaises(AnsibleError):
                combine_vars(dict(a=1), [1, 2, 3])
        with mock.patch('ansible.constants.DEFAULT_HASH_BEHAVIOUR', 'merge'):
            with self.assertRaises(AnsibleError):
                combine_vars([1, 2, 3], dict(a=1))
            with self.assertRaises(AnsibleError):
                combine_vars(dict(a=1), [1, 2, 3])

    def test_combine_vars_replace(self):
        with mock.patch('ansible.constants.DEFAULT_HASH_BEHAVIOUR', 'replace'):
            for test in self.combine_vars_replace_data:
                self.assertEqual(combine_vars(test['a'], test['b']), test['result'])

    def test_combine_vars_merge(self):
        with mock.patch('ansible.constants.DEFAULT_HASH_BEHAVIOUR', 'merge'):
            for test in self.combine_vars_merge_data:
                self.assertEqual(combine_vars(test['a'], test['b']), test['result'])
    merge_hash_data = {'low_prio': {'a': {"a'": {'x': 'low_value', 'y': 'low_value', 'list': ['low_value']}}, 'b': [1, 1, 2, 3]}, 'high_prio': {'a': {"a'": {'y': 'high_value', 'z': 'high_value', 'list': ['high_value']}}, 'b': [3, 4, 4, {'5': 'value'}]}}

    def test_merge_hash_simple(self):
        for test in self.combine_vars_merge_data:
            self.assertEqual(merge_hash(test['a'], test['b']), test['result'])
        low = self.merge_hash_data['low_prio']
        high = self.merge_hash_data['high_prio']
        expected = {'a': {"a'": {'x': 'low_value', 'y': 'high_value', 'z': 'high_value', 'list': ['high_value']}}, 'b': high['b']}
        self.assertEqual(merge_hash(low, high), expected)

    def test_merge_hash_non_recursive_and_list_replace(self):
        low = self.merge_hash_data['low_prio']
        high = self.merge_hash_data['high_prio']
        expected = high
        self.assertEqual(merge_hash(low, high, False, 'replace'), expected)

    def test_merge_hash_non_recursive_and_list_keep(self):
        low = self.merge_hash_data['low_prio']
        high = self.merge_hash_data['high_prio']
        expected = {'a': high['a'], 'b': low['b']}
        self.assertEqual(merge_hash(low, high, False, 'keep'), expected)

    def test_merge_hash_non_recursive_and_list_append(self):
        low = self.merge_hash_data['low_prio']
        high = self.merge_hash_data['high_prio']
        expected = {'a': high['a'], 'b': low['b'] + high['b']}
        self.assertEqual(merge_hash(low, high, False, 'append'), expected)

    def test_merge_hash_non_recursive_and_list_prepend(self):
        low = self.merge_hash_data['low_prio']
        high = self.merge_hash_data['high_prio']
        expected = {'a': high['a'], 'b': high['b'] + low['b']}
        self.assertEqual(merge_hash(low, high, False, 'prepend'), expected)

    def test_merge_hash_non_recursive_and_list_append_rp(self):
        low = self.merge_hash_data['low_prio']
        high = self.merge_hash_data['high_prio']
        expected = {'a': high['a'], 'b': [1, 1, 2] + high['b']}
        self.assertEqual(merge_hash(low, high, False, 'append_rp'), expected)

    def test_merge_hash_non_recursive_and_list_prepend_rp(self):
        low = self.merge_hash_data['low_prio']
        high = self.merge_hash_data['high_prio']
        expected = {'a': high['a'], 'b': high['b'] + [1, 1, 2]}
        self.assertEqual(merge_hash(low, high, False, 'prepend_rp'), expected)

    def test_merge_hash_recursive_and_list_replace(self):
        low = self.merge_hash_data['low_prio']
        high = self.merge_hash_data['high_prio']
        expected = {'a': {"a'": {'x': 'low_value', 'y': 'high_value', 'z': 'high_value', 'list': ['high_value']}}, 'b': high['b']}
        self.assertEqual(merge_hash(low, high, True, 'replace'), expected)

    def test_merge_hash_recursive_and_list_keep(self):
        low = self.merge_hash_data['low_prio']
        high = self.merge_hash_data['high_prio']
        expected = {'a': {"a'": {'x': 'low_value', 'y': 'high_value', 'z': 'high_value', 'list': ['low_value']}}, 'b': low['b']}
        self.assertEqual(merge_hash(low, high, True, 'keep'), expected)

    def test_merge_hash_recursive_and_list_append(self):
        low = self.merge_hash_data['low_prio']
        high = self.merge_hash_data['high_prio']
        expected = {'a': {"a'": {'x': 'low_value', 'y': 'high_value', 'z': 'high_value', 'list': ['low_value', 'high_value']}}, 'b': low['b'] + high['b']}
        self.assertEqual(merge_hash(low, high, True, 'append'), expected)

    def test_merge_hash_recursive_and_list_prepend(self):
        low = self.merge_hash_data['low_prio']
        high = self.merge_hash_data['high_prio']
        expected = {'a': {"a'": {'x': 'low_value', 'y': 'high_value', 'z': 'high_value', 'list': ['high_value', 'low_value']}}, 'b': high['b'] + low['b']}
        self.assertEqual(merge_hash(low, high, True, 'prepend'), expected)

    def test_merge_hash_recursive_and_list_append_rp(self):
        low = self.merge_hash_data['low_prio']
        high = self.merge_hash_data['high_prio']
        expected = {'a': {"a'": {'x': 'low_value', 'y': 'high_value', 'z': 'high_value', 'list': ['low_value', 'high_value']}}, 'b': [1, 1, 2] + high['b']}
        self.assertEqual(merge_hash(low, high, True, 'append_rp'), expected)

    def test_merge_hash_recursive_and_list_prepend_rp(self):
        low = self.merge_hash_data['low_prio']
        high = self.merge_hash_data['high_prio']
        expected = {'a': {"a'": {'x': 'low_value', 'y': 'high_value', 'z': 'high_value', 'list': ['high_value', 'low_value']}}, 'b': high['b'] + [1, 1, 2]}
        self.assertEqual(merge_hash(low, high, True, 'prepend_rp'), expected)

def test_TestVariableUtils_setUp():
    ret = TestVariableUtils().setUp()

def test_TestVariableUtils_tearDown():
    ret = TestVariableUtils().tearDown()

def test_TestVariableUtils_test_combine_vars_improper_args():
    ret = TestVariableUtils().test_combine_vars_improper_args()

def test_TestVariableUtils_test_combine_vars_replace():
    ret = TestVariableUtils().test_combine_vars_replace()

def test_TestVariableUtils_test_combine_vars_merge():
    ret = TestVariableUtils().test_combine_vars_merge()

def test_TestVariableUtils_test_merge_hash_simple():
    ret = TestVariableUtils().test_merge_hash_simple()

def test_TestVariableUtils_test_merge_hash_non_recursive_and_list_replace():
    ret = TestVariableUtils().test_merge_hash_non_recursive_and_list_replace()

def test_TestVariableUtils_test_merge_hash_non_recursive_and_list_keep():
    ret = TestVariableUtils().test_merge_hash_non_recursive_and_list_keep()

def test_TestVariableUtils_test_merge_hash_non_recursive_and_list_append():
    ret = TestVariableUtils().test_merge_hash_non_recursive_and_list_append()

def test_TestVariableUtils_test_merge_hash_non_recursive_and_list_prepend():
    ret = TestVariableUtils().test_merge_hash_non_recursive_and_list_prepend()

def test_TestVariableUtils_test_merge_hash_non_recursive_and_list_append_rp():
    ret = TestVariableUtils().test_merge_hash_non_recursive_and_list_append_rp()

def test_TestVariableUtils_test_merge_hash_non_recursive_and_list_prepend_rp():
    ret = TestVariableUtils().test_merge_hash_non_recursive_and_list_prepend_rp()

def test_TestVariableUtils_test_merge_hash_recursive_and_list_replace():
    ret = TestVariableUtils().test_merge_hash_recursive_and_list_replace()

def test_TestVariableUtils_test_merge_hash_recursive_and_list_keep():
    ret = TestVariableUtils().test_merge_hash_recursive_and_list_keep()

def test_TestVariableUtils_test_merge_hash_recursive_and_list_append():
    ret = TestVariableUtils().test_merge_hash_recursive_and_list_append()

def test_TestVariableUtils_test_merge_hash_recursive_and_list_prepend():
    ret = TestVariableUtils().test_merge_hash_recursive_and_list_prepend()

def test_TestVariableUtils_test_merge_hash_recursive_and_list_append_rp():
    ret = TestVariableUtils().test_merge_hash_recursive_and_list_append_rp()

def test_TestVariableUtils_test_merge_hash_recursive_and_list_prepend_rp():
    ret = TestVariableUtils().test_merge_hash_recursive_and_list_prepend_rp()