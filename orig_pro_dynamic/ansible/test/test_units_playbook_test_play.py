from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from units.compat.mock import patch, MagicMock
from ansible.errors import AnsibleParserError
from ansible.playbook.play import Play
from units.mock.loader import DictDataLoader
from units.mock.path import mock_unfrackpath_noop

class TestPlay(unittest.TestCase):

    def test_empty_play(self):
        p = Play.load(dict())
        self.assertEqual(str(p), '')

    def test_basic_play(self):
        p = Play.load(dict(name='test play', hosts=['foo'], gather_facts=False, connection='local', remote_user='root', become=True, become_user='testing'))

    def test_play_with_user_conflict(self):
        p = Play.load(dict(name='test play', hosts=['foo'], user='testing', gather_facts=False))
        self.assertEqual(p.remote_user, 'testing')

    def test_play_with_user_conflict(self):
        play_data = dict(name='test play', hosts=['foo'], user='testing', remote_user='testing')
        self.assertRaises(AnsibleParserError, Play.load, play_data)

    def test_play_with_tasks(self):
        p = Play.load(dict(name='test play', hosts=['foo'], gather_facts=False, tasks=[dict(action='shell echo "hello world"')]))

    def test_play_with_handlers(self):
        p = Play.load(dict(name='test play', hosts=['foo'], gather_facts=False, handlers=[dict(action='shell echo "hello world"')]))

    def test_play_with_pre_tasks(self):
        p = Play.load(dict(name='test play', hosts=['foo'], gather_facts=False, pre_tasks=[dict(action='shell echo "hello world"')]))

    def test_play_with_post_tasks(self):
        p = Play.load(dict(name='test play', hosts=['foo'], gather_facts=False, post_tasks=[dict(action='shell echo "hello world"')]))

    @patch('ansible.playbook.role.definition.unfrackpath', mock_unfrackpath_noop)
    def test_play_with_roles(self):
        fake_loader = DictDataLoader({'/etc/ansible/roles/foo/tasks.yml': '\n            - name: role task\n              shell: echo "hello world"\n            '})
        mock_var_manager = MagicMock()
        mock_var_manager.get_vars.return_value = dict()
        p = Play.load(dict(name='test play', hosts=['foo'], gather_facts=False, roles=['foo']), loader=fake_loader, variable_manager=mock_var_manager)
        blocks = p.compile()

    def test_play_compile(self):
        p = Play.load(dict(name='test play', hosts=['foo'], gather_facts=False, tasks=[dict(action='shell echo "hello world"')]))
        blocks = p.compile()
        self.assertEqual(len(blocks), 4)

def test_TestPlay_test_empty_play():
    ret = TestPlay().test_empty_play()

def test_TestPlay_test_basic_play():
    ret = TestPlay().test_basic_play()

def test_TestPlay_test_play_with_user_conflict():
    ret = TestPlay().test_play_with_user_conflict()

def test_TestPlay_test_play_with_user_conflict():
    ret = TestPlay().test_play_with_user_conflict()

def test_TestPlay_test_play_with_tasks():
    ret = TestPlay().test_play_with_tasks()

def test_TestPlay_test_play_with_handlers():
    ret = TestPlay().test_play_with_handlers()

def test_TestPlay_test_play_with_pre_tasks():
    ret = TestPlay().test_play_with_pre_tasks()

def test_TestPlay_test_play_with_post_tasks():
    ret = TestPlay().test_play_with_post_tasks()

def test_TestPlay_test_play_with_roles():
    ret = TestPlay().test_play_with_roles()

def test_TestPlay_test_play_compile():
    ret = TestPlay().test_play_compile()