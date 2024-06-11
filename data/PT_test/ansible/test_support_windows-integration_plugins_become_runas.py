from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\n    become: runas\n    short_description: Run As user\n    description:\n        - This become plugins allows your remote/login user to execute commands as another user via the windows runas facility.\n    author: ansible (@core)\n    version_added: "2.8"\n    options:\n        become_user:\n            description: User you \'become\' to execute the task\n            ini:\n              - section: privilege_escalation\n                key: become_user\n              - section: runas_become_plugin\n                key: user\n            vars:\n              - name: ansible_become_user\n              - name: ansible_runas_user\n            env:\n              - name: ANSIBLE_BECOME_USER\n              - name: ANSIBLE_RUNAS_USER\n            required: True\n        become_flags:\n            description: Options to pass to runas, a space delimited list of k=v pairs\n            default: \'\'\n            ini:\n              - section: privilege_escalation\n                key: become_flags\n              - section: runas_become_plugin\n                key: flags\n            vars:\n              - name: ansible_become_flags\n              - name: ansible_runas_flags\n            env:\n              - name: ANSIBLE_BECOME_FLAGS\n              - name: ANSIBLE_RUNAS_FLAGS\n        become_pass:\n            description: password\n            ini:\n              - section: runas_become_plugin\n                key: password\n            vars:\n              - name: ansible_become_password\n              - name: ansible_become_pass\n              - name: ansible_runas_pass\n            env:\n              - name: ANSIBLE_BECOME_PASS\n              - name: ANSIBLE_RUNAS_PASS\n    notes:\n        - runas is really implemented in the powershell module handler and as such can only be used with winrm connections.\n        - This plugin ignores the \'become_exe\' setting as it uses an API and not an executable.\n        - The Secondary Logon service (seclogon) must be running to use runas\n'
from ansible.plugins.become import BecomeBase

class BecomeModule(BecomeBase):
    name = 'runas'

    def build_become_command(self, cmd, shell):
        return cmd

def test_BecomeModule_build_become_command():
    ret = BecomeModule().build_become_command()