from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'network'}
DOCUMENTATION = "module: cli_config\nauthor: Trishna Guha (@trishnaguha)\nnotes:\n- The commands will be returned only for platforms that do not support onbox diff.\n  The C(--diff) option with the playbook will return the difference in configuration\n  for devices that has support for onbox diff\nshort_description: Push text based configuration to network devices over network_cli\ndescription:\n- This module provides platform agnostic way of pushing text based configuration to\n  network devices over network_cli connection plugin.\nextends_documentation_fragment:\n- ansible.netcommon.network_agnostic\noptions:\n  config:\n    description:\n    - The config to be pushed to the network device. This argument is mutually exclusive\n      with C(rollback) and either one of the option should be given as input. The\n      config should have indentation that the device uses.\n    type: str\n  commit:\n    description:\n    - The C(commit) argument instructs the module to push the configuration to the\n      device. This is mapped to module check mode.\n    type: bool\n  replace:\n    description:\n    - If the C(replace) argument is set to C(yes), it will replace the entire running-config\n      of the device with the C(config) argument value. For devices that support replacing\n      running configuration from file on device like NXOS/JUNOS, the C(replace) argument\n      takes path to the file on the device that will be used for replacing the entire\n      running-config. The value of C(config) option should be I(None) for such devices.\n      Nexus 9K devices only support replace. Use I(net_put) or I(nxos_file_copy) in\n      case of NXOS module to copy the flat file to remote device and then use set\n      the fullpath to this argument.\n    type: str\n  backup:\n    description:\n    - This argument will cause the module to create a full backup of the current running\n      config from the remote device before any changes are made. If the C(backup_options)\n      value is not given, the backup file is written to the C(backup) folder in the\n      playbook root directory or role root directory, if playbook is part of an ansible\n      role. If the directory does not exist, it is created.\n    type: bool\n    default: 'no'\n  rollback:\n    description:\n    - The C(rollback) argument instructs the module to rollback the current configuration\n      to the identifier specified in the argument.  If the specified rollback identifier\n      does not exist on the remote device, the module will fail. To rollback to the\n      most recent commit, set the C(rollback) argument to 0. This option is mutually\n      exclusive with C(config).\n  commit_comment:\n    description:\n    - The C(commit_comment) argument specifies a text string to be used when committing\n      the configuration. If the C(commit) argument is set to False, this argument\n      is silently ignored. This argument is only valid for the platforms that support\n      commit operation with comment.\n    type: str\n  defaults:\n    description:\n    - The I(defaults) argument will influence how the running-config is collected\n      from the device.  When the value is set to true, the command used to collect\n      the running-config is append with the all keyword.  When the value is set to\n      false, the command is issued without the all keyword.\n    default: 'no'\n    type: bool\n  multiline_delimiter:\n    description:\n    - This argument is used when pushing a multiline configuration element to the\n      device. It specifies the character to use as the delimiting character. This\n      only applies to the configuration action.\n    type: str\n  diff_replace:\n    description:\n    - Instructs the module on the way to perform the configuration on the device.\n      If the C(diff_replace) argument is set to I(line) then the modified lines are\n      pushed to the device in configuration mode. If the argument is set to I(block)\n      then the entire command block is pushed to the device in configuration mode\n      if any line is not correct. Note that this parameter will be ignored if the\n      platform has onbox diff support.\n    choices:\n    - line\n    - block\n    - config\n  diff_match:\n    description:\n    - Instructs the module on the way to perform the matching of the set of commands\n      against the current device config. If C(diff_match) is set to I(line), commands\n      are matched line by line. If C(diff_match) is set to I(strict), command lines\n      are matched with respect to position. If C(diff_match) is set to I(exact), command\n      lines must be an equal match. Finally, if C(diff_match) is set to I(none), the\n      module will not attempt to compare the source configuration with the running\n      configuration on the remote device. Note that this parameter will be ignored\n      if the platform has onbox diff support.\n    choices:\n    - line\n    - strict\n    - exact\n    - none\n  diff_ignore_lines:\n    description:\n    - Use this argument to specify one or more lines that should be ignored during\n      the diff. This is used for lines in the configuration that are automatically\n      updated by the system. This argument takes a list of regular expressions or\n      exact line matches. Note that this parameter will be ignored if the platform\n      has onbox diff support.\n  backup_options:\n    description:\n    - This is a dict object containing configurable options related to backup file\n      path. The value of this option is read only when C(backup) is set to I(yes),\n      if C(backup) is set to I(no) this option will be silently ignored.\n    suboptions:\n      filename:\n        description:\n        - The filename to be used to store the backup configuration. If the filename\n          is not given it will be generated based on the hostname, current time and\n          date in format defined by <hostname>_config.<current-date>@<current-time>\n      dir_path:\n        description:\n        - This option provides the path ending with directory name in which the backup\n          configuration file will be stored. If the directory does not exist it will\n          be first created and the filename is either the value of C(filename) or\n          default filename as described in C(filename) options description. If the\n          path value is not given in that case a I(backup) directory will be created\n          in the current working directory and backup configuration will be copied\n          in C(filename) within I(backup) directory.\n        type: path\n    type: dict\n"
EXAMPLES = '\n- name: configure device with config\n  cli_config:\n    config: "{{ lookup(\'template\', \'basic/config.j2\') }}"\n\n- name: multiline config\n  cli_config:\n    config: |\n      hostname foo\n      feature nxapi\n\n- name: configure device with config with defaults enabled\n  cli_config:\n    config: "{{ lookup(\'template\', \'basic/config.j2\') }}"\n    defaults: yes\n\n- name: Use diff_match\n  cli_config:\n    config: "{{ lookup(\'file\', \'interface_config\') }}"\n    diff_match: none\n\n- name: nxos replace config\n  cli_config:\n    replace: \'bootflash:nxoscfg\'\n\n- name: junos replace config\n  cli_config:\n    replace: \'/var/home/ansible/junos01.cfg\'\n\n- name: commit with comment\n  cli_config:\n    config: set system host-name foo\n    commit_comment: this is a test\n\n- name: configurable backup path\n  cli_config:\n    config: "{{ lookup(\'template\', \'basic/config.j2\') }}"\n    backup: yes\n    backup_options:\n      filename: backup.cfg\n      dir_path: /home/user\n'
RETURN = "\ncommands:\n  description: The set of commands that will be pushed to the remote device\n  returned: always\n  type: list\n  sample: ['interface Loopback999', 'no shutdown']\nbackup_path:\n  description: The full path to the backup file\n  returned: when backup is yes\n  type: str\n  sample: /playbooks/ansible/backup/hostname_config.2016-07-16@22:28:34\n"
import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection
from ansible.module_utils._text import to_text

