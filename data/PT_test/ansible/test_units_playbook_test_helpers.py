from __future__ import absolute_import, division, print_function
__metaclass__ = type
import os
from units.compat import unittest
from units.compat.mock import MagicMock
from units.mock.loader import DictDataLoader
from ansible import errors
from ansible.playbook.block import Block
from ansible.playbook.handler import Handler
from ansible.playbook.task import Task
from ansible.playbook.task_include import TaskInclude
from ansible.playbook.role.include import RoleInclude
from ansible.playbook import helpers

class MixinForMocks(object):

    def _setup(self):
        self.fake_loader = DictDataLoader({'include_test.yml': '', 'other_include_test.yml': ''})
        self.mock_tqm = MagicMock(name='MockTaskQueueManager')
        self.mock_play = MagicMock(name='MockPlay')
        self.mock_play._attributes = []
        self.mock_play.collections = None
        self.mock_iterator = MagicMock(name='MockIterator')
        self.mock_iterator._play = self.mock_play
        self.mock_inventory = MagicMock(name='MockInventory')
        self.mock_inventory._hosts_cache = dict()

        def _get_host(host_name):
            return None
        self.mock_inventory.get_host.side_effect = _get_host
        self.mock_variable_manager = MagicMock(name='MockVariableManager')
        self.mock_variable_manager.get_vars.return_value = dict()
        self.mock_block = MagicMock(name='MockBlock')
        self.fake_role_loader = DictDataLoader({os.path.join(os.path.realpath('/etc'), 'ansible/roles/bogus_role/tasks/main.yml'): "\n                                                - shell: echo 'hello world'\n                                                "})
        self._test_data_path = os.path.dirname(__file__)
        self.fake_include_loader = DictDataLoader({'/dev/null/includes/test_include.yml': "\n                                                   - include: other_test_include.yml\n                                                   - shell: echo 'hello world'\n                                                   ", '/dev/null/includes/static_test_include.yml': "\n                                                   - include: other_test_include.yml\n                                                   - shell: echo 'hello static world'\n                                                   ", '/dev/null/includes/other_test_include.yml': '\n                                                   - debug:\n                                                       msg: other_test_include_debug\n                                                   '})

