from __future__ import absolute_import, division, print_function
__metaclass__ = type
import string
import textwrap
from ansible import constants as C
from units.compat import mock
from units.compat import unittest
from ansible.module_utils.six import string_types
from ansible.module_utils._text import to_text
from units.mock.path import mock_unfrackpath_noop
from ansible.inventory.manager import InventoryManager, split_host_pattern
from units.mock.loader import DictDataLoader

class TestInventory(unittest.TestCase):
    patterns = {'a': ['a'], 'a, b': ['a', 'b'], 'a , b': ['a', 'b'], ' a,b ,c[1:2] ': ['a', 'b', 'c[1:2]'], '9a01:7f8:191:7701::9': ['9a01:7f8:191:7701::9'], '9a01:7f8:191:7701::9,9a01:7f8:191:7701::9': ['9a01:7f8:191:7701::9', '9a01:7f8:191:7701::9'], '9a01:7f8:191:7701::9,9a01:7f8:191:7701::9,foo': ['9a01:7f8:191:7701::9', '9a01:7f8:191:7701::9', 'foo'], 'foo[1:2]': ['foo[1:2]'], 'a::b': ['a::b'], 'a:b': ['a', 'b'], ' a : b ': ['a', 'b'], 'foo:bar:baz[1:2]': ['foo', 'bar', 'baz[1:2]'], 'a,,b': ['a', 'b'], 'a,  ,b,,c, ,': ['a', 'b', 'c'], ',': [], '': []}
    pattern_lists = [[['a'], ['a']], [['a', 'b'], ['a', 'b']], [['a, b'], ['a', 'b']], [['9a01:7f8:191:7701::9', '9a01:7f8:191:7701::9,foo'], ['9a01:7f8:191:7701::9', '9a01:7f8:191:7701::9', 'foo']]]
    subscripts = {'a': [('a', None), list(string.ascii_letters)], 'a[0]': [('a', (0, None)), ['a']], 'a[1]': [('a', (1, None)), ['b']], 'a[2:3]': [('a', (2, 3)), ['c', 'd']], 'a[-1]': [('a', (-1, None)), ['Z']], 'a[-2]': [('a', (-2, None)), ['Y']], 'a[48:]': [('a', (48, -1)), ['W', 'X', 'Y', 'Z']], 'a[49:]': [('a', (49, -1)), ['X', 'Y', 'Z']], 'a[1:]': [('a', (1, -1)), list(string.ascii_letters[1:])]}
    ranges_to_expand = {'a[1:2]': ['a1', 'a2'], 'a[1:10:2]': ['a1', 'a3', 'a5', 'a7', 'a9'], 'a[a:b]': ['aa', 'ab'], 'a[a:i:3]': ['aa', 'ad', 'ag'], 'a[a:b][c:d]': ['aac', 'aad', 'abc', 'abd'], 'a[0:1][2:3]': ['a02', 'a03', 'a12', 'a13'], 'a[a:b][2:3]': ['aa2', 'aa3', 'ab2', 'ab3']}

    def setUp(self):
        fake_loader = DictDataLoader({})
        self.i = InventoryManager(loader=fake_loader, sources=[None])

    def test_split_patterns(self):
        for p in self.patterns:
            r = self.patterns[p]
            self.assertEqual(r, split_host_pattern(p))
        for (p, r) in self.pattern_lists:
            self.assertEqual(r, split_host_pattern(p))

    def test_ranges(self):
        for s in self.subscripts:
            r = self.subscripts[s]
            self.assertEqual(r[0], self.i._split_subscript(s))
            self.assertEqual(r[1], self.i._apply_subscript(list(string.ascii_letters), r[0][1]))