def validate_args(module, device_operations):
    """validate param if it is supported on the platform
    """
    feature_list = ['replace', 'rollback', 'commit_comment', 'defaults', 'multiline_delimiter', 'diff_replace', 'diff_match', 'diff_ignore_lines']
    for feature in feature_list:
        if module.params[feature]:
            supports_feature = device_operations.get('supports_%s' % feature)
            if supports_feature is None:
                module.fail_json("This platform does not specify whether %s is supported or not. Please report an issue against this platform's cliconf plugin." % feature)
            elif not supports_feature:
                module.fail_json(msg='Option %s is not supported on this platform' % feature)

def run(module, device_operations, connection, candidate, running, rollback_id):
    result = {}
    resp = {}
    config_diff = []
    banner_diff = {}
    replace = module.params['replace']
    commit_comment = module.params['commit_comment']
    multiline_delimiter = module.params['multiline_delimiter']
    diff_replace = module.params['diff_replace']
    diff_match = module.params['diff_match']
    diff_ignore_lines = module.params['diff_ignore_lines']
    commit = not module.check_mode
    if replace in ('yes', 'true', 'True'):
        replace = True
    elif replace in ('no', 'false', 'False'):
        replace = False
    if replace is not None and replace not in [True, False] and (candidate is not None):
        module.fail_json(msg="Replace value '%s' is a configuration file path already present on the device. Hence 'replace' and 'config' options are mutually exclusive" % replace)
    if rollback_id is not None:
        resp = connection.rollback(rollback_id, commit)
        if 'diff' in resp:
            result['changed'] = True
    elif device_operations.get('supports_onbox_diff'):
        if diff_replace:
            module.warn('diff_replace is ignored as the device supports onbox diff')
        if diff_match:
            module.warn('diff_mattch is ignored as the device supports onbox diff')
        if diff_ignore_lines:
            module.warn('diff_ignore_lines is ignored as the device supports onbox diff')
        if candidate and (not isinstance(candidate, list)):
            candidate = candidate.strip('\n').splitlines()
        kwargs = {'candidate': candidate, 'commit': commit, 'replace': replace, 'comment': commit_comment}
        resp = connection.edit_config(**kwargs)
        if 'diff' in resp:
            result['changed'] = True
    elif device_operations.get('supports_generate_diff'):
        kwargs = {'candidate': candidate, 'running': running}
        if diff_match:
            kwargs.update({'diff_match': diff_match})
        if diff_replace:
            kwargs.update({'diff_replace': diff_replace})
        if diff_ignore_lines:
            kwargs.update({'diff_ignore_lines': diff_ignore_lines})
        diff_response = connection.get_diff(**kwargs)
        config_diff = diff_response.get('config_diff')
        banner_diff = diff_response.get('banner_diff')
        if config_diff:
            if isinstance(config_diff, list):
                candidate = config_diff
            else:
                candidate = config_diff.splitlines()
            kwargs = {'candidate': candidate, 'commit': commit, 'replace': replace, 'comment': commit_comment}
            if commit:
                connection.edit_config(**kwargs)
            result['changed'] = True
            result['commands'] = config_diff.split('\n')
        if banner_diff:
            candidate = json.dumps(banner_diff)
            kwargs = {'candidate': candidate, 'commit': commit}
            if multiline_delimiter:
                kwargs.update({'multiline_delimiter': multiline_delimiter})
            if commit:
                connection.edit_banner(**kwargs)
            result['changed'] = True
    if module._diff:
        if 'diff' in resp:
            result['diff'] = {'prepared': resp['diff']}
        else:
            diff = ''
            if config_diff:
                if isinstance(config_diff, list):
                    diff += '\n'.join(config_diff)
                else:
                    diff += config_diff
            if banner_diff:
                diff += json.dumps(banner_diff)
            result['diff'] = {'prepared': diff}
    return result