class TestLoadListOfTasks(unittest.TestCase, MixinForMocks):

    def setUp(self):
        self._setup()

    def _assert_is_task_list(self, results):
        for result in results:
            self.assertIsInstance(result, Task)

    def _assert_is_task_list_or_blocks(self, results):
        self.assertIsInstance(results, list)
        for result in results:
            self.assertIsInstance(result, (Task, Block))

    def test_ds_not_list(self):
        ds = {}
        self.assertRaises(AssertionError, helpers.load_list_of_tasks, ds, self.mock_play, block=None, role=None, task_include=None, use_handlers=False, variable_manager=None, loader=None)

    def test_ds_not_dict(self):
        ds = [[]]
        self.assertRaises(AssertionError, helpers.load_list_of_tasks, ds, self.mock_play, block=None, role=None, task_include=None, use_handlers=False, variable_manager=None, loader=None)

    def test_empty_task(self):
        ds = [{}]
        self.assertRaisesRegexp(errors.AnsibleParserError, 'no module/action detected in task', helpers.load_list_of_tasks, ds, play=self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_loader)

    def test_empty_task_use_handlers(self):
        ds = [{}]
        self.assertRaisesRegexp(errors.AnsibleParserError, 'no module/action detected in task.', helpers.load_list_of_tasks, ds, use_handlers=True, play=self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_loader)

    def test_one_bogus_block(self):
        ds = [{'block': None}]
        self.assertRaisesRegexp(errors.AnsibleParserError, 'A malformed block was encountered', helpers.load_list_of_tasks, ds, play=self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_loader)

    def test_unknown_action(self):
        action_name = 'foo_test_unknown_action'
        ds = [{'action': action_name}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_loader)
        self._assert_is_task_list_or_blocks(res)
        self.assertEqual(res[0].action, action_name)

    def test_block_unknown_action(self):
        action_name = 'foo_test_block_unknown_action'
        ds = [{'block': [{'action': action_name}]}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_loader)
        self._assert_is_task_list_or_blocks(res)
        self.assertIsInstance(res[0], Block)
        self._assert_default_block(res[0])

    def _assert_default_block(self, block):
        self.assertIsInstance(block.block, list)
        self.assertEqual(len(block.block), 1)
        self.assertIsInstance(block.rescue, list)
        self.assertEqual(len(block.rescue), 0)
        self.assertIsInstance(block.always, list)
        self.assertEqual(len(block.always), 0)

    def test_block_unknown_action_use_handlers(self):
        ds = [{'block': [{'action': 'foo_test_block_unknown_action'}]}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, use_handlers=True, variable_manager=self.mock_variable_manager, loader=self.fake_loader)
        self._assert_is_task_list_or_blocks(res)
        self.assertIsInstance(res[0], Block)
        self._assert_default_block(res[0])

    def test_one_bogus_block_use_handlers(self):
        ds = [{'block': True}]
        self.assertRaisesRegexp(errors.AnsibleParserError, 'A malformed block was encountered', helpers.load_list_of_tasks, ds, play=self.mock_play, use_handlers=True, variable_manager=self.mock_variable_manager, loader=self.fake_loader)

    def test_one_bogus_include(self):
        ds = [{'include': 'somefile.yml'}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_loader)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 0)

    def test_one_bogus_include_use_handlers(self):
        ds = [{'include': 'somefile.yml'}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, use_handlers=True, variable_manager=self.mock_variable_manager, loader=self.fake_loader)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 0)

    def test_one_bogus_include_static(self):
        ds = [{'include': 'somefile.yml', 'static': 'true'}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_loader)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 0)

    def test_one_include(self):
        ds = [{'include': '/dev/null/includes/other_test_include.yml'}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_include_loader)
        self.assertEqual(len(res), 1)
        self._assert_is_task_list_or_blocks(res)

    def test_one_parent_include(self):
        ds = [{'include': '/dev/null/includes/test_include.yml'}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_include_loader)
        self._assert_is_task_list_or_blocks(res)
        self.assertIsInstance(res[0], Block)
        self.assertIsInstance(res[0]._parent, TaskInclude)

    def test_one_include_tags(self):
        ds = [{'include': '/dev/null/includes/other_test_include.yml', 'tags': ['test_one_include_tags_tag1', 'and_another_tagB']}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_include_loader)
        self._assert_is_task_list_or_blocks(res)
        self.assertIsInstance(res[0], Block)
        self.assertIn('test_one_include_tags_tag1', res[0].tags)
        self.assertIn('and_another_tagB', res[0].tags)

    def test_one_parent_include_tags(self):
        ds = [{'include': '/dev/null/includes/test_include.yml', 'tags': ['test_one_parent_include_tags_tag1', 'and_another_tag2']}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_include_loader)
        self._assert_is_task_list_or_blocks(res)
        self.assertIsInstance(res[0], Block)
        self.assertIn('test_one_parent_include_tags_tag1', res[0].tags)
        self.assertIn('and_another_tag2', res[0].tags)

    def test_one_include_tags_deprecated_mixed(self):
        ds = [{'include': '/dev/null/includes/other_test_include.yml', 'vars': {'tags': "['tag_on_include1', 'tag_on_include2']"}, 'tags': 'mixed_tag1, mixed_tag2'}]
        self.assertRaisesRegexp(errors.AnsibleParserError, 'Mixing styles', helpers.load_list_of_tasks, ds, play=self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_include_loader)

    def test_one_include_tags_deprecated_include(self):
        ds = [{'include': '/dev/null/includes/other_test_include.yml', 'vars': {'tags': ['include_tag1_deprecated', 'and_another_tagB_deprecated']}}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_include_loader)
        self._assert_is_task_list_or_blocks(res)
        self.assertIsInstance(res[0], Block)
        self.assertIn('include_tag1_deprecated', res[0].tags)
        self.assertIn('and_another_tagB_deprecated', res[0].tags)

    def test_one_include_use_handlers(self):
        ds = [{'include': '/dev/null/includes/other_test_include.yml'}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, use_handlers=True, variable_manager=self.mock_variable_manager, loader=self.fake_include_loader)
        self._assert_is_task_list_or_blocks(res)
        self.assertIsInstance(res[0], Handler)

    def test_one_parent_include_use_handlers(self):
        ds = [{'include': '/dev/null/includes/test_include.yml'}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, use_handlers=True, variable_manager=self.mock_variable_manager, loader=self.fake_include_loader)
        self._assert_is_task_list_or_blocks(res)
        self.assertIsInstance(res[0], Handler)
        self.assertEqual(res[0].listen, [])

    def test_one_include_not_static(self):
        ds = [{'include': '/dev/null/includes/static_test_include.yml', 'static': False}]
        ti_ds = {'include': '/dev/null/includes/ssdftatic_test_include.yml'}
        a_task_include = TaskInclude()
        ti = a_task_include.load(ti_ds)
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, block=ti, variable_manager=self.mock_variable_manager, loader=self.fake_include_loader)
        self._assert_is_task_list_or_blocks(res)
        self.assertIsInstance(res[0], Task)
        self.assertEqual(res[0].args['_raw_params'], '/dev/null/includes/static_test_include.yml')

    def test_one_bogus_include_role(self):
        ds = [{'include_role': {'name': 'bogus_role'}, 'collections': []}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, block=self.mock_block, variable_manager=self.mock_variable_manager, loader=self.fake_role_loader)
        self.assertEqual(len(res), 1)
        self._assert_is_task_list_or_blocks(res)

    def test_one_bogus_include_role_use_handlers(self):
        ds = [{'include_role': {'name': 'bogus_role'}, 'collections': []}]
        res = helpers.load_list_of_tasks(ds, play=self.mock_play, use_handlers=True, block=self.mock_block, variable_manager=self.mock_variable_manager, loader=self.fake_role_loader)
        self.assertEqual(len(res), 1)
        self._assert_is_task_list_or_blocks(res)

