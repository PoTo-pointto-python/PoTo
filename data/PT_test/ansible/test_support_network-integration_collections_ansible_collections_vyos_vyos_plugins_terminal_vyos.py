from __future__ import absolute_import, division, print_function
__metaclass__ = type
import os
import re
from ansible.plugins.terminal import TerminalBase
from ansible.errors import AnsibleConnectionFailure

class TerminalModule(TerminalBase):
    terminal_stdout_re = [re.compile(b'[\\r\\n]?[\\w+\\-\\.:\\/\\[\\]]+(?:\\([^\\)]+\\)){,3}(?:>|#) ?$'), re.compile(b'\\@[\\w\\-\\.]+:\\S+?[>#\\$] ?$')]
    terminal_stderr_re = [re.compile(b'\\n\\s*Invalid command:'), re.compile(b'\\nCommit failed'), re.compile(b'\\n\\s+Set failed')]
    terminal_length = os.getenv('ANSIBLE_VYOS_TERMINAL_LENGTH', 10000)

    def on_open_shell(self):
        try:
            for cmd in (b'set terminal length 0', b'set terminal width 512'):
                self._exec_cli_command(cmd)
            self._exec_cli_command(b'set terminal length %d' % self.terminal_length)
        except AnsibleConnectionFailure:
            raise AnsibleConnectionFailure('unable to set terminal parameters')

def test_TerminalModule_on_open_shell():
    ret = TerminalModule().on_open_shell()