from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from units.compat.mock import patch
from ansible.playbook.task import Task
from ansible.parsing.yaml import objects
from ansible import errors
basic_command_task = dict(name='Test Task', command='echo hi')
kv_command_task = dict(action='command echo hi')
kv_bad_args_str = '- apk: sdfs sf sdf 37'
kv_bad_args_ds = {'apk': 'sdfs sf sdf 37'}

class TestTask(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_construct_empty_task(self):
        Task()

    def test_construct_task_with_role(self):
        pass

    def test_construct_task_with_block(self):
        pass

    def test_construct_task_with_role_and_block(self):
        pass

    def test_load_task_simple(self):
        t = Task.load(basic_command_task)
        assert t is not None
        self.assertEqual(t.name, basic_command_task['name'])
        self.assertEqual(t.action, 'command')
        self.assertEqual(t.args, dict(_raw_params='echo hi'))

    def test_load_task_kv_form(self):
        t = Task.load(kv_command_task)
        self.assertEqual(t.action, 'command')
        self.assertEqual(t.args, dict(_raw_params='echo hi'))

    @patch.object(errors.AnsibleError, '_get_error_lines_from_file')
    def test_load_task_kv_form_error_36848(self, mock_get_err_lines):
        ds = objects.AnsibleMapping(kv_bad_args_ds)
        ds.ansible_pos = ('test_task_faux_playbook.yml', 1, 1)
        mock_get_err_lines.return_value = (kv_bad_args_str, '')
        with self.assertRaises(errors.AnsibleParserError) as cm:
            Task.load(ds)
        self.assertIsInstance(cm.exception, errors.AnsibleParserError)
        self.assertEqual(cm.exception._obj, ds)
        self.assertEqual(cm.exception._obj, kv_bad_args_ds)
        self.assertIn("The error appears to be in 'test_task_faux_playbook.yml", cm.exception.message)
        self.assertIn(kv_bad_args_str, cm.exception.message)
        self.assertIn('apk', cm.exception.message)
        self.assertEqual(cm.exception.message.count('The offending line'), 1)
        self.assertEqual(cm.exception.message.count('The error appears to be in'), 1)

    def test_task_auto_name(self):
        assert 'name' not in kv_command_task
        Task.load(kv_command_task)

    def test_task_auto_name_with_role(self):
        pass

    def test_load_task_complex_form(self):
        pass

    def test_can_load_module_complex_form(self):
        pass

    def test_local_action_implies_delegate(self):
        pass

    def test_local_action_conflicts_with_delegate(self):
        pass

    def test_delegate_to_parses(self):
        pass

def test_TestTask_setUp():
    ret = TestTask().setUp()

def test_TestTask_tearDown():
    ret = TestTask().tearDown()

def test_TestTask_test_construct_empty_task():
    ret = TestTask().test_construct_empty_task()

def test_TestTask_test_construct_task_with_role():
    ret = TestTask().test_construct_task_with_role()

def test_TestTask_test_construct_task_with_block():
    ret = TestTask().test_construct_task_with_block()

def test_TestTask_test_construct_task_with_role_and_block():
    ret = TestTask().test_construct_task_with_role_and_block()

def test_TestTask_test_load_task_simple():
    ret = TestTask().test_load_task_simple()

def test_TestTask_test_load_task_kv_form():
    ret = TestTask().test_load_task_kv_form()

def test_TestTask_test_load_task_kv_form_error_36848():
    ret = TestTask().test_load_task_kv_form_error_36848()

def test_TestTask_test_task_auto_name():
    ret = TestTask().test_task_auto_name()

def test_TestTask_test_task_auto_name_with_role():
    ret = TestTask().test_task_auto_name_with_role()

def test_TestTask_test_load_task_complex_form():
    ret = TestTask().test_load_task_complex_form()

def test_TestTask_test_can_load_module_complex_form():
    ret = TestTask().test_can_load_module_complex_form()

def test_TestTask_test_local_action_implies_delegate():
    ret = TestTask().test_local_action_implies_delegate()

def test_TestTask_test_local_action_conflicts_with_delegate():
    ret = TestTask().test_local_action_conflicts_with_delegate()

def test_TestTask_test_delegate_to_parses():
    ret = TestTask().test_delegate_to_parses()