class TestLoadListOfRoles(unittest.TestCase, MixinForMocks):

    def setUp(self):
        self._setup()

    def test_ds_not_list(self):
        ds = {}
        self.assertRaises(AssertionError, helpers.load_list_of_roles, ds, self.mock_play)

    def test_empty_role(self):
        ds = [{}]
        self.assertRaisesRegexp(errors.AnsibleError, 'role definitions must contain a role name', helpers.load_list_of_roles, ds, self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_role_loader)

    def test_empty_role_just_name(self):
        ds = [{'name': 'bogus_role'}]
        res = helpers.load_list_of_roles(ds, self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_role_loader)
        self.assertIsInstance(res, list)
        for r in res:
            self.assertIsInstance(r, RoleInclude)

    def test_block_unknown_action(self):
        ds = [{'block': [{'action': 'foo_test_block_unknown_action'}]}]
        ds = [{'name': 'bogus_role'}]
        res = helpers.load_list_of_roles(ds, self.mock_play, variable_manager=self.mock_variable_manager, loader=self.fake_role_loader)
        self.assertIsInstance(res, list)
        for r in res:
            self.assertIsInstance(r, RoleInclude)

class TestLoadListOfBlocks(unittest.TestCase, MixinForMocks):

    def setUp(self):
        self._setup()

    def test_ds_not_list(self):
        ds = {}
        mock_play = MagicMock(name='MockPlay')
        self.assertRaises(AssertionError, helpers.load_list_of_blocks, ds, mock_play, parent_block=None, role=None, task_include=None, use_handlers=False, variable_manager=None, loader=None)

    def test_empty_block(self):
        ds = [{}]
        mock_play = MagicMock(name='MockPlay')
        self.assertRaisesRegexp(errors.AnsibleParserError, 'no module/action detected in task', helpers.load_list_of_blocks, ds, mock_play, parent_block=None, role=None, task_include=None, use_handlers=False, variable_manager=None, loader=None)

    def test_block_unknown_action(self):
        ds = [{'action': 'foo', 'collections': []}]
        mock_play = MagicMock(name='MockPlay')
        res = helpers.load_list_of_blocks(ds, mock_play, parent_block=None, role=None, task_include=None, use_handlers=False, variable_manager=None, loader=None)
        self.assertIsInstance(res, list)
        for block in res:
            self.assertIsInstance(block, Block)

def test_MixinForMocks__get_host():
    ret = MixinForMocks()._get_host()

def test_MixinForMocks__setup():
    ret = MixinForMocks()._setup()

def test_TestLoadListOfTasks_setUp():
    ret = TestLoadListOfTasks().setUp()

def test_TestLoadListOfTasks__assert_is_task_list():
    ret = TestLoadListOfTasks()._assert_is_task_list()

def test_TestLoadListOfTasks__assert_is_task_list_or_blocks():
    ret = TestLoadListOfTasks()._assert_is_task_list_or_blocks()

def test_TestLoadListOfTasks_test_ds_not_list():
    ret = TestLoadListOfTasks().test_ds_not_list()

