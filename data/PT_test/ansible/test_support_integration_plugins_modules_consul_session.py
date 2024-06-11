from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\nmodule: consul_session\nshort_description: Manipulate consul sessions\ndescription:\n - Allows the addition, modification and deletion of sessions in a consul\n   cluster. These sessions can then be used in conjunction with key value pairs\n   to implement distributed locks. In depth documentation for working with\n   sessions can be found at http://www.consul.io/docs/internals/sessions.html\nrequirements:\n  - python-consul\n  - requests\nversion_added: "2.0"\nauthor:\n- Steve Gargan (@sgargan)\noptions:\n    id:\n        description:\n          - ID of the session, required when I(state) is either C(info) or\n            C(remove).\n        type: str\n    state:\n        description:\n          - Whether the session should be present i.e. created if it doesn\'t\n            exist, or absent, removed if present. If created, the I(id) for the\n            session is returned in the output. If C(absent), I(id) is\n            required to remove the session. Info for a single session, all the\n            sessions for a node or all available sessions can be retrieved by\n            specifying C(info), C(node) or C(list) for the I(state); for C(node)\n            or C(info), the node I(name) or session I(id) is required as parameter.\n        choices: [ absent, info, list, node, present ]\n        type: str\n        default: present\n    name:\n        description:\n          - The name that should be associated with the session. Required when\n            I(state=node) is used.\n        type: str\n    delay:\n        description:\n          - The optional lock delay that can be attached to the session when it\n            is created. Locks for invalidated sessions ar blocked from being\n            acquired until this delay has expired. Durations are in seconds.\n        type: int\n        default: 15\n    node:\n        description:\n          - The name of the node that with which the session will be associated.\n            by default this is the name of the agent.\n        type: str\n    datacenter:\n        description:\n          - The name of the datacenter in which the session exists or should be\n            created.\n        type: str\n    checks:\n        description:\n          - Checks that will be used to verify the session health. If\n            all the checks fail, the session will be invalidated and any locks\n            associated with the session will be release and can be acquired once\n            the associated lock delay has expired.\n        type: list\n    host:\n        description:\n          - The host of the consul agent defaults to localhost.\n        type: str\n        default: localhost\n    port:\n        description:\n          - The port on which the consul agent is running.\n        type: int\n        default: 8500\n    scheme:\n        description:\n          - The protocol scheme on which the consul agent is running.\n        type: str\n        default: http\n        version_added: "2.1"\n    validate_certs:\n        description:\n          - Whether to verify the TLS certificate of the consul agent.\n        type: bool\n        default: True\n        version_added: "2.1"\n    behavior:\n        description:\n          - The optional behavior that can be attached to the session when it\n            is created. This controls the behavior when a session is invalidated.\n        choices: [ delete, release ]\n        type: str\n        default: release\n        version_added: "2.2"\n'
EXAMPLES = '\n- name: register basic session with consul\n  consul_session:\n    name: session1\n\n- name: register a session with an existing check\n  consul_session:\n    name: session_with_check\n    checks:\n      - existing_check_name\n\n- name: register a session with lock_delay\n  consul_session:\n    name: session_with_delay\n    delay: 20s\n\n- name: retrieve info about session by id\n  consul_session:\n    id: session_id\n    state: info\n\n- name: retrieve active sessions\n  consul_session:\n    state: list\n'
try:
    import consul
    from requests.exceptions import ConnectionError
    python_consul_installed = True
except ImportError:
    python_consul_installed = False
from ansible.module_utils.basic import AnsibleModule

def execute(module):
    state = module.params.get('state')
    if state in ['info', 'list', 'node']:
        lookup_sessions(module)
    elif state == 'present':
        update_session(module)
    else:
        remove_session(module)

def lookup_sessions(module):
    datacenter = module.params.get('datacenter')
    state = module.params.get('state')
    consul_client = get_consul_api(module)
    try:
        if state == 'list':
            sessions_list = consul_client.session.list(dc=datacenter)
            if sessions_list and len(sessions_list) >= 2:
                sessions_list = sessions_list[1]
            module.exit_json(changed=True, sessions=sessions_list)
        elif state == 'node':
            node = module.params.get('node')
            sessions = consul_client.session.node(node, dc=datacenter)
            module.exit_json(changed=True, node=node, sessions=sessions)
        elif state == 'info':
            session_id = module.params.get('id')
            session_by_id = consul_client.session.info(session_id, dc=datacenter)
            module.exit_json(changed=True, session_id=session_id, sessions=session_by_id)
    except Exception as e:
        module.fail_json(msg='Could not retrieve session info %s' % e)

def update_session(module):
    name = module.params.get('name')
    delay = module.params.get('delay')
    checks = module.params.get('checks')
    datacenter = module.params.get('datacenter')
    node = module.params.get('node')
    behavior = module.params.get('behavior')
    consul_client = get_consul_api(module)
    try:
        session = consul_client.session.create(name=name, behavior=behavior, node=node, lock_delay=delay, dc=datacenter, checks=checks)
        module.exit_json(changed=True, session_id=session, name=name, behavior=behavior, delay=delay, checks=checks, node=node)
    except Exception as e:
        module.fail_json(msg='Could not create/update session %s' % e)

def remove_session(module):
    session_id = module.params.get('id')
    consul_client = get_consul_api(module)
    try:
        consul_client.session.destroy(session_id)
        module.exit_json(changed=True, session_id=session_id)
    except Exception as e:
        module.fail_json(msg="Could not remove session with id '%s' %s" % (session_id, e))

def get_consul_api(module):
    return consul.Consul(host=module.params.get('host'), port=module.params.get('port'), scheme=module.params.get('scheme'), verify=module.params.get('validate_certs'))

def test_dependencies(module):
    if not python_consul_installed:
        module.fail_json(msg='python-consul required for this module. see https://python-consul.readthedocs.io/en/latest/#installation')

def main():
    argument_spec = dict(checks=dict(type='list'), delay=dict(type='int', default='15'), behavior=dict(type='str', default='release', choices=['release', 'delete']), host=dict(type='str', default='localhost'), port=dict(type='int', default=8500), scheme=dict(type='str', default='http'), validate_certs=dict(type='bool', default=True), id=dict(type='str'), name=dict(type='str'), node=dict(type='str'), state=dict(type='str', default='present', choices=['absent', 'info', 'list', 'node', 'present']), datacenter=dict(type='str'))
    module = AnsibleModule(argument_spec=argument_spec, required_if=[('state', 'node', ['name']), ('state', 'info', ['id']), ('state', 'remove', ['id'])], supports_check_mode=False)
    test_dependencies(module)
    try:
        execute(module)
    except ConnectionError as e:
        module.fail_json(msg='Could not connect to consul agent at %s:%s, error was %s' % (module.params.get('host'), module.params.get('port'), e))
    except Exception as e:
        module.fail_json(msg=str(e))
if __name__ == '__main__':
    main()