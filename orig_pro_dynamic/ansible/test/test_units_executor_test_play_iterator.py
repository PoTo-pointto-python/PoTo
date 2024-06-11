from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from units.compat.mock import patch, MagicMock
from ansible.executor.play_iterator import HostState, PlayIterator
from ansible.playbook import Playbook
from ansible.playbook.play_context import PlayContext
from units.mock.loader import DictDataLoader
from units.mock.path import mock_unfrackpath_noop

class TestPlayIterator(unittest.TestCase):

    def test_host_state(self):
        hs = HostState(blocks=list(range(0, 10)))
        hs.tasks_child_state = HostState(blocks=[0])
        hs.rescue_child_state = HostState(blocks=[1])
        hs.always_child_state = HostState(blocks=[2])
        hs.__repr__()
        hs.run_state = 100
        hs.__repr__()
        hs.fail_state = 15
        hs.__repr__()
        for i in range(0, 10):
            hs.cur_block = i
            self.assertEqual(hs.get_current_block(), i)
        new_hs = hs.copy()

    @patch('ansible.playbook.role.definition.unfrackpath', mock_unfrackpath_noop)
    def test_play_iterator(self):
        fake_loader = DictDataLoader({'test_play.yml': '\n            - hosts: all\n              gather_facts: false\n              roles:\n              - test_role\n              pre_tasks:\n              - debug: msg="this is a pre_task"\n              tasks:\n              - debug: msg="this is a regular task"\n              - block:\n                - debug: msg="this is a block task"\n                - block:\n                  - debug: msg="this is a sub-block in a block"\n                rescue:\n                - debug: msg="this is a rescue task"\n                - block:\n                  - debug: msg="this is a sub-block in a rescue"\n                always:\n                - debug: msg="this is an always task"\n                - block:\n                  - debug: msg="this is a sub-block in an always"\n              post_tasks:\n              - debug: msg="this is a post_task"\n            ', '/etc/ansible/roles/test_role/tasks/main.yml': '\n            - name: role task\n              debug: msg="this is a role task"\n            - block:\n              - name: role block task\n                debug: msg="inside block in role"\n              always:\n              - name: role always task\n                debug: msg="always task in block in role"\n            - include: foo.yml\n            - name: role task after include\n              debug: msg="after include in role"\n            - block:\n              - name: starting role nested block 1\n                debug:\n              - block:\n                - name: role nested block 1 task 1\n                  debug:\n                - name: role nested block 1 task 2\n                  debug:\n                - name: role nested block 1 task 3\n                  debug:\n              - name: end of role nested block 1\n                debug:\n              - name: starting role nested block 2\n                debug:\n              - block:\n                - name: role nested block 2 task 1\n                  debug:\n                - name: role nested block 2 task 2\n                  debug:\n                - name: role nested block 2 task 3\n                  debug:\n              - name: end of role nested block 2\n                debug:\n            ', '/etc/ansible/roles/test_role/tasks/foo.yml': '\n            - name: role included task\n              debug: msg="this is task in an include from a role"\n            '})
        mock_var_manager = MagicMock()
        mock_var_manager._fact_cache = dict()
        mock_var_manager.get_vars.return_value = dict()
        p = Playbook.load('test_play.yml', loader=fake_loader, variable_manager=mock_var_manager)
        hosts = []
        for i in range(0, 10):
            host = MagicMock()
            host.name = host.get_name.return_value = 'host%02d' % i
            hosts.append(host)
        mock_var_manager._fact_cache['host00'] = dict()
        inventory = MagicMock()
        inventory.get_hosts.return_value = hosts
        inventory.filter_hosts.return_value = hosts
        play_context = PlayContext(play=p._entries[0])
        itr = PlayIterator(inventory=inventory, play=p._entries[0], play_context=play_context, variable_manager=mock_var_manager, all_vars=dict())
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'debug')
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'meta')
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'debug')
        self.assertEqual(task.name, 'role task')
        self.assertIsNotNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'role block task')
        self.assertIsNotNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'role always task')
        self.assertIsNotNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'role task after include')
        self.assertIsNotNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'starting role nested block 1')
        self.assertIsNotNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'role nested block 1 task 1')
        self.assertIsNotNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'role nested block 1 task 2')
        self.assertIsNotNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'role nested block 1 task 3')
        self.assertIsNotNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'end of role nested block 1')
        self.assertIsNotNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'starting role nested block 2')
        self.assertIsNotNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'role nested block 2 task 1')
        self.assertIsNotNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'role nested block 2 task 2')
        self.assertIsNotNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'role nested block 2 task 3')
        self.assertIsNotNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'end of role nested block 2')
        self.assertIsNotNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'debug')
        self.assertIsNone(task._role)
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'debug')
        self.assertEqual(task.args, dict(msg='this is a block task'))
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'debug')
        self.assertEqual(task.args, dict(msg='this is a sub-block in a block'))
        itr.mark_host_failed(hosts[0])
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'debug')
        self.assertEqual(task.args, dict(msg='this is a rescue task'))
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'debug')
        self.assertEqual(task.args, dict(msg='this is a sub-block in a rescue'))
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'debug')
        self.assertEqual(task.args, dict(msg='this is an always task'))
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'debug')
        self.assertEqual(task.args, dict(msg='this is a sub-block in an always'))
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'meta')
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'debug')
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'meta')
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNone(task)
        failed_hosts = itr.get_failed_hosts()
        self.assertNotIn(hosts[0], failed_hosts)

    def test_play_iterator_nested_blocks(self):
        fake_loader = DictDataLoader({'test_play.yml': '\n            - hosts: all\n              gather_facts: false\n              tasks:\n              - block:\n                - block:\n                  - block:\n                    - block:\n                      - block:\n                        - debug: msg="this is the first task"\n                        - ping:\n                      rescue:\n                      - block:\n                        - block:\n                          - block:\n                            - block:\n                              - debug: msg="this is the rescue task"\n                  always:\n                  - block:\n                    - block:\n                      - block:\n                        - block:\n                          - debug: msg="this is the always task"\n            '})
        mock_var_manager = MagicMock()
        mock_var_manager._fact_cache = dict()
        mock_var_manager.get_vars.return_value = dict()
        p = Playbook.load('test_play.yml', loader=fake_loader, variable_manager=mock_var_manager)
        hosts = []
        for i in range(0, 10):
            host = MagicMock()
            host.name = host.get_name.return_value = 'host%02d' % i
            hosts.append(host)
        inventory = MagicMock()
        inventory.get_hosts.return_value = hosts
        inventory.filter_hosts.return_value = hosts
        play_context = PlayContext(play=p._entries[0])
        itr = PlayIterator(inventory=inventory, play=p._entries[0], play_context=play_context, variable_manager=mock_var_manager, all_vars=dict())
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'meta')
        self.assertEqual(task.args, dict(_raw_params='flush_handlers'))
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'debug')
        self.assertEqual(task.args, dict(msg='this is the first task'))
        itr.mark_host_failed(hosts[0])
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'debug')
        self.assertEqual(task.args, dict(msg='this is the rescue task'))
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'debug')
        self.assertEqual(task.args, dict(msg='this is the always task'))
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'meta')
        self.assertEqual(task.args, dict(_raw_params='flush_handlers'))
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNotNone(task)
        self.assertEqual(task.action, 'meta')
        self.assertEqual(task.args, dict(_raw_params='flush_handlers'))
        (host_state, task) = itr.get_next_task_for_host(hosts[0])
        self.assertIsNone(task)

    def test_play_iterator_add_tasks(self):
        fake_loader = DictDataLoader({'test_play.yml': '\n            - hosts: all\n              gather_facts: no\n              tasks:\n              - debug: msg="dummy task"\n            '})
        mock_var_manager = MagicMock()
        mock_var_manager._fact_cache = dict()
        mock_var_manager.get_vars.return_value = dict()
        p = Playbook.load('test_play.yml', loader=fake_loader, variable_manager=mock_var_manager)
        hosts = []
        for i in range(0, 10):
            host = MagicMock()
            host.name = host.get_name.return_value = 'host%02d' % i
            hosts.append(host)
        inventory = MagicMock()
        inventory.get_hosts.return_value = hosts
        inventory.filter_hosts.return_value = hosts
        play_context = PlayContext(play=p._entries[0])
        itr = PlayIterator(inventory=inventory, play=p._entries[0], play_context=play_context, variable_manager=mock_var_manager, all_vars=dict())
        s = HostState(blocks=[0, 1, 2])
        itr._insert_tasks_into_state = MagicMock(return_value=s)
        itr.add_tasks(hosts[0], [MagicMock(), MagicMock(), MagicMock()])
        self.assertEqual(itr._host_states[hosts[0].name], s)
        itr = PlayIterator(inventory=inventory, play=p._entries[0], play_context=play_context, variable_manager=mock_var_manager, all_vars=dict())
        (_, task) = itr.get_next_task_for_host(hosts[0])
        while task and task.action != 'debug':
            (_, task) = itr.get_next_task_for_host(hosts[0])
        if task is None:
            raise Exception('iterated past end of play while looking for place to insert tasks')
        s = itr.get_host_state(hosts[0])
        s_copy = s.copy()
        res_state = itr._insert_tasks_into_state(s_copy, task_list=[])
        self.assertEqual(res_state, s_copy)
        s_copy.fail_state = itr.FAILED_TASKS
        res_state = itr._insert_tasks_into_state(s_copy, task_list=[MagicMock()])
        self.assertEqual(res_state, s_copy)
        mock_task = MagicMock()
        s_copy.run_state = itr.ITERATING_RESCUE
        res_state = itr._insert_tasks_into_state(s_copy, task_list=[mock_task])
        self.assertEqual(res_state, s_copy)
        self.assertIn(mock_task, res_state._blocks[res_state.cur_block].rescue)
        itr._host_states[hosts[0].name] = res_state
        (next_state, next_task) = itr.get_next_task_for_host(hosts[0], peek=True)
        self.assertEqual(next_task, mock_task)
        itr._host_states[hosts[0].name] = s
        s_copy = s.copy()
        res_state = itr._insert_tasks_into_state(s_copy, task_list=[MagicMock()])

def test_TestPlayIterator_test_host_state():
    ret = TestPlayIterator().test_host_state()

def test_TestPlayIterator_test_play_iterator():
    ret = TestPlayIterator().test_play_iterator()

def test_TestPlayIterator_test_play_iterator_nested_blocks():
    ret = TestPlayIterator().test_play_iterator_nested_blocks()

def test_TestPlayIterator_test_play_iterator_add_tasks():
    ret = TestPlayIterator().test_play_iterator_add_tasks()