from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from units.compat.mock import patch
from ansible.cli.console import ConsoleCLI

class TestConsoleCLI(unittest.TestCase):

    def test_parse(self):
        cli = ConsoleCLI(['ansible test'])
        cli.parse()
        self.assertTrue(cli.parser is not None)

    def test_module_args(self):
        cli = ConsoleCLI(['ansible test'])
        cli.parse()
        res = cli.module_args('copy')
        self.assertTrue(cli.parser is not None)
        self.assertIn('src', res)
        self.assertIn('backup', res)
        self.assertIsInstance(res, list)

    @patch('ansible.utils.display.Display.display')
    def test_helpdefault(self, mock_display):
        cli = ConsoleCLI(['ansible test'])
        cli.parse()
        cli.modules = set(['copy'])
        cli.helpdefault('copy')
        self.assertTrue(cli.parser is not None)
        self.assertTrue(len(mock_display.call_args_list) > 0, 'display.display should have been called but was not')

def test_TestConsoleCLI_test_parse():
    ret = TestConsoleCLI().test_parse()

def test_TestConsoleCLI_test_module_args():
    ret = TestConsoleCLI().test_module_args()

def test_TestConsoleCLI_test_helpdefault():
    ret = TestConsoleCLI().test_helpdefault()