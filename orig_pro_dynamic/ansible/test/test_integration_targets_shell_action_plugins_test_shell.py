from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.plugins.action import ActionBase

class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp
        result['shell'] = self._connection._shell.SHELL_FAMILY
        return result

def test_ActionModule_run():
    ret = ActionModule().run()