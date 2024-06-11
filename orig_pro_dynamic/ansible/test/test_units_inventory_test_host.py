from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pickle
from units.compat import unittest
from ansible.inventory.group import Group
from ansible.inventory.host import Host
from ansible.module_utils.six import string_types

class TestHost(unittest.TestCase):
    ansible_port = 22

    def setUp(self):
        self.hostA = Host('a')
        self.hostB = Host('b')

    def test_equality(self):
        self.assertEqual(self.hostA, self.hostA)
        self.assertNotEqual(self.hostA, self.hostB)
        self.assertNotEqual(self.hostA, Host('a'))

    def test_hashability(self):
        self.assertEqual(hash(self.hostA), hash(Host('a')))

    def test_get_vars(self):
        host_vars = self.hostA.get_vars()
        self.assertIsInstance(host_vars, dict)

    def test_repr(self):
        host_repr = repr(self.hostA)
        self.assertIsInstance(host_repr, string_types)

    def test_add_group(self):
        group = Group('some_group')
        group_len = len(self.hostA.groups)
        self.hostA.add_group(group)
        self.assertEqual(len(self.hostA.groups), group_len + 1)

    def test_get_groups(self):
        group = Group('some_group')
        self.hostA.add_group(group)
        groups = self.hostA.get_groups()
        self.assertEqual(len(groups), 1)
        for _group in groups:
            self.assertIsInstance(_group, Group)

    def test_equals_none(self):
        other = None
        self.hostA == other
        other == self.hostA
        self.hostA != other
        other != self.hostA
        self.assertNotEqual(self.hostA, other)

    def test_serialize(self):
        group = Group('some_group')
        self.hostA.add_group(group)
        data = self.hostA.serialize()
        self.assertIsInstance(data, dict)

    def test_serialize_then_deserialize(self):
        group = Group('some_group')
        self.hostA.add_group(group)
        hostA_data = self.hostA.serialize()
        hostA_clone = Host()
        hostA_clone.deserialize(hostA_data)
        self.assertEqual(self.hostA, hostA_clone)

    def test_set_state(self):
        group = Group('some_group')
        self.hostA.add_group(group)
        pickled_hostA = pickle.dumps(self.hostA)
        hostA_clone = pickle.loads(pickled_hostA)
        self.assertEqual(self.hostA, hostA_clone)

class TestHostWithPort(TestHost):
    ansible_port = 8822

    def setUp(self):
        self.hostA = Host(name='a', port=self.ansible_port)
        self.hostB = Host(name='b', port=self.ansible_port)

    def test_get_vars_ansible_port(self):
        host_vars = self.hostA.get_vars()
        self.assertEqual(host_vars['ansible_port'], self.ansible_port)

def test_TestHost_setUp():
    ret = TestHost().setUp()

def test_TestHost_test_equality():
    ret = TestHost().test_equality()

def test_TestHost_test_hashability():
    ret = TestHost().test_hashability()

def test_TestHost_test_get_vars():
    ret = TestHost().test_get_vars()

def test_TestHost_test_repr():
    ret = TestHost().test_repr()

def test_TestHost_test_add_group():
    ret = TestHost().test_add_group()

def test_TestHost_test_get_groups():
    ret = TestHost().test_get_groups()

def test_TestHost_test_equals_none():
    ret = TestHost().test_equals_none()

def test_TestHost_test_serialize():
    ret = TestHost().test_serialize()

def test_TestHost_test_serialize_then_deserialize():
    ret = TestHost().test_serialize_then_deserialize()

def test_TestHost_test_set_state():
    ret = TestHost().test_set_state()

def test_TestHostWithPort_setUp():
    ret = TestHostWithPort().setUp()

def test_TestHostWithPort_test_get_vars_ansible_port():
    ret = TestHostWithPort().test_get_vars_ansible_port()