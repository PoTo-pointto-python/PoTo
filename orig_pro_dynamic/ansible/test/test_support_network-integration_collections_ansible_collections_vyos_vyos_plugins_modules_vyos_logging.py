ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'network'}
DOCUMENTATION = 'module: vyos_logging\nauthor: Trishna Guha (@trishnaguha)\nshort_description: Manage logging on network devices\ndescription:\n- This module provides declarative management of logging on Vyatta Vyos devices.\nnotes:\n- Tested against VyOS 1.1.8 (helium).\n- This module works with connection C(network_cli). See L(the VyOS OS Platform Options,../network/user_guide/platform_vyos.html).\noptions:\n  dest:\n    description:\n    - Destination of the logs.\n    choices:\n    - console\n    - file\n    - global\n    - host\n    - user\n  name:\n    description:\n    - If value of C(dest) is I(file) it indicates file-name, for I(user) it indicates\n      username and for I(host) indicates the host name to be notified.\n  facility:\n    description:\n    - Set logging facility.\n  level:\n    description:\n    - Set logging severity levels.\n  aggregate:\n    description: List of logging definitions.\n  state:\n    description:\n    - State of the logging configuration.\n    default: present\n    choices:\n    - present\n    - absent\nextends_documentation_fragment:\n- vyos.vyos.vyos\n'
EXAMPLES = '\n- name: configure console logging\n  vyos_logging:\n    dest: console\n    facility: all\n    level: crit\n\n- name: remove console logging configuration\n  vyos_logging:\n    dest: console\n    state: absent\n\n- name: configure file logging\n  vyos_logging:\n    dest: file\n    name: test\n    facility: local3\n    level: err\n\n- name: Add logging aggregate\n  vyos_logging:\n    aggregate:\n      - { dest: file, name: test1, facility: all, level: info }\n      - { dest: file, name: test2, facility: news, level: debug }\n    state: present\n\n- name: Remove logging aggregate\n  vyos_logging:\n    aggregate:\n      - { dest: console, facility: all, level: info }\n      - { dest: console, facility: daemon, level: warning }\n      - { dest: file, name: test2, facility: news, level: debug }\n    state: absent\n'
RETURN = '\ncommands:\n  description: The list of configuration mode commands to send to the device\n  returned: always\n  type: list\n  sample:\n    - set system syslog global facility all level notice\n'
import re
from copy import deepcopy
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import remove_default_spec
from ansible_collections.vyos.vyos.plugins.module_utils.network.vyos.vyos import get_config, load_config
from ansible_collections.vyos.vyos.plugins.module_utils.network.vyos.vyos import vyos_argument_spec

def spec_to_commands(updates, module):
    commands = list()
    (want, have) = updates
    for w in want:
        dest = w['dest']
        name = w['name']
        facility = w['facility']
        level = w['level']
        state = w['state']
        del w['state']
        if state == 'absent' and w in have:
            if w['name']:
                commands.append('delete system syslog {0} {1} facility {2} level {3}'.format(dest, name, facility, level))
            else:
                commands.append('delete system syslog {0} facility {1} level {2}'.format(dest, facility, level))
        elif state == 'present' and w not in have:
            if w['name']:
                commands.append('set system syslog {0} {1} facility {2} level {3}'.format(dest, name, facility, level))
            else:
                commands.append('set system syslog {0} facility {1} level {2}'.format(dest, facility, level))
    return commands

def config_to_dict(module):
    data = get_config(module)
    obj = []
    for line in data.split('\n'):
        if line.startswith('set system syslog'):
            match = re.search('set system syslog (\\S+)', line, re.M)
            dest = match.group(1)
            if dest == 'host':
                match = re.search('host (\\S+)', line, re.M)
                name = match.group(1)
            elif dest == 'file':
                match = re.search('file (\\S+)', line, re.M)
                name = match.group(1)
            elif dest == 'user':
                match = re.search('user (\\S+)', line, re.M)
                name = match.group(1)
            else:
                name = None
            if 'facility' in line:
                match = re.search('facility (\\S+)', line, re.M)
                facility = match.group(1)
            if 'level' in line:
                match = re.search('level (\\S+)', line, re.M)
                level = match.group(1).strip("'")
                obj.append({'dest': dest, 'name': name, 'facility': facility, 'level': level})
    return obj

def map_params_to_obj(module, required_if=None):
    obj = []
    aggregate = module.params.get('aggregate')
    if aggregate:
        for item in aggregate:
            for key in item:
                if item.get(key) is None:
                    item[key] = module.params[key]
            module._check_required_if(required_if, item)
            obj.append(item.copy())
    else:
        if module.params['dest'] not in ('host', 'file', 'user'):
            module.params['name'] = None
        obj.append({'dest': module.params['dest'], 'name': module.params['name'], 'facility': module.params['facility'], 'level': module.params['level'], 'state': module.params['state']})
    return obj

def main():
    """ main entry point for module execution
    """
    element_spec = dict(dest=dict(type='str', choices=['console', 'file', 'global', 'host', 'user']), name=dict(type='str'), facility=dict(type='str'), level=dict(type='str'), state=dict(default='present', choices=['present', 'absent']))
    aggregate_spec = deepcopy(element_spec)
    remove_default_spec(aggregate_spec)
    argument_spec = dict(aggregate=dict(type='list', elements='dict', options=aggregate_spec))
    argument_spec.update(element_spec)
    argument_spec.update(vyos_argument_spec)
    required_if = [('dest', 'host', ['name', 'facility', 'level']), ('dest', 'file', ['name', 'facility', 'level']), ('dest', 'user', ['name', 'facility', 'level']), ('dest', 'console', ['facility', 'level']), ('dest', 'global', ['facility', 'level'])]
    module = AnsibleModule(argument_spec=argument_spec, required_if=required_if, supports_check_mode=True)
    warnings = list()
    result = {'changed': False}
    if warnings:
        result['warnings'] = warnings
    want = map_params_to_obj(module, required_if=required_if)
    have = config_to_dict(module)
    commands = spec_to_commands((want, have), module)
    result['commands'] = commands
    if commands:
        commit = not module.check_mode
        load_config(module, commands, commit=commit)
        result['changed'] = True
    module.exit_json(**result)
if __name__ == '__main__':
    main()