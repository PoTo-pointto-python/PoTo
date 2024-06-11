from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from ansible.errors import AnsibleParserError
from ansible.playbook import Playbook
from ansible.vars.manager import VariableManager
from units.mock.loader import DictDataLoader

class TestPlaybook(unittest.TestCase):

    def test_empty_playbook(self):
        fake_loader = DictDataLoader({})
        p = Playbook(loader=fake_loader)

    def test_basic_playbook(self):
        fake_loader = DictDataLoader({'test_file.yml': '\n            - hosts: all\n            '})
        p = Playbook.load('test_file.yml', loader=fake_loader)
        plays = p.get_plays()

    def test_bad_playbook_files(self):
        fake_loader = DictDataLoader({'bad_list.yml': '\n            foo: bar\n\n            ', 'bad_entry.yml': '\n            -\n              - "This should be a mapping..."\n\n            '})
        vm = VariableManager()
        self.assertRaises(AnsibleParserError, Playbook.load, 'bad_list.yml', vm, fake_loader)
        self.assertRaises(AnsibleParserError, Playbook.load, 'bad_entry.yml', vm, fake_loader)

def test_TestPlaybook_test_empty_playbook():
    ret = TestPlaybook().test_empty_playbook()

def test_TestPlaybook_test_basic_playbook():
    ret = TestPlaybook().test_basic_playbook()

def test_TestPlaybook_test_bad_playbook_files():
    ret = TestPlaybook().test_bad_playbook_files()