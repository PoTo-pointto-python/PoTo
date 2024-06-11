from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: mongodb_parameter\nshort_description: Change an administrative parameter on a MongoDB server\ndescription:\n    - Change an administrative parameter on a MongoDB server.\nversion_added: "2.1"\noptions:\n    login_user:\n        description:\n            - The MongoDB username used to authenticate with.\n        type: str\n    login_password:\n        description:\n            - The login user\'s password used to authenticate with.\n        type: str\n    login_host:\n        description:\n            - The host running the database.\n        type: str\n        default: localhost\n    login_port:\n        description:\n            - The MongoDB port to connect to.\n        default: 27017\n        type: int\n    login_database:\n        description:\n            - The database where login credentials are stored.\n        type: str\n    replica_set:\n        description:\n            - Replica set to connect to (automatically connects to primary for writes).\n        type: str\n    ssl:\n        description:\n            - Whether to use an SSL connection when connecting to the database.\n        type: bool\n        default: no\n    param:\n        description:\n            - MongoDB administrative parameter to modify.\n        type: str\n        required: true\n    value:\n        description:\n            - MongoDB administrative parameter value to set.\n        type: str\n        required: true\n    param_type:\n        description:\n            - Define the type of parameter value.\n        default: str\n        type: str\n        choices: [int, str]\n\nnotes:\n    - Requires the pymongo Python package on the remote host, version 2.4.2+.\n    - This can be installed using pip or the OS package manager.\n    - See also U(http://api.mongodb.org/python/current/installation.html)\nrequirements: [ "pymongo" ]\nauthor: "Loic Blot (@nerzhul)"\n'
EXAMPLES = '\n- name: Set MongoDB syncdelay to 60 (this is an int)\n  mongodb_parameter:\n    param: syncdelay\n    value: 60\n    param_type: int\n'
RETURN = '\nbefore:\n    description: value before modification\n    returned: success\n    type: str\nafter:\n    description: value after modification\n    returned: success\n    type: str\n'
import os
import traceback
try:
    from pymongo.errors import ConnectionFailure
    from pymongo.errors import OperationFailure
    from pymongo import version as PyMongoVersion
    from pymongo import MongoClient
except ImportError:
    try:
        from pymongo import Connection as MongoClient
    except ImportError:
        pymongo_found = False
    else:
        pymongo_found = True
else:
    pymongo_found = True
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.six.moves import configparser
from ansible.module_utils._text import to_native

def load_mongocnf():
    config = configparser.RawConfigParser()
    mongocnf = os.path.expanduser('~/.mongodb.cnf')
    try:
        config.readfp(open(mongocnf))
        creds = dict(user=config.get('client', 'user'), password=config.get('client', 'pass'))
    except (configparser.NoOptionError, IOError):
        return False
    return creds

def main():
    module = AnsibleModule(argument_spec=dict(login_user=dict(default=None), login_password=dict(default=None, no_log=True), login_host=dict(default='localhost'), login_port=dict(default=27017, type='int'), login_database=dict(default=None), replica_set=dict(default=None), param=dict(required=True), value=dict(required=True), param_type=dict(default='str', choices=['str', 'int']), ssl=dict(default=False, type='bool')))
    if not pymongo_found:
        module.fail_json(msg=missing_required_lib('pymongo'))
    login_user = module.params['login_user']
    login_password = module.params['login_password']
    login_host = module.params['login_host']
    login_port = module.params['login_port']
    login_database = module.params['login_database']
    replica_set = module.params['replica_set']
    ssl = module.params['ssl']
    param = module.params['param']
    param_type = module.params['param_type']
    value = module.params['value']
    try:
        if param_type == 'int':
            value = int(value)
    except ValueError:
        module.fail_json(msg="value '%s' is not %s" % (value, param_type))
    try:
        if replica_set:
            client = MongoClient(login_host, int(login_port), replicaset=replica_set, ssl=ssl)
        else:
            client = MongoClient(login_host, int(login_port), ssl=ssl)
        if login_user is None and login_password is None:
            mongocnf_creds = load_mongocnf()
            if mongocnf_creds is not False:
                login_user = mongocnf_creds['user']
                login_password = mongocnf_creds['password']
        elif login_password is None or login_user is None:
            module.fail_json(msg='when supplying login arguments, both login_user and login_password must be provided')
        if login_user is not None and login_password is not None:
            client.admin.authenticate(login_user, login_password, source=login_database)
    except ConnectionFailure as e:
        module.fail_json(msg='unable to connect to database: %s' % to_native(e), exception=traceback.format_exc())
    db = client.admin
    try:
        after_value = db.command('setParameter', **{param: value})
    except OperationFailure as e:
        module.fail_json(msg='unable to change parameter: %s' % to_native(e), exception=traceback.format_exc())
    if 'was' not in after_value:
        module.exit_json(changed=True, msg='Unable to determine old value, assume it changed.')
    else:
        module.exit_json(changed=value != after_value['was'], before=after_value['was'], after=value)
if __name__ == '__main__':
    main()