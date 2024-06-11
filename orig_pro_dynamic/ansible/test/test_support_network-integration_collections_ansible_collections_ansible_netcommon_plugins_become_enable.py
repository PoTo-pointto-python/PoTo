from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = "become: enable\nshort_description: Switch to elevated permissions on a network device\ndescription:\n- This become plugins allows elevated permissions on a remote network device.\nauthor: ansible (@core)\noptions:\n  become_pass:\n    description: password\n    ini:\n    - section: enable_become_plugin\n      key: password\n    vars:\n    - name: ansible_become_password\n    - name: ansible_become_pass\n    - name: ansible_enable_pass\n    env:\n    - name: ANSIBLE_BECOME_PASS\n    - name: ANSIBLE_ENABLE_PASS\nnotes:\n- enable is really implemented in the network connection handler and as such can only\n  be used with network connections.\n- This plugin ignores the 'become_exe' and 'become_user' settings as it uses an API\n  and not an executable.\n"
from ansible.plugins.become import BecomeBase

class BecomeModule(BecomeBase):
    name = 'ansible.netcommon.enable'

    def build_become_command(self, cmd, shell):
        return cmd

def test_BecomeModule_build_become_command():
    ret = BecomeModule().build_become_command()