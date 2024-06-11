from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from ansible.playbook.block import Block
from ansible.playbook.task import Task

class TestBlock(unittest.TestCase):

    def test_construct_empty_block(self):
        b = Block()

    def test_construct_block_with_role(self):
        pass

    def test_load_block_simple(self):
        ds = dict(block=[], rescue=[], always=[])
        b = Block.load(ds)
        self.assertEqual(b.block, [])
        self.assertEqual(b.rescue, [])
        self.assertEqual(b.always, [])

    def test_load_block_with_tasks(self):
        ds = dict(block=[dict(action='block')], rescue=[dict(action='rescue')], always=[dict(action='always')])
        b = Block.load(ds)
        self.assertEqual(len(b.block), 1)
        self.assertIsInstance(b.block[0], Task)
        self.assertEqual(len(b.rescue), 1)
        self.assertIsInstance(b.rescue[0], Task)
        self.assertEqual(len(b.always), 1)
        self.assertIsInstance(b.always[0], Task)

    def test_load_implicit_block(self):
        ds = [dict(action='foo')]
        b = Block.load(ds)
        self.assertEqual(len(b.block), 1)
        self.assertIsInstance(b.block[0], Task)

    def test_deserialize(self):
        ds = dict(block=[dict(action='block')], rescue=[dict(action='rescue')], always=[dict(action='always')])
        b = Block.load(ds)
        data = dict(parent=ds, parent_type='Block')
        b.deserialize(data)
        self.assertIsInstance(b._parent, Block)

def test_TestBlock_test_construct_empty_block():
    ret = TestBlock().test_construct_empty_block()

def test_TestBlock_test_construct_block_with_role():
    ret = TestBlock().test_construct_block_with_role()

def test_TestBlock_test_load_block_simple():
    ret = TestBlock().test_load_block_simple()

def test_TestBlock_test_load_block_with_tasks():
    ret = TestBlock().test_load_block_with_tasks()

def test_TestBlock_test_load_implicit_block():
    ret = TestBlock().test_load_implicit_block()

def test_TestBlock_test_deserialize():
    ret = TestBlock().test_deserialize()