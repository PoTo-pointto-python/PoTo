from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from units.compat.mock import MagicMock
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.playbook import Playbook
from ansible.template import Templar
from ansible.utils import context_objects as co
from units.mock.loader import DictDataLoader

class TestPlaybookExecutor(unittest.TestCase):

    def setUp(self):
        co.GlobalCLIArgs._Singleton__instance = None

    def tearDown(self):
        co.GlobalCLIArgs._Singleton__instance = None

    def test_get_serialized_batches(self):
        fake_loader = DictDataLoader({'no_serial.yml': '\n            - hosts: all\n              gather_facts: no\n              tasks:\n              - debug: var=inventory_hostname\n            ', 'serial_int.yml': '\n            - hosts: all\n              gather_facts: no\n              serial: 2\n              tasks:\n              - debug: var=inventory_hostname\n            ', 'serial_pct.yml': '\n            - hosts: all\n              gather_facts: no\n              serial: 20%\n              tasks:\n              - debug: var=inventory_hostname\n            ', 'serial_list.yml': '\n            - hosts: all\n              gather_facts: no\n              serial: [1, 2, 3]\n              tasks:\n              - debug: var=inventory_hostname\n            ', 'serial_list_mixed.yml': '\n            - hosts: all\n              gather_facts: no\n              serial: [1, "20%", -1]\n              tasks:\n              - debug: var=inventory_hostname\n            '})
        mock_inventory = MagicMock()
        mock_var_manager = MagicMock()
        templar = Templar(loader=fake_loader)
        pbe = PlaybookExecutor(playbooks=['no_serial.yml', 'serial_int.yml', 'serial_pct.yml', 'serial_list.yml', 'serial_list_mixed.yml'], inventory=mock_inventory, variable_manager=mock_var_manager, loader=fake_loader, passwords=[])
        playbook = Playbook.load(pbe._playbooks[0], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(pbe._get_serialized_batches(play), [['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']])
        playbook = Playbook.load(pbe._playbooks[1], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(pbe._get_serialized_batches(play), [['host0', 'host1'], ['host2', 'host3'], ['host4', 'host5'], ['host6', 'host7'], ['host8', 'host9']])
        playbook = Playbook.load(pbe._playbooks[2], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(pbe._get_serialized_batches(play), [['host0', 'host1'], ['host2', 'host3'], ['host4', 'host5'], ['host6', 'host7'], ['host8', 'host9']])
        playbook = Playbook.load(pbe._playbooks[3], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(pbe._get_serialized_batches(play), [['host0'], ['host1', 'host2'], ['host3', 'host4', 'host5'], ['host6', 'host7', 'host8'], ['host9']])
        playbook = Playbook.load(pbe._playbooks[4], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']
        self.assertEqual(pbe._get_serialized_batches(play), [['host0'], ['host1', 'host2'], ['host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9']])
        playbook = Playbook.load(pbe._playbooks[2], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2']
        self.assertEqual(pbe._get_serialized_batches(play), [['host0'], ['host1'], ['host2']])
        playbook = Playbook.load(pbe._playbooks[2], variable_manager=mock_var_manager, loader=fake_loader)
        play = playbook.get_plays()[0]
        play.post_validate(templar)
        mock_inventory.get_hosts.return_value = ['host0', 'host1', 'host2', 'host3', 'host4', 'host5', 'host6', 'host7', 'host8', 'host9', 'host10']
        self.assertEqual(pbe._get_serialized_batches(play), [['host0', 'host1'], ['host2', 'host3'], ['host4', 'host5'], ['host6', 'host7'], ['host8', 'host9'], ['host10']])

def test_TestPlaybookExecutor_setUp():
    ret = TestPlaybookExecutor().setUp()

def test_TestPlaybookExecutor_tearDown():
    ret = TestPlaybookExecutor().tearDown()

def test_TestPlaybookExecutor_test_get_serialized_batches():
    ret = TestPlaybookExecutor().test_get_serialized_batches()