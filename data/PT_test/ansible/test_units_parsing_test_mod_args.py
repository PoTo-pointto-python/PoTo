from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pytest
import re
from ansible.errors import AnsibleParserError
from ansible.parsing.mod_args import ModuleArgsParser
from ansible.utils.sentinel import Sentinel

class TestModArgsDwim:
    INVALID_MULTIPLE_ACTIONS = (({'action': 'shell echo hi', 'local_action': 'shell echo hi'}, 'action and local_action are mutually exclusive'), ({'action': 'shell echo hi', 'shell': 'echo hi'}, 'conflicting action statements: shell, shell'), ({'local_action': 'shell echo hi', 'shell': 'echo hi'}, 'conflicting action statements: shell, shell'))

    def _debug(self, mod, args, to):
        print('RETURNED module = {0}'.format(mod))
        print('           args = {0}'.format(args))
        print('             to = {0}'.format(to))

    def test_basic_shell(self):
        m = ModuleArgsParser(dict(shell='echo hi'))
        (mod, args, to) = m.parse()
        self._debug(mod, args, to)
        assert mod == 'shell'
        assert args == dict(_raw_params='echo hi')
        assert to is Sentinel

    def test_basic_command(self):
        m = ModuleArgsParser(dict(command='echo hi'))
        (mod, args, to) = m.parse()
        self._debug(mod, args, to)
        assert mod == 'command'
        assert args == dict(_raw_params='echo hi')
        assert to is Sentinel

    def test_shell_with_modifiers(self):
        m = ModuleArgsParser(dict(shell='/bin/foo creates=/tmp/baz removes=/tmp/bleep'))
        (mod, args, to) = m.parse()
        self._debug(mod, args, to)
        assert mod == 'shell'
        assert args == dict(creates='/tmp/baz', removes='/tmp/bleep', _raw_params='/bin/foo')
        assert to is Sentinel

    def test_normal_usage(self):
        m = ModuleArgsParser(dict(copy='src=a dest=b'))
        (mod, args, to) = m.parse()
        self._debug(mod, args, to)
        assert mod, 'copy'
        assert args, dict(src='a', dest='b')
        assert to is Sentinel

    def test_complex_args(self):
        m = ModuleArgsParser(dict(copy=dict(src='a', dest='b')))
        (mod, args, to) = m.parse()
        self._debug(mod, args, to)
        assert mod, 'copy'
        assert args, dict(src='a', dest='b')
        assert to is Sentinel

    def test_action_with_complex(self):
        m = ModuleArgsParser(dict(action=dict(module='copy', src='a', dest='b')))
        (mod, args, to) = m.parse()
        self._debug(mod, args, to)
        assert mod == 'copy'
        assert args == dict(src='a', dest='b')
        assert to is Sentinel

    def test_action_with_complex_and_complex_args(self):
        m = ModuleArgsParser(dict(action=dict(module='copy', args=dict(src='a', dest='b'))))
        (mod, args, to) = m.parse()
        self._debug(mod, args, to)
        assert mod == 'copy'
        assert args == dict(src='a', dest='b')
        assert to is Sentinel

    def test_local_action_string(self):
        m = ModuleArgsParser(dict(local_action='copy src=a dest=b'))
        (mod, args, delegate_to) = m.parse()
        self._debug(mod, args, delegate_to)
        assert mod == 'copy'
        assert args == dict(src='a', dest='b')
        assert delegate_to == 'localhost'

    @pytest.mark.parametrize('args_dict, msg', INVALID_MULTIPLE_ACTIONS)
    def test_multiple_actions(self, args_dict, msg):
        (args_dict,  msg) = INVALID_MULTIPLE_ACTIONS[0]
        m = ModuleArgsParser(args_dict)
        with pytest.raises(AnsibleParserError) as err:
            m.parse()
        assert err.value.args[0] == msg

    def test_multiple_actions(self):
        args_dict = {'ping': 'data=hi', 'shell': 'echo hi'}
        m = ModuleArgsParser(args_dict)
        with pytest.raises(AnsibleParserError) as err:
            m.parse()
        assert err.value.args[0].startswith('conflicting action statements: ')
        actions = set(re.search('(\\w+), (\\w+)', err.value.args[0]).groups())
        assert actions == set(['ping', 'shell'])

    def test_bogus_action(self):
        args_dict = {'bogusaction': {}}
        m = ModuleArgsParser(args_dict)
        with pytest.raises(AnsibleParserError) as err:
            m.parse()
        assert err.value.args[0].startswith("couldn't resolve module/action 'bogusaction'")

def test_TestModArgsDwim__debug():
    ret = TestModArgsDwim()._debug()

def test_TestModArgsDwim_test_basic_shell():
    ret = TestModArgsDwim().test_basic_shell()

def test_TestModArgsDwim_test_basic_command():
    ret = TestModArgsDwim().test_basic_command()

def test_TestModArgsDwim_test_shell_with_modifiers():
    ret = TestModArgsDwim().test_shell_with_modifiers()

def test_TestModArgsDwim_test_normal_usage():
    ret = TestModArgsDwim().test_normal_usage()

def test_TestModArgsDwim_test_complex_args():
    ret = TestModArgsDwim().test_complex_args()

def test_TestModArgsDwim_test_action_with_complex():
    ret = TestModArgsDwim().test_action_with_complex()

def test_TestModArgsDwim_test_action_with_complex_and_complex_args():
    ret = TestModArgsDwim().test_action_with_complex_and_complex_args()

def test_TestModArgsDwim_test_local_action_string():
    ret = TestModArgsDwim().test_local_action_string()

def test_TestModArgsDwim_test_multiple_actions():
    ret = TestModArgsDwim().test_multiple_actions()

def test_TestModArgsDwim_test_multiple_actions():
    ret = TestModArgsDwim().test_multiple_actions()

def test_TestModArgsDwim_test_bogus_action():
    ret = TestModArgsDwim().test_bogus_action()