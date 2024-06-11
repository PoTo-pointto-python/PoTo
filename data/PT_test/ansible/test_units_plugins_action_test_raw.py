from __future__ import absolute_import, division, print_function
__metaclass__ = type
import os
from ansible.errors import AnsibleActionFail
from units.compat import unittest
from units.compat.mock import MagicMock, Mock
from ansible.plugins.action.raw import ActionModule
from ansible.playbook.task import Task
from ansible.plugins.loader import connection_loader

class TestCopyResultExclude(unittest.TestCase):

    def setUp(self):
        self.play_context = Mock()
        self.play_context.shell = 'sh'
        self.connection = connection_loader.get('local', self.play_context, os.devnull)

    def tearDown(self):
        pass

    def test_raw_executable_is_not_empty_string(self):
        task = MagicMock(Task)
        task.async_val = False
        task.args = {'_raw_params': 'Args1'}
        self.play_context.check_mode = False
        self.mock_am = ActionModule(task, self.connection, self.play_context, loader=None, templar=None, shared_loader_obj=None)
        self.mock_am._low_level_execute_command = Mock(return_value={})
        self.mock_am.display = Mock()
        self.mock_am._admin_users = ['root', 'toor']
        self.mock_am.run()
        self.mock_am._low_level_execute_command.assert_called_with('Args1', executable=False)

    def test_raw_check_mode_is_True(self):
        task = MagicMock(Task)
        task.async_val = False
        task.args = {'_raw_params': 'Args1'}
        self.play_context.check_mode = True
        try:
            self.mock_am = ActionModule(task, self.connection, self.play_context, loader=None, templar=None, shared_loader_obj=None)
        except AnsibleActionFail:
            pass

    def test_raw_test_environment_is_None(self):
        task = MagicMock(Task)
        task.async_val = False
        task.args = {'_raw_params': 'Args1'}
        task.environment = None
        self.play_context.check_mode = False
        self.mock_am = ActionModule(task, self.connection, self.play_context, loader=None, templar=None, shared_loader_obj=None)
        self.mock_am._low_level_execute_command = Mock(return_value={})
        self.mock_am.display = Mock()
        self.assertEqual(task.environment, None)

    def test_raw_task_vars_is_not_None(self):
        task = MagicMock(Task)
        task.async_val = False
        task.args = {'_raw_params': 'Args1'}
        task.environment = None
        self.play_context.check_mode = False
        self.mock_am = ActionModule(task, self.connection, self.play_context, loader=None, templar=None, shared_loader_obj=None)
        self.mock_am._low_level_execute_command = Mock(return_value={})
        self.mock_am.display = Mock()
        self.mock_am.run(task_vars={'a': 'b'})
        self.assertEqual(task.environment, None)

def test_TestCopyResultExclude_setUp():
    ret = TestCopyResultExclude().setUp()

def test_TestCopyResultExclude_tearDown():
    ret = TestCopyResultExclude().tearDown()

def test_TestCopyResultExclude_test_raw_executable_is_not_empty_string():
    ret = TestCopyResultExclude().test_raw_executable_is_not_empty_string()

def test_TestCopyResultExclude_test_raw_check_mode_is_True():
    ret = TestCopyResultExclude().test_raw_check_mode_is_True()

def test_TestCopyResultExclude_test_raw_test_environment_is_None():
    ret = TestCopyResultExclude().test_raw_test_environment_is_None()

def test_TestCopyResultExclude_test_raw_task_vars_is_not_None():
    ret = TestCopyResultExclude().test_raw_task_vars_is_not_None()