def test_TestLoadListOfTasks_test_ds_not_dict():
    ret = TestLoadListOfTasks().test_ds_not_dict()

def test_TestLoadListOfTasks_test_empty_task():
    ret = TestLoadListOfTasks().test_empty_task()

def test_TestLoadListOfTasks_test_empty_task_use_handlers():
    ret = TestLoadListOfTasks().test_empty_task_use_handlers()

def test_TestLoadListOfTasks_test_one_bogus_block():
    ret = TestLoadListOfTasks().test_one_bogus_block()

def test_TestLoadListOfTasks_test_unknown_action():
    ret = TestLoadListOfTasks().test_unknown_action()

def test_TestLoadListOfTasks_test_block_unknown_action():
    ret = TestLoadListOfTasks().test_block_unknown_action()

def test_TestLoadListOfTasks__assert_default_block():
    ret = TestLoadListOfTasks()._assert_default_block()

def test_TestLoadListOfTasks_test_block_unknown_action_use_handlers():
    ret = TestLoadListOfTasks().test_block_unknown_action_use_handlers()

def test_TestLoadListOfTasks_test_one_bogus_block_use_handlers():
    ret = TestLoadListOfTasks().test_one_bogus_block_use_handlers()

def test_TestLoadListOfTasks_test_one_bogus_include():
    ret = TestLoadListOfTasks().test_one_bogus_include()

def test_TestLoadListOfTasks_test_one_bogus_include_use_handlers():
    ret = TestLoadListOfTasks().test_one_bogus_include_use_handlers()

def test_TestLoadListOfTasks_test_one_bogus_include_static():
    ret = TestLoadListOfTasks().test_one_bogus_include_static()

def test_TestLoadListOfTasks_test_one_include():
    ret = TestLoadListOfTasks().test_one_include()

def test_TestLoadListOfTasks_test_one_parent_include():
    ret = TestLoadListOfTasks().test_one_parent_include()

def test_TestLoadListOfTasks_test_one_include_tags():
    ret = TestLoadListOfTasks().test_one_include_tags()

def test_TestLoadListOfTasks_test_one_parent_include_tags():
    ret = TestLoadListOfTasks().test_one_parent_include_tags()

def test_TestLoadListOfTasks_test_one_include_tags_deprecated_mixed():
    ret = TestLoadListOfTasks().test_one_include_tags_deprecated_mixed()

def test_TestLoadListOfTasks_test_one_include_tags_deprecated_include():
    ret = TestLoadListOfTasks().test_one_include_tags_deprecated_include()

def test_TestLoadListOfTasks_test_one_include_use_handlers():
    ret = TestLoadListOfTasks().test_one_include_use_handlers()

def test_TestLoadListOfTasks_test_one_parent_include_use_handlers():
    ret = TestLoadListOfTasks().test_one_parent_include_use_handlers()

def test_TestLoadListOfTasks_test_one_include_not_static():
    ret = TestLoadListOfTasks().test_one_include_not_static()

def test_TestLoadListOfTasks_test_one_bogus_include_role():
    ret = TestLoadListOfTasks().test_one_bogus_include_role()

def test_TestLoadListOfTasks_test_one_bogus_include_role_use_handlers():
    ret = TestLoadListOfTasks().test_one_bogus_include_role_use_handlers()

def test_TestLoadListOfRoles_setUp():
    ret = TestLoadListOfRoles().setUp()

def test_TestLoadListOfRoles_test_ds_not_list():
    ret = TestLoadListOfRoles().test_ds_not_list()

def test_TestLoadListOfRoles_test_empty_role():
    ret = TestLoadListOfRoles().test_empty_role()

def test_TestLoadListOfRoles_test_empty_role_just_name():
    ret = TestLoadListOfRoles().test_empty_role_just_name()

def test_TestLoadListOfRoles_test_block_unknown_action():
    ret = TestLoadListOfRoles().test_block_unknown_action()

def test_TestLoadListOfBlocks_setUp():
    ret = TestLoadListOfBlocks().setUp()

def test_TestLoadListOfBlocks_test_ds_not_list():
    ret = TestLoadListOfBlocks().test_ds_not_list()

def test_TestLoadListOfBlocks_test_empty_block():
    ret = TestLoadListOfBlocks().test_empty_block()

def test_TestLoadListOfBlocks_test_block_unknown_action():
    ret = TestLoadListOfBlocks().test_block_unknown_action()