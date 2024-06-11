from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from units.compat.mock import patch, MagicMock
from ansible.executor.play_iterator import PlayIterator
from ansible.playbook import Playbook
from ansible.playbook.play_context import PlayContext
from ansible.plugins.strategy.linear import StrategyModule
from ansible.executor.task_queue_manager import TaskQueueManager
from units.mock.loader import DictDataLoader
from units.mock.path import mock_unfrackpath_noop

class TestStrategyLinear(unittest.TestCase):

    @patch('ansible.playbook.role.definition.unfrackpath', mock_unfrackpath_noop)
    def test_noop(self):
        fake_loader = DictDataLoader({'test_play.yml': "\n            - hosts: all\n              gather_facts: no\n              tasks:\n                - block:\n                   - block:\n                     - name: task1\n                       debug: msg='task1'\n                       failed_when: inventory_hostname == 'host01'\n\n                     - name: task2\n                       debug: msg='task2'\n\n                     rescue:\n                       - name: rescue1\n                         debug: msg='rescue1'\n\n                       - name: rescue2\n                         debug: msg='rescue2'\n            "})
        mock_var_manager = MagicMock()
        mock_var_manager._fact_cache = dict()
        mock_var_manager.get_vars.return_value = dict()
        p = Playbook.load('test_play.yml', loader=fake_loader, variable_manager=mock_var_manager)
        inventory = MagicMock()
        inventory.hosts = {}
        hosts = []
        for i in range(0, 2):
            host = MagicMock()
            host.name = host.get_name.return_value = 'host%02d' % i
            hosts.append(host)
            inventory.hosts[host.name] = host
        inventory.get_hosts.return_value = hosts
        inventory.filter_hosts.return_value = hosts
        mock_var_manager._fact_cache['host00'] = dict()
        play_context = PlayContext(play=p._entries[0])
        itr = PlayIterator(inventory=inventory, play=p._entries[0], play_context=play_context, variable_manager=mock_var_manager, all_vars=dict())
        tqm = TaskQueueManager(inventory=inventory, variable_manager=mock_var_manager, loader=fake_loader, passwords=None, forks=5)
        tqm._initialize_processes(3)
        strategy = StrategyModule(tqm)
        strategy._hosts_cache = [h.name for h in hosts]
        strategy._hosts_cache_all = [h.name for h in hosts]
        hosts_left = strategy.get_hosts_left(itr)
        hosts_tasks = strategy._get_next_task_lockstep(hosts_left, itr)
        host1_task = hosts_tasks[0][1]
        host2_task = hosts_tasks[1][1]
        self.assertIsNotNone(host1_task)
        self.assertIsNotNone(host2_task)
        self.assertEqual(host1_task.action, 'meta')
        self.assertEqual(host2_task.action, 'meta')
        hosts_left = strategy.get_hosts_left(itr)
        hosts_tasks = strategy._get_next_task_lockstep(hosts_left, itr)
        host1_task = hosts_tasks[0][1]
        host2_task = hosts_tasks[1][1]
        self.assertIsNotNone(host1_task)
        self.assertIsNotNone(host2_task)
        self.assertEqual(host1_task.action, 'debug')
        self.assertEqual(host2_task.action, 'debug')
        self.assertEqual(host1_task.name, 'task1')
        self.assertEqual(host2_task.name, 'task1')
        itr.mark_host_failed(hosts[1])
        hosts_left = strategy.get_hosts_left(itr)
        hosts_tasks = strategy._get_next_task_lockstep(hosts_left, itr)
        host1_task = hosts_tasks[0][1]
        host2_task = hosts_tasks[1][1]
        self.assertIsNotNone(host1_task)
        self.assertIsNotNone(host2_task)
        self.assertEqual(host1_task.action, 'debug')
        self.assertEqual(host2_task.action, 'meta')
        self.assertEqual(host1_task.name, 'task2')
        self.assertEqual(host2_task.name, '')
        hosts_left = strategy.get_hosts_left(itr)
        hosts_tasks = strategy._get_next_task_lockstep(hosts_left, itr)
        host1_task = hosts_tasks[0][1]
        host2_task = hosts_tasks[1][1]
        self.assertIsNotNone(host1_task)
        self.assertIsNotNone(host2_task)
        self.assertEqual(host1_task.action, 'meta')
        self.assertEqual(host2_task.action, 'debug')
        self.assertEqual(host1_task.name, '')
        self.assertEqual(host2_task.name, 'rescue1')
        hosts_left = strategy.get_hosts_left(itr)
        hosts_tasks = strategy._get_next_task_lockstep(hosts_left, itr)
        host1_task = hosts_tasks[0][1]
        host2_task = hosts_tasks[1][1]
        self.assertIsNotNone(host1_task)
        self.assertIsNotNone(host2_task)
        self.assertEqual(host1_task.action, 'meta')
        self.assertEqual(host2_task.action, 'debug')
        self.assertEqual(host1_task.name, '')
        self.assertEqual(host2_task.name, 'rescue2')
        hosts_left = strategy.get_hosts_left(itr)
        hosts_tasks = strategy._get_next_task_lockstep(hosts_left, itr)
        host1_task = hosts_tasks[0][1]
        host2_task = hosts_tasks[1][1]
        self.assertIsNotNone(host1_task)
        self.assertIsNotNone(host2_task)
        self.assertEqual(host1_task.action, 'meta')
        self.assertEqual(host2_task.action, 'meta')
        hosts_left = strategy.get_hosts_left(itr)
        hosts_tasks = strategy._get_next_task_lockstep(hosts_left, itr)
        host1_task = hosts_tasks[0][1]
        host2_task = hosts_tasks[1][1]
        self.assertIsNotNone(host1_task)
        self.assertIsNotNone(host2_task)
        self.assertEqual(host1_task.action, 'meta')
        self.assertEqual(host2_task.action, 'meta')
        hosts_left = strategy.get_hosts_left(itr)
        hosts_tasks = strategy._get_next_task_lockstep(hosts_left, itr)
        host1_task = hosts_tasks[0][1]
        host2_task = hosts_tasks[1][1]
        self.assertIsNone(host1_task)
        self.assertIsNone(host2_task)

def test_TestStrategyLinear_test_noop():
    ret = TestStrategyLinear().test_noop()