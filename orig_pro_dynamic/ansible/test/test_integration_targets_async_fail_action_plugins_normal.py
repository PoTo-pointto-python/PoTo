from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash

class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        self._supports_check_mode = True
        self._supports_async = True
        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp
        if not result.get('skipped'):
            if result.get('invocation', {}).get('module_args'):
                del result['invocation']['module_args']
            wrap_async = self._task.async_val and (not self._connection.has_native_async)
            result = merge_hash(result, self._execute_module(task_vars=task_vars, wrap_async=wrap_async))
            if self._task.action == 'setup':
                result['_ansible_verbose_override'] = True
        if self._task.action == 'async_status' and 'finished' in result and (result['finished'] != 1):
            raise AnsibleError('Pretend to fail somewher ein executing async_status')
        if not wrap_async:
            self._remove_tmp_path(self._connection._shell.tmpdir)
        return result

def test_ActionModule_run():
    ret = ActionModule().run()