def main():
    """main entry point for execution
    """
    backup_spec = dict(filename=dict(), dir_path=dict(type='path'))
    argument_spec = dict(backup=dict(default=False, type='bool'), backup_options=dict(type='dict', options=backup_spec), config=dict(type='str'), commit=dict(type='bool'), replace=dict(type='str'), rollback=dict(type='int'), commit_comment=dict(type='str'), defaults=dict(default=False, type='bool'), multiline_delimiter=dict(type='str'), diff_replace=dict(choices=['line', 'block', 'config']), diff_match=dict(choices=['line', 'strict', 'exact', 'none']), diff_ignore_lines=dict(type='list'))
    mutually_exclusive = [('config', 'rollback')]
    required_one_of = [['backup', 'config', 'rollback']]
    module = AnsibleModule(argument_spec=argument_spec, mutually_exclusive=mutually_exclusive, required_one_of=required_one_of, supports_check_mode=True)
    result = {'changed': False}
    connection = Connection(module._socket_path)
    capabilities = module.from_json(connection.get_capabilities())
    if capabilities:
        device_operations = capabilities.get('device_operations', dict())
        validate_args(module, device_operations)
    else:
        device_operations = dict()
    if module.params['defaults']:
        if 'get_default_flag' in capabilities.get('rpc'):
            flags = connection.get_default_flag()
        else:
            flags = 'all'
    else:
        flags = []
    candidate = module.params['config']
    candidate = to_text(candidate, errors='surrogate_then_replace') if candidate else None
    running = connection.get_config(flags=flags)
    rollback_id = module.params['rollback']
    if module.params['backup']:
        result['__backup__'] = running
    if candidate or rollback_id or module.params['replace']:
        try:
            result.update(run(module, device_operations, connection, candidate, running, rollback_id))
        except Exception as exc:
            module.fail_json(msg=to_text(exc))
    module.exit_json(**result)
if __name__ == '__main__':
    main()