from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from ansible.inventory.group import Group
from ansible.inventory.host import Host
from ansible.errors import AnsibleError

class TestGroup(unittest.TestCase):

    def test_depth_update(self):
        A = Group('A')
        B = Group('B')
        Z = Group('Z')
        A.add_child_group(B)
        A.add_child_group(Z)
        self.assertEqual(A.depth, 0)
        self.assertEqual(Z.depth, 1)
        self.assertEqual(B.depth, 1)

    def test_depth_update_dual_branches(self):
        alpha = Group('alpha')
        A = Group('A')
        alpha.add_child_group(A)
        B = Group('B')
        A.add_child_group(B)
        Z = Group('Z')
        alpha.add_child_group(Z)
        beta = Group('beta')
        B.add_child_group(beta)
        Z.add_child_group(beta)
        self.assertEqual(alpha.depth, 0)
        self.assertEqual(beta.depth, 3)
        omega = Group('omega')
        omega.add_child_group(alpha)
        self.assertEqual(B.depth, 3)
        self.assertEqual(beta.depth, 4)

    def test_depth_recursion(self):
        A = Group('A')
        B = Group('B')
        A.add_child_group(B)
        A.parent_groups.append(B)
        B.child_groups.append(A)
        with self.assertRaises(AnsibleError):
            B._check_children_depth()

    def test_loop_detection(self):
        A = Group('A')
        B = Group('B')
        C = Group('C')
        A.add_child_group(B)
        B.add_child_group(C)
        with self.assertRaises(AnsibleError):
            C.add_child_group(A)

    def test_direct_host_ordering(self):
        """Hosts are returned in order they are added
        """
        group = Group('A')
        host_name_list = ['z', 'b', 'c', 'a', 'p', 'q']
        expected_hosts = []
        for host_name in host_name_list:
            h = Host(host_name)
            group.add_host(h)
            expected_hosts.append(h)
        assert group.get_hosts() == expected_hosts

    def test_sub_group_host_ordering(self):
        """With multiple nested groups, asserts that hosts are returned
        in deterministic order
        """
        top_group = Group('A')
        expected_hosts = []
        for name in ['z', 'b', 'c', 'a', 'p', 'q']:
            child = Group('group_{0}'.format(name))
            top_group.add_child_group(child)
            host = Host('host_{0}'.format(name))
            child.add_host(host)
            expected_hosts.append(host)
        assert top_group.get_hosts() == expected_hosts

    def test_populates_descendant_hosts(self):
        A = Group('A')
        B = Group('B')
        C = Group('C')
        h = Host('h')
        C.add_host(h)
        A.add_child_group(B)
        B.add_child_group(C)
        A.add_child_group(B)
        self.assertEqual(set(h.groups), set([C, B, A]))
        h2 = Host('h2')
        C.add_host(h2)
        self.assertEqual(set(h2.groups), set([C, B, A]))

    def test_ancestor_example(self):
        groups = {}
        for name in ['A', 'B', 'C', 'D', 'E', 'F']:
            groups[name] = Group(name)
        groups['A'].add_child_group(groups['D'])
        groups['B'].add_child_group(groups['D'])
        groups['B'].add_child_group(groups['E'])
        groups['C'].add_child_group(groups['D'])
        groups['D'].add_child_group(groups['E'])
        groups['D'].add_child_group(groups['F'])
        groups['E'].add_child_group(groups['F'])
        self.assertEqual(set(groups['F'].get_ancestors()), set([groups['A'], groups['B'], groups['C'], groups['D'], groups['E']]))

    def test_ancestors_recursive_loop_safe(self):
        """
        The get_ancestors method may be referenced before circular parenting
        checks, so the method is expected to be stable even with loops
        """
        A = Group('A')
        B = Group('B')
        A.parent_groups.append(B)
        B.parent_groups.append(A)
        self.assertEqual(A.get_ancestors(), set([A, B]))

def test_TestGroup_test_depth_update():
    ret = TestGroup().test_depth_update()

def test_TestGroup_test_depth_update_dual_branches():
    ret = TestGroup().test_depth_update_dual_branches()

def test_TestGroup_test_depth_recursion():
    ret = TestGroup().test_depth_recursion()

def test_TestGroup_test_loop_detection():
    ret = TestGroup().test_loop_detection()

def test_TestGroup_test_direct_host_ordering():
    ret = TestGroup().test_direct_host_ordering()

def test_TestGroup_test_sub_group_host_ordering():
    ret = TestGroup().test_sub_group_host_ordering()

def test_TestGroup_test_populates_descendant_hosts():
    ret = TestGroup().test_populates_descendant_hosts()

def test_TestGroup_test_ancestor_example():
    ret = TestGroup().test_ancestor_example()

def test_TestGroup_test_ancestors_recursive_loop_safe():
    ret = TestGroup().test_ancestors_recursive_loop_safe()