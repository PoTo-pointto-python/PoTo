from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible_collections.ansible.netcommon.plugins.action.net_base import ActionModule as _ActionModule

class ActionModule(_ActionModule):

    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp
        return result

def test_ActionModule_run():
    ret = ActionModule().run()