class TestInventoryPlugins(unittest.TestCase):

    def test_empty_inventory(self):
        inventory = self._get_inventory('')
        self.assertIn('all', inventory.groups)
        self.assertIn('ungrouped', inventory.groups)
        self.assertFalse(inventory.groups['all'].get_hosts())
        self.assertFalse(inventory.groups['ungrouped'].get_hosts())

    def test_ini(self):
        self._test_default_groups('\n            host1\n            host2\n            host3\n            [servers]\n            host3\n            host4\n            host5\n            ')

    def test_ini_explicit_ungrouped(self):
        self._test_default_groups('\n            [ungrouped]\n            host1\n            host2\n            host3\n            [servers]\n            host3\n            host4\n            host5\n            ')

    def test_ini_variables_stringify(self):
        values = ['string', 'no', 'No', 'false', 'FALSE', [], False, 0]
        inventory_content = 'host1 '
        inventory_content += ' '.join(['var%s=%s' % (i, to_text(x)) for (i, x) in enumerate(values)])
        inventory = self._get_inventory(inventory_content)
        variables = inventory.get_host('host1').vars
        for i in range(len(values)):
            if isinstance(values[i], string_types):
                self.assertIsInstance(variables['var%s' % i], string_types)
            else:
                self.assertIsInstance(variables['var%s' % i], type(values[i]))

    @mock.patch('ansible.inventory.manager.unfrackpath', mock_unfrackpath_noop)
    @mock.patch('os.path.exists', lambda x: True)
    @mock.patch('os.access', lambda x, y: True)
    def test_yaml_inventory(self, filename='test.yaml'):
        inventory_content = {filename: textwrap.dedent('        ---\n        all:\n            hosts:\n                test1:\n                test2:\n        ')}
        C.INVENTORY_ENABLED = ['yaml']
        fake_loader = DictDataLoader(inventory_content)
        im = InventoryManager(loader=fake_loader, sources=filename)
        self.assertTrue(im._inventory.hosts)
        self.assertIn('test1', im._inventory.hosts)
        self.assertIn('test2', im._inventory.hosts)
        self.assertIn(im._inventory.get_host('test1'), im._inventory.groups['all'].hosts)
        self.assertIn(im._inventory.get_host('test2'), im._inventory.groups['all'].hosts)
        self.assertEqual(len(im._inventory.groups['all'].hosts), 2)
        self.assertIn(im._inventory.get_host('test1'), im._inventory.groups['ungrouped'].hosts)
        self.assertIn(im._inventory.get_host('test2'), im._inventory.groups['ungrouped'].hosts)
        self.assertEqual(len(im._inventory.groups['ungrouped'].hosts), 2)

    def _get_inventory(self, inventory_content):
        fake_loader = DictDataLoader({__file__: inventory_content})
        return InventoryManager(loader=fake_loader, sources=[__file__])

    def _test_default_groups(self, inventory_content):
        inventory = self._get_inventory(inventory_content)
        self.assertIn('all', inventory.groups)
        self.assertIn('ungrouped', inventory.groups)
        all_hosts = set((host.name for host in inventory.groups['all'].get_hosts()))
        self.assertEqual(set(['host1', 'host2', 'host3', 'host4', 'host5']), all_hosts)
        ungrouped_hosts = set((host.name for host in inventory.groups['ungrouped'].get_hosts()))
        self.assertEqual(set(['host1', 'host2']), ungrouped_hosts)
        servers_hosts = set((host.name for host in inventory.groups['servers'].get_hosts()))
        self.assertEqual(set(['host3', 'host4', 'host5']), servers_hosts)

def test_TestInventory_setUp():
    ret = TestInventory().setUp()

def test_TestInventory_test_split_patterns():
    ret = TestInventory().test_split_patterns()

def test_TestInventory_test_ranges():
    ret = TestInventory().test_ranges()

def test_TestInventoryPlugins_test_empty_inventory():
    ret = TestInventoryPlugins().test_empty_inventory()

def test_TestInventoryPlugins_test_ini():
    ret = TestInventoryPlugins().test_ini()

def test_TestInventoryPlugins_test_ini_explicit_ungrouped():
    ret = TestInventoryPlugins().test_ini_explicit_ungrouped()

def test_TestInventoryPlugins_test_ini_variables_stringify():
    ret = TestInventoryPlugins().test_ini_variables_stringify()

def test_TestInventoryPlugins_test_yaml_inventory():
    ret = TestInventoryPlugins().test_yaml_inventory()

def test_TestInventoryPlugins__get_inventory():
    ret = TestInventoryPlugins()._get_inventory()

def test_TestInventoryPlugins__test_default_groups():
    ret = TestInventoryPlugins()._test_default_groups()