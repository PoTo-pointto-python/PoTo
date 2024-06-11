from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from units.mock.loader import DictDataLoader
from ansible import context
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.cli.playbook import PlaybookCLI

class TestPlaybookCLI(unittest.TestCase):

    def test_flush_cache(self):
        cli = PlaybookCLI(args=['ansible-playbook', '--flush-cache', 'foobar.yml'])
        cli.parse()
        self.assertTrue(context.CLIARGS['flush_cache'])
        variable_manager = VariableManager()
        fake_loader = DictDataLoader({'foobar.yml': ''})
        inventory = InventoryManager(loader=fake_loader, sources='testhost,')
        variable_manager.set_host_facts('testhost', {'canary': True})
        self.assertTrue('testhost' in variable_manager._fact_cache)
        cli._flush_cache(inventory, variable_manager)
        self.assertFalse('testhost' in variable_manager._fact_cache)

def test_TestPlaybookCLI_test_flush_cache():
    ret = TestPlaybookCLI().test_flush_cache()