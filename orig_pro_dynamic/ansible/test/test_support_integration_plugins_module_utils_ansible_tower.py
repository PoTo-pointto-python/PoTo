import os
import traceback
TOWER_CLI_IMP_ERR = None
try:
    import tower_cli.utils.exceptions as exc
    from tower_cli.utils import parser
    from tower_cli.api import client
    HAS_TOWER_CLI = True
except ImportError:
    TOWER_CLI_IMP_ERR = traceback.format_exc()
    HAS_TOWER_CLI = False
from ansible.module_utils.basic import AnsibleModule, missing_required_lib

def tower_auth_config(module):
    """tower_auth_config attempts to load the tower-cli.cfg file
    specified from the `tower_config_file` parameter. If found,
    if returns the contents of the file as a dictionary, else
    it will attempt to fetch values from the module params and
    only pass those values that have been set.
    """
    config_file = module.params.pop('tower_config_file', None)
    if config_file:
        if not os.path.exists(config_file):
            module.fail_json(msg='file not found: %s' % config_file)
        if os.path.isdir(config_file):
            module.fail_json(msg='directory can not be used as config file: %s' % config_file)
        with open(config_file, 'rb') as f:
            return parser.string_to_dict(f.read())
    else:
        auth_config = {}
        host = module.params.pop('tower_host', None)
        if host:
            auth_config['host'] = host
        username = module.params.pop('tower_username', None)
        if username:
            auth_config['username'] = username
        password = module.params.pop('tower_password', None)
        if password:
            auth_config['password'] = password
        module.params.pop('tower_verify_ssl', None)
        verify_ssl = module.params.pop('validate_certs', None)
        if verify_ssl is not None:
            auth_config['verify_ssl'] = verify_ssl
        return auth_config

def tower_check_mode(module):
    """Execute check mode logic for Ansible Tower modules"""
    if module.check_mode:
        try:
            result = client.get('/ping').json()
            module.exit_json(changed=True, tower_version='{0}'.format(result['version']))
        except (exc.ServerError, exc.ConnectionError, exc.BadRequest) as excinfo:
            module.fail_json(changed=False, msg='Failed check mode: {0}'.format(excinfo))

class TowerModule(AnsibleModule):

    def __init__(self, argument_spec, **kwargs):
        args = dict(tower_host=dict(), tower_username=dict(), tower_password=dict(no_log=True), validate_certs=dict(type='bool', aliases=['tower_verify_ssl']), tower_config_file=dict(type='path'))
        args.update(argument_spec)
        mutually_exclusive = kwargs.get('mutually_exclusive', [])
        kwargs['mutually_exclusive'] = mutually_exclusive.extend((('tower_config_file', 'tower_host'), ('tower_config_file', 'tower_username'), ('tower_config_file', 'tower_password'), ('tower_config_file', 'validate_certs')))
        super(TowerModule, self).__init__(argument_spec=args, **kwargs)
        if not HAS_TOWER_CLI:
            self.fail_json(msg=missing_required_lib('ansible-tower-cli'), exception=TOWER_CLI_IMP_ERR)