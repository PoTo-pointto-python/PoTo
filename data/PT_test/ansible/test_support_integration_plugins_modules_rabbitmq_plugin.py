from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: rabbitmq_plugin\nshort_description: Manage RabbitMQ plugins\ndescription:\n  - This module can be used to enable or disable RabbitMQ plugins.\nversion_added: "1.1"\nauthor:\n  - Chris Hoffman (@chrishoffman)\noptions:\n  names:\n    description:\n      - Comma-separated list of plugin names. Also, accepts plugin name.\n    required: true\n    aliases: [name]\n  new_only:\n    description:\n      - Only enable missing plugins.\n      - Does not disable plugins that are not in the names list.\n    type: bool\n    default: "no"\n  state:\n    description:\n      - Specify if plugins are to be enabled or disabled.\n    default: enabled\n    choices: [enabled, disabled]\n  prefix:\n    description:\n      - Specify a custom install prefix to a Rabbit.\n    version_added: "1.3"\n'
EXAMPLES = "\n- name: Enables the rabbitmq_management plugin\n  rabbitmq_plugin:\n    names: rabbitmq_management\n    state: enabled\n\n- name: Enable multiple rabbitmq plugins\n  rabbitmq_plugin:\n    names: rabbitmq_management,rabbitmq_management_visualiser\n    state: enabled\n\n- name: Disable plugin\n  rabbitmq_plugin:\n    names: rabbitmq_management\n    state: disabled\n\n- name: Enable every plugin in list with existing plugins\n  rabbitmq_plugin:\n    names: rabbitmq_management,rabbitmq_management_visualiser,rabbitmq_shovel,rabbitmq_shovel_management\n    state: enabled\n    new_only: 'yes'\n"
RETURN = '\nenabled:\n  description: list of plugins enabled during task run\n  returned: always\n  type: list\n  sample: ["rabbitmq_management"]\ndisabled:\n  description: list of plugins disabled during task run\n  returned: always\n  type: list\n  sample: ["rabbitmq_management"]\n'
import os
from ansible.module_utils.basic import AnsibleModule

class RabbitMqPlugins(object):

    def __init__(self, module):
        self.module = module
        bin_path = ''
        if module.params['prefix']:
            if os.path.isdir(os.path.join(module.params['prefix'], 'bin')):
                bin_path = os.path.join(module.params['prefix'], 'bin')
            elif os.path.isdir(os.path.join(module.params['prefix'], 'sbin')):
                bin_path = os.path.join(module.params['prefix'], 'sbin')
            else:
                module.fail_json(msg='No binary folder in prefix %s' % module.params['prefix'])
            self._rabbitmq_plugins = os.path.join(bin_path, 'rabbitmq-plugins')
        else:
            self._rabbitmq_plugins = module.get_bin_path('rabbitmq-plugins', True)

    def _exec(self, args, run_in_check_mode=False):
        if not self.module.check_mode or (self.module.check_mode and run_in_check_mode):
            cmd = [self._rabbitmq_plugins]
            (rc, out, err) = self.module.run_command(cmd + args, check_rc=True)
            return out.splitlines()
        return list()

    def get_all(self):
        list_output = self._exec(['list', '-E', '-m'], True)
        plugins = []
        for plugin in list_output:
            if not plugin:
                break
            plugins.append(plugin)
        return plugins

    def enable(self, name):
        self._exec(['enable', name])

    def disable(self, name):
        self._exec(['disable', name])

def main():
    arg_spec = dict(names=dict(required=True, aliases=['name']), new_only=dict(default='no', type='bool'), state=dict(default='enabled', choices=['enabled', 'disabled']), prefix=dict(required=False, default=None))
    module = AnsibleModule(argument_spec=arg_spec, supports_check_mode=True)
    result = dict()
    names = module.params['names'].split(',')
    new_only = module.params['new_only']
    state = module.params['state']
    rabbitmq_plugins = RabbitMqPlugins(module)
    enabled_plugins = rabbitmq_plugins.get_all()
    enabled = []
    disabled = []
    if state == 'enabled':
        if not new_only:
            for plugin in enabled_plugins:
                if ' ' in plugin:
                    continue
                if plugin not in names:
                    rabbitmq_plugins.disable(plugin)
                    disabled.append(plugin)
        for name in names:
            if name not in enabled_plugins:
                rabbitmq_plugins.enable(name)
                enabled.append(name)
    else:
        for plugin in enabled_plugins:
            if plugin in names:
                rabbitmq_plugins.disable(plugin)
                disabled.append(plugin)
    result['changed'] = len(enabled) > 0 or len(disabled) > 0
    result['enabled'] = enabled
    result['disabled'] = disabled
    module.exit_json(**result)
if __name__ == '__main__':
    main()

def test_RabbitMqPlugins__exec():
    ret = RabbitMqPlugins()._exec()

def test_RabbitMqPlugins_get_all():
    ret = RabbitMqPlugins().get_all()

def test_RabbitMqPlugins_enable():
    ret = RabbitMqPlugins().enable()

def test_RabbitMqPlugins_disable():
    ret = RabbitMqPlugins().disable()