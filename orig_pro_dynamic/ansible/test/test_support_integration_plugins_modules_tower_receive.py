from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: tower_receive\nauthor: "John Westcott IV (@john-westcott-iv)"\nversion_added: "2.8"\nshort_description: Receive assets from Ansible Tower.\ndescription:\n    - Receive assets from Ansible Tower. See\n      U(https://www.ansible.com/tower) for an overview.\noptions:\n    all:\n      description:\n        - Export all assets\n      type: bool\n      default: \'False\'\n    organization:\n      description:\n        - List of organization names to export\n      default: []\n    user:\n      description:\n        - List of user names to export\n      default: []\n    team:\n      description:\n        - List of team names to export\n      default: []\n    credential_type:\n      description:\n        - List of credential type names to export\n      default: []\n    credential:\n      description:\n        - List of credential names to export\n      default: []\n    notification_template:\n      description:\n        - List of notification template names to export\n      default: []\n    inventory_script:\n      description:\n        - List of inventory script names to export\n      default: []\n    inventory:\n      description:\n        - List of inventory names to export\n      default: []\n    project:\n      description:\n        - List of project names to export\n      default: []\n    job_template:\n      description:\n        - List of job template names to export\n      default: []\n    workflow:\n      description:\n        - List of workflow names to export\n      default: []\n\nrequirements:\n  - "ansible-tower-cli >= 3.3.0"\n\nnotes:\n  - Specifying a name of "all" for any asset type will export all items of that asset type.\n\nextends_documentation_fragment: tower\n'
EXAMPLES = '\n- name: Export all tower assets\n  tower_receive:\n    all: True\n    tower_config_file: "~/tower_cli.cfg"\n\n- name: Export all inventories\n  tower_receive:\n    inventory:\n      - all\n\n- name: Export a job template named "My Template" and all Credentials\n  tower_receive:\n    job_template:\n      - "My Template"\n    credential:\n      - all\n'
RETURN = '\nassets:\n    description: The exported assets\n    returned: success\n    type: dict\n    sample: [ {}, {} ]\n'
from ansible.module_utils.ansible_tower import TowerModule, tower_auth_config, HAS_TOWER_CLI
try:
    from tower_cli.cli.transfer.receive import Receiver
    from tower_cli.cli.transfer.common import SEND_ORDER
    from tower_cli.utils.exceptions import TowerCLIError
    from tower_cli.conf import settings
    TOWER_CLI_HAS_EXPORT = True
except ImportError:
    TOWER_CLI_HAS_EXPORT = False

def main():
    argument_spec = dict(all=dict(type='bool', default=False), credential=dict(type='list', default=[]), credential_type=dict(type='list', default=[]), inventory=dict(type='list', default=[]), inventory_script=dict(type='list', default=[]), job_template=dict(type='list', default=[]), notification_template=dict(type='list', default=[]), organization=dict(type='list', default=[]), project=dict(type='list', default=[]), team=dict(type='list', default=[]), user=dict(type='list', default=[]), workflow=dict(type='list', default=[]))
    module = TowerModule(argument_spec=argument_spec, supports_check_mode=False)
    if not HAS_TOWER_CLI:
        module.fail_json(msg='ansible-tower-cli required for this module')
    if not TOWER_CLI_HAS_EXPORT:
        module.fail_json(msg='ansible-tower-cli version does not support export')
    export_all = module.params.get('all')
    assets_to_export = {}
    for asset_type in SEND_ORDER:
        assets_to_export[asset_type] = module.params.get(asset_type)
    result = dict(assets=None, changed=False, message='')
    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        try:
            receiver = Receiver()
            result['assets'] = receiver.export_assets(all=export_all, asset_input=assets_to_export)
            module.exit_json(**result)
        except TowerCLIError as e:
            result['message'] = e.message
            module.fail_json(msg='Receive Failed', **result)
if __name__ == '__main__':
    main()