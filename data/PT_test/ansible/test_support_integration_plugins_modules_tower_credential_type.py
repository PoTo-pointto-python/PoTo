from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'status': ['preview'], 'supported_by': 'community', 'metadata_version': '1.1'}
DOCUMENTATION = '\n---\nmodule: tower_credential_type\nauthor: "Adrien Fleury (@fleu42)"\nversion_added: "2.7"\nshort_description: Create, update, or destroy custom Ansible Tower credential type.\ndescription:\n    - Create, update, or destroy Ansible Tower credential type. See\n      U(https://www.ansible.com/tower) for an overview.\noptions:\n    name:\n      description:\n        - The name of the credential type.\n      required: True\n    description:\n      description:\n        - The description of the credential type to give more detail about it.\n      required: False\n    kind:\n      description:\n        - >-\n          The type of credential type being added. Note that only cloud and\n          net can be used for creating credential types. Refer to the Ansible\n          for more information.\n      choices: [ \'ssh\', \'vault\', \'net\', \'scm\', \'cloud\', \'insights\' ]\n      required: False\n    inputs:\n      description:\n        - >-\n          Enter inputs using either JSON or YAML syntax. Refer to the Ansible\n          Tower documentation for example syntax.\n      required: False\n    injectors:\n      description:\n        - >-\n          Enter injectors using either JSON or YAML syntax. Refer to the\n          Ansible Tower documentation for example syntax.\n      required: False\n    state:\n      description:\n        - Desired state of the resource.\n      required: False\n      default: "present"\n      choices: ["present", "absent"]\n    validate_certs:\n      description:\n        - Tower option to avoid certificates check.\n      required: False\n      type: bool\n      aliases: [ tower_verify_ssl ]\nextends_documentation_fragment: tower\n'
EXAMPLES = '\n- tower_credential_type:\n    name: Nexus\n    description: Credentials type for Nexus\n    kind: cloud\n    inputs: "{{ lookup(\'file\', \'tower_credential_inputs_nexus.json\') }}"\n    injectors: {\'extra_vars\': {\'nexus_credential\': \'test\' }}\n    state: present\n    validate_certs: false\n\n- tower_credential_type:\n    name: Nexus\n    state: absent\n'
RETURN = ' # '
from ansible.module_utils.ansible_tower import TowerModule, tower_auth_config, tower_check_mode
try:
    import tower_cli
    import tower_cli.exceptions as exc
    from tower_cli.conf import settings
except ImportError:
    pass
KIND_CHOICES = {'ssh': 'Machine', 'vault': 'Ansible Vault', 'net': 'Network', 'scm': 'Source Control', 'cloud': 'Lots of others', 'insights': 'Insights'}

def main():
    argument_spec = dict(name=dict(required=True), description=dict(required=False), kind=dict(required=False, choices=KIND_CHOICES.keys()), inputs=dict(type='dict', required=False), injectors=dict(type='dict', required=False), state=dict(choices=['present', 'absent'], default='present'))
    module = TowerModule(argument_spec=argument_spec, supports_check_mode=False)
    name = module.params.get('name')
    kind = module.params.get('kind')
    state = module.params.get('state')
    json_output = {'credential_type': name, 'state': state}
    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        tower_check_mode(module)
        credential_type_res = tower_cli.get_resource('credential_type')
        params = {}
        params['name'] = name
        params['kind'] = kind
        params['managed_by_tower'] = False
        if module.params.get('description'):
            params['description'] = module.params.get('description')
        if module.params.get('inputs'):
            params['inputs'] = module.params.get('inputs')
        if module.params.get('injectors'):
            params['injectors'] = module.params.get('injectors')
        try:
            if state == 'present':
                params['create_on_missing'] = True
                result = credential_type_res.modify(**params)
                json_output['id'] = result['id']
            elif state == 'absent':
                params['fail_on_missing'] = False
                result = credential_type_res.delete(**params)
        except (exc.ConnectionError, exc.BadRequest, exc.AuthError) as excinfo:
            module.fail_json(msg='Failed to update credential type: {0}'.format(excinfo), changed=False)
    json_output['changed'] = result['changed']
    module.exit_json(**json_output)
if __name__ == '__main__':
    main()