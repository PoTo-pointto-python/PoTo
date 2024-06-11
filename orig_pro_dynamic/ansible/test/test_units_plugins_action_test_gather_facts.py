from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from units.compat.mock import MagicMock, patch
from ansible import constants as C
from ansible.plugins.action.gather_facts import ActionModule
from ansible.playbook.task import Task
from ansible.template import Templar
import ansible.executor.module_common as module_common
from units.mock.loader import DictDataLoader

class TestNetworkFacts(unittest.TestCase):
    task = MagicMock(Task)
    play_context = MagicMock()
    play_context.check_mode = False
    connection = MagicMock()
    fake_loader = DictDataLoader({})
    templar = Templar(loader=fake_loader)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_network_gather_facts(self):
        self.task_vars = {'ansible_network_os': 'ios'}
        self.task.action = 'gather_facts'
        self.task.async_val = False
        self.task._ansible_internal_redirect_list = []
        self.task.args = {'gather_subset': 'min'}
        self.task.module_defaults = [{'ios_facts': {'gather_subset': 'min'}}]
        plugin = ActionModule(self.task, self.connection, self.play_context, loader=None, templar=self.templar, shared_loader_obj=None)
        plugin._execute_module = MagicMock()
        res = plugin.run(task_vars=self.task_vars)
        self.assertEqual(res['ansible_facts']['_ansible_facts_gathered'], True)
        mod_args = plugin._get_module_args('ios_facts', task_vars=self.task_vars)
        self.assertEqual(mod_args['gather_subset'], 'min')
        facts_modules = C.config.get_config_value('FACTS_MODULES', variables=self.task_vars)
        self.assertEqual(facts_modules, ['ansible.legacy.ios_facts'])

    @patch.object(module_common, '_get_collection_metadata', return_value={})
    def test_network_gather_facts_fqcn(self, mock_collection_metadata):
        self.fqcn_task_vars = {'ansible_network_os': 'cisco.ios.ios'}
        self.task.action = 'gather_facts'
        self.task._ansible_internal_redirect_list = ['cisco.ios.ios_facts']
        self.task.async_val = False
        self.task.args = {'gather_subset': 'min'}
        self.task.module_defaults = [{'cisco.ios.ios_facts': {'gather_subset': 'min'}}]
        plugin = ActionModule(self.task, self.connection, self.play_context, loader=None, templar=self.templar, shared_loader_obj=None)
        plugin._execute_module = MagicMock()
        res = plugin.run(task_vars=self.fqcn_task_vars)
        self.assertEqual(res['ansible_facts']['_ansible_facts_gathered'], True)
        mod_args = plugin._get_module_args('cisco.ios.ios_facts', task_vars=self.fqcn_task_vars)
        self.assertEqual(mod_args['gather_subset'], 'min')
        facts_modules = C.config.get_config_value('FACTS_MODULES', variables=self.fqcn_task_vars)
        self.assertEqual(facts_modules, ['cisco.ios.ios_facts'])

def test_TestNetworkFacts_setUp():
    ret = TestNetworkFacts().setUp()

def test_TestNetworkFacts_tearDown():
    ret = TestNetworkFacts().tearDown()

def test_TestNetworkFacts_test_network_gather_facts():
    ret = TestNetworkFacts().test_network_gather_facts()

def test_TestNetworkFacts_test_network_gather_facts_fqcn():
    ret = TestNetworkFacts().test_network_gather_facts_fqcn()