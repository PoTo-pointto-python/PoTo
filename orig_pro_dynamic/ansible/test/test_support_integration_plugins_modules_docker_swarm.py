from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: docker_swarm\nshort_description: Manage Swarm cluster\nversion_added: "2.7"\ndescription:\n  - Create a new Swarm cluster.\n  - Add/Remove nodes or managers to an existing cluster.\noptions:\n  advertise_addr:\n    description:\n      - Externally reachable address advertised to other nodes.\n      - This can either be an address/port combination\n          in the form C(192.168.1.1:4567), or an interface followed by a\n          port number, like C(eth0:4567).\n      - If the port number is omitted,\n          the port number from the listen address is used.\n      - If I(advertise_addr) is not specified, it will be automatically\n          detected when possible.\n      - Only used when swarm is initialised or joined. Because of this it\'s not\n        considered for idempotency checking.\n    type: str\n  default_addr_pool:\n    description:\n      - Default address pool in CIDR format.\n      - Only used when swarm is initialised. Because of this it\'s not considered\n        for idempotency checking.\n      - Requires API version >= 1.39.\n    type: list\n    elements: str\n    version_added: "2.8"\n  subnet_size:\n    description:\n      - Default address pool subnet mask length.\n      - Only used when swarm is initialised. Because of this it\'s not considered\n        for idempotency checking.\n      - Requires API version >= 1.39.\n    type: int\n    version_added: "2.8"\n  listen_addr:\n    description:\n      - Listen address used for inter-manager communication.\n      - This can either be an address/port combination in the form\n          C(192.168.1.1:4567), or an interface followed by a port number,\n          like C(eth0:4567).\n      - If the port number is omitted, the default swarm listening port\n          is used.\n      - Only used when swarm is initialised or joined. Because of this it\'s not\n        considered for idempotency checking.\n    type: str\n    default: 0.0.0.0:2377\n  force:\n    description:\n      - Use with state C(present) to force creating a new Swarm, even if already part of one.\n      - Use with state C(absent) to Leave the swarm even if this node is a manager.\n    type: bool\n    default: no\n  state:\n    description:\n      - Set to C(present), to create/update a new cluster.\n      - Set to C(join), to join an existing cluster.\n      - Set to C(absent), to leave an existing cluster.\n      - Set to C(remove), to remove an absent node from the cluster.\n        Note that removing requires Docker SDK for Python >= 2.4.0.\n      - Set to C(inspect) to display swarm informations.\n    type: str\n    default: present\n    choices:\n      - present\n      - join\n      - absent\n      - remove\n      - inspect\n  node_id:\n    description:\n      - Swarm id of the node to remove.\n      - Used with I(state=remove).\n    type: str\n  join_token:\n    description:\n      - Swarm token used to join a swarm cluster.\n      - Used with I(state=join).\n    type: str\n  remote_addrs:\n    description:\n      - Remote address of one or more manager nodes of an existing Swarm to connect to.\n      - Used with I(state=join).\n    type: list\n    elements: str\n  task_history_retention_limit:\n    description:\n      - Maximum number of tasks history stored.\n      - Docker default value is C(5).\n    type: int\n  snapshot_interval:\n    description:\n      - Number of logs entries between snapshot.\n      - Docker default value is C(10000).\n    type: int\n  keep_old_snapshots:\n    description:\n      - Number of snapshots to keep beyond the current snapshot.\n      - Docker default value is C(0).\n    type: int\n  log_entries_for_slow_followers:\n    description:\n      - Number of log entries to keep around to sync up slow followers after a snapshot is created.\n    type: int\n  heartbeat_tick:\n    description:\n      - Amount of ticks (in seconds) between each heartbeat.\n      - Docker default value is C(1s).\n    type: int\n  election_tick:\n    description:\n      - Amount of ticks (in seconds) needed without a leader to trigger a new election.\n      - Docker default value is C(10s).\n    type: int\n  dispatcher_heartbeat_period:\n    description:\n      - The delay for an agent to send a heartbeat to the dispatcher.\n      - Docker default value is C(5s).\n    type: int\n  node_cert_expiry:\n    description:\n      - Automatic expiry for nodes certificates.\n      - Docker default value is C(3months).\n    type: int\n  name:\n    description:\n      - The name of the swarm.\n    type: str\n  labels:\n    description:\n      - User-defined key/value metadata.\n      - Label operations in this module apply to the docker swarm cluster.\n        Use M(docker_node) module to add/modify/remove swarm node labels.\n      - Requires API version >= 1.32.\n    type: dict\n  signing_ca_cert:\n    description:\n      - The desired signing CA certificate for all swarm node TLS leaf certificates, in PEM format.\n      - This must not be a path to a certificate, but the contents of the certificate.\n      - Requires API version >= 1.30.\n    type: str\n  signing_ca_key:\n    description:\n      - The desired signing CA key for all swarm node TLS leaf certificates, in PEM format.\n      - This must not be a path to a key, but the contents of the key.\n      - Requires API version >= 1.30.\n    type: str\n  ca_force_rotate:\n    description:\n      - An integer whose purpose is to force swarm to generate a new signing CA certificate and key,\n          if none have been specified.\n      - Docker default value is C(0).\n      - Requires API version >= 1.30.\n    type: int\n  autolock_managers:\n    description:\n      - If set, generate a key and use it to lock data stored on the managers.\n      - Docker default value is C(no).\n      - M(docker_swarm_info) can be used to retrieve the unlock key.\n    type: bool\n  rotate_worker_token:\n    description: Rotate the worker join token.\n    type: bool\n    default: no\n  rotate_manager_token:\n    description: Rotate the manager join token.\n    type: bool\n    default: no\nextends_documentation_fragment:\n  - docker\n  - docker.docker_py_1_documentation\nrequirements:\n  - "L(Docker SDK for Python,https://docker-py.readthedocs.io/en/stable/) >= 1.10.0 (use L(docker-py,https://pypi.org/project/docker-py/) for Python 2.6)"\n  - Docker API >= 1.25\nauthor:\n  - Thierry Bouvet (@tbouvet)\n  - Piotr Wojciechowski (@WojciechowskiPiotr)\n'
EXAMPLES = "\n\n- name: Init a new swarm with default parameters\n  docker_swarm:\n    state: present\n\n- name: Update swarm configuration\n  docker_swarm:\n    state: present\n    election_tick: 5\n\n- name: Add nodes\n  docker_swarm:\n    state: join\n    advertise_addr: 192.168.1.2\n    join_token: SWMTKN-1--xxxxx\n    remote_addrs: [ '192.168.1.1:2377' ]\n\n- name: Leave swarm for a node\n  docker_swarm:\n    state: absent\n\n- name: Remove a swarm manager\n  docker_swarm:\n    state: absent\n    force: true\n\n- name: Remove node from swarm\n  docker_swarm:\n    state: remove\n    node_id: mynode\n\n- name: Inspect swarm\n  docker_swarm:\n    state: inspect\n  register: swarm_info\n"
RETURN = '\nswarm_facts:\n  description: Informations about swarm.\n  returned: success\n  type: dict\n  contains:\n      JoinTokens:\n          description: Tokens to connect to the Swarm.\n          returned: success\n          type: dict\n          contains:\n              Worker:\n                  description: Token to create a new *worker* node\n                  returned: success\n                  type: str\n                  example: SWMTKN-1--xxxxx\n              Manager:\n                  description: Token to create a new *manager* node\n                  returned: success\n                  type: str\n                  example: SWMTKN-1--xxxxx\n      UnlockKey:\n          description: The swarm unlock-key if I(autolock_managers) is C(true).\n          returned: on success if I(autolock_managers) is C(true)\n            and swarm is initialised, or if I(autolock_managers) has changed.\n          type: str\n          example: SWMKEY-1-xxx\n\nactions:\n  description: Provides the actions done on the swarm.\n  returned: when action failed.\n  type: list\n  elements: str\n  example: "[\'This cluster is already a swarm cluster\']"\n\n'
import json
import traceback
try:
    from docker.errors import DockerException, APIError
except ImportError:
    pass
from ansible.module_utils.docker.common import DockerBaseClass, DifferenceTracker, RequestException
from ansible.module_utils.docker.swarm import AnsibleDockerSwarmClient
from ansible.module_utils._text import to_native

class TaskParameters(DockerBaseClass):

    def __init__(self):
        super(TaskParameters, self).__init__()
        self.advertise_addr = None
        self.listen_addr = None
        self.remote_addrs = None
        self.join_token = None
        self.snapshot_interval = None
        self.task_history_retention_limit = None
        self.keep_old_snapshots = None
        self.log_entries_for_slow_followers = None
        self.heartbeat_tick = None
        self.election_tick = None
        self.dispatcher_heartbeat_period = None
        self.node_cert_expiry = None
        self.name = None
        self.labels = None
        self.log_driver = None
        self.signing_ca_cert = None
        self.signing_ca_key = None
        self.ca_force_rotate = None
        self.autolock_managers = None
        self.rotate_worker_token = None
        self.rotate_manager_token = None
        self.default_addr_pool = None
        self.subnet_size = None

    @staticmethod
    def from_ansible_params(client):
        result = TaskParameters()
        for (key, value) in client.module.params.items():
            if key in result.__dict__:
                setattr(result, key, value)
        result.update_parameters(client)
        return result

    def update_from_swarm_info(self, swarm_info):
        spec = swarm_info['Spec']
        ca_config = spec.get('CAConfig') or dict()
        if self.node_cert_expiry is None:
            self.node_cert_expiry = ca_config.get('NodeCertExpiry')
        if self.ca_force_rotate is None:
            self.ca_force_rotate = ca_config.get('ForceRotate')
        dispatcher = spec.get('Dispatcher') or dict()
        if self.dispatcher_heartbeat_period is None:
            self.dispatcher_heartbeat_period = dispatcher.get('HeartbeatPeriod')
        raft = spec.get('Raft') or dict()
        if self.snapshot_interval is None:
            self.snapshot_interval = raft.get('SnapshotInterval')
        if self.keep_old_snapshots is None:
            self.keep_old_snapshots = raft.get('KeepOldSnapshots')
        if self.heartbeat_tick is None:
            self.heartbeat_tick = raft.get('HeartbeatTick')
        if self.log_entries_for_slow_followers is None:
            self.log_entries_for_slow_followers = raft.get('LogEntriesForSlowFollowers')
        if self.election_tick is None:
            self.election_tick = raft.get('ElectionTick')
        orchestration = spec.get('Orchestration') or dict()
        if self.task_history_retention_limit is None:
            self.task_history_retention_limit = orchestration.get('TaskHistoryRetentionLimit')
        encryption_config = spec.get('EncryptionConfig') or dict()
        if self.autolock_managers is None:
            self.autolock_managers = encryption_config.get('AutoLockManagers')
        if self.name is None:
            self.name = spec['Name']
        if self.labels is None:
            self.labels = spec.get('Labels') or {}
        if 'LogDriver' in spec['TaskDefaults']:
            self.log_driver = spec['TaskDefaults']['LogDriver']

    def update_parameters(self, client):
        assign = dict(snapshot_interval='snapshot_interval', task_history_retention_limit='task_history_retention_limit', keep_old_snapshots='keep_old_snapshots', log_entries_for_slow_followers='log_entries_for_slow_followers', heartbeat_tick='heartbeat_tick', election_tick='election_tick', dispatcher_heartbeat_period='dispatcher_heartbeat_period', node_cert_expiry='node_cert_expiry', name='name', labels='labels', signing_ca_cert='signing_ca_cert', signing_ca_key='signing_ca_key', ca_force_rotate='ca_force_rotate', autolock_managers='autolock_managers', log_driver='log_driver')
        params = dict()
        for (dest, source) in assign.items():
            if not client.option_minimal_versions[source]['supported']:
                continue
            value = getattr(self, source)
            if value is not None:
                params[dest] = value
        self.spec = client.create_swarm_spec(**params)

    def compare_to_active(self, other, client, differences):
        for k in self.__dict__:
            if k in ('advertise_addr', 'listen_addr', 'remote_addrs', 'join_token', 'rotate_worker_token', 'rotate_manager_token', 'spec', 'default_addr_pool', 'subnet_size'):
                continue
            if not client.option_minimal_versions[k]['supported']:
                continue
            value = getattr(self, k)
            if value is None:
                continue
            other_value = getattr(other, k)
            if value != other_value:
                differences.add(k, parameter=value, active=other_value)
        if self.rotate_worker_token:
            differences.add('rotate_worker_token', parameter=True, active=False)
        if self.rotate_manager_token:
            differences.add('rotate_manager_token', parameter=True, active=False)
        return differences

class SwarmManager(DockerBaseClass):

    def __init__(self, client, results):
        super(SwarmManager, self).__init__()
        self.client = client
        self.results = results
        self.check_mode = self.client.check_mode
        self.swarm_info = {}
        self.state = client.module.params['state']
        self.force = client.module.params['force']
        self.node_id = client.module.params['node_id']
        self.differences = DifferenceTracker()
        self.parameters = TaskParameters.from_ansible_params(client)
        self.created = False

    def __call__(self):
        choice_map = {'present': self.init_swarm, 'join': self.join, 'absent': self.leave, 'remove': self.remove, 'inspect': self.inspect_swarm}
        if self.state == 'inspect':
            self.client.module.deprecate("The 'inspect' state is deprecated, please use 'docker_swarm_info' to inspect swarm cluster", version='2.12', collection_name='ansible.builtin')
        choice_map.get(self.state)()
        if self.client.module._diff or self.parameters.debug:
            diff = dict()
            (diff['before'], diff['after']) = self.differences.get_before_after()
            self.results['diff'] = diff

    def inspect_swarm(self):
        try:
            data = self.client.inspect_swarm()
            json_str = json.dumps(data, ensure_ascii=False)
            self.swarm_info = json.loads(json_str)
            self.results['changed'] = False
            self.results['swarm_facts'] = self.swarm_info
            unlock_key = self.get_unlock_key()
            self.swarm_info.update(unlock_key)
        except APIError:
            return

    def get_unlock_key(self):
        default = {'UnlockKey': None}
        if not self.has_swarm_lock_changed():
            return default
        try:
            return self.client.get_unlock_key() or default
        except APIError:
            return default

    def has_swarm_lock_changed(self):
        return self.parameters.autolock_managers and (self.created or self.differences.has_difference_for('autolock_managers'))

    def init_swarm(self):
        if not self.force and self.client.check_if_swarm_manager():
            self.__update_swarm()
            return
        if not self.check_mode:
            init_arguments = {'advertise_addr': self.parameters.advertise_addr, 'listen_addr': self.parameters.listen_addr, 'force_new_cluster': self.force, 'swarm_spec': self.parameters.spec}
            if self.parameters.default_addr_pool is not None:
                init_arguments['default_addr_pool'] = self.parameters.default_addr_pool
            if self.parameters.subnet_size is not None:
                init_arguments['subnet_size'] = self.parameters.subnet_size
            try:
                self.client.init_swarm(**init_arguments)
            except APIError as exc:
                self.client.fail('Can not create a new Swarm Cluster: %s' % to_native(exc))
        if not self.client.check_if_swarm_manager():
            if not self.check_mode:
                self.client.fail('Swarm not created or other error!')
        self.created = True
        self.inspect_swarm()
        self.results['actions'].append('New Swarm cluster created: %s' % self.swarm_info.get('ID'))
        self.differences.add('state', parameter='present', active='absent')
        self.results['changed'] = True
        self.results['swarm_facts'] = {'JoinTokens': self.swarm_info.get('JoinTokens'), 'UnlockKey': self.swarm_info.get('UnlockKey')}

    def __update_swarm(self):
        try:
            self.inspect_swarm()
            version = self.swarm_info['Version']['Index']
            self.parameters.update_from_swarm_info(self.swarm_info)
            old_parameters = TaskParameters()
            old_parameters.update_from_swarm_info(self.swarm_info)
            self.parameters.compare_to_active(old_parameters, self.client, self.differences)
            if self.differences.empty:
                self.results['actions'].append('No modification')
                self.results['changed'] = False
                return
            update_parameters = TaskParameters.from_ansible_params(self.client)
            update_parameters.update_parameters(self.client)
            if not self.check_mode:
                self.client.update_swarm(version=version, swarm_spec=update_parameters.spec, rotate_worker_token=self.parameters.rotate_worker_token, rotate_manager_token=self.parameters.rotate_manager_token)
        except APIError as exc:
            self.client.fail('Can not update a Swarm Cluster: %s' % to_native(exc))
            return
        self.inspect_swarm()
        self.results['actions'].append('Swarm cluster updated')
        self.results['changed'] = True

    def join(self):
        if self.client.check_if_swarm_node():
            self.results['actions'].append('This node is already part of a swarm.')
            return
        if not self.check_mode:
            try:
                self.client.join_swarm(remote_addrs=self.parameters.remote_addrs, join_token=self.parameters.join_token, listen_addr=self.parameters.listen_addr, advertise_addr=self.parameters.advertise_addr)
            except APIError as exc:
                self.client.fail('Can not join the Swarm Cluster: %s' % to_native(exc))
        self.results['actions'].append('New node is added to swarm cluster')
        self.differences.add('joined', parameter=True, active=False)
        self.results['changed'] = True

    def leave(self):
        if not self.client.check_if_swarm_node():
            self.results['actions'].append('This node is not part of a swarm.')
            return
        if not self.check_mode:
            try:
                self.client.leave_swarm(force=self.force)
            except APIError as exc:
                self.client.fail('This node can not leave the Swarm Cluster: %s' % to_native(exc))
        self.results['actions'].append('Node has left the swarm cluster')
        self.differences.add('joined', parameter='absent', active='present')
        self.results['changed'] = True

    def remove(self):
        if not self.client.check_if_swarm_manager():
            self.client.fail('This node is not a manager.')
        try:
            status_down = self.client.check_if_swarm_node_is_down(node_id=self.node_id, repeat_check=5)
        except APIError:
            return
        if not status_down:
            self.client.fail('Can not remove the node. The status node is ready and not down.')
        if not self.check_mode:
            try:
                self.client.remove_node(node_id=self.node_id, force=self.force)
            except APIError as exc:
                self.client.fail('Can not remove the node from the Swarm Cluster: %s' % to_native(exc))
        self.results['actions'].append('Node is removed from swarm cluster.')
        self.differences.add('joined', parameter=False, active=True)
        self.results['changed'] = True

def _detect_remove_operation(client):
    return client.module.params['state'] == 'remove'

def main():
    argument_spec = dict(advertise_addr=dict(type='str'), state=dict(type='str', default='present', choices=['present', 'join', 'absent', 'remove', 'inspect']), force=dict(type='bool', default=False), listen_addr=dict(type='str', default='0.0.0.0:2377'), remote_addrs=dict(type='list', elements='str'), join_token=dict(type='str'), snapshot_interval=dict(type='int'), task_history_retention_limit=dict(type='int'), keep_old_snapshots=dict(type='int'), log_entries_for_slow_followers=dict(type='int'), heartbeat_tick=dict(type='int'), election_tick=dict(type='int'), dispatcher_heartbeat_period=dict(type='int'), node_cert_expiry=dict(type='int'), name=dict(type='str'), labels=dict(type='dict'), signing_ca_cert=dict(type='str'), signing_ca_key=dict(type='str'), ca_force_rotate=dict(type='int'), autolock_managers=dict(type='bool'), node_id=dict(type='str'), rotate_worker_token=dict(type='bool', default=False), rotate_manager_token=dict(type='bool', default=False), default_addr_pool=dict(type='list', elements='str'), subnet_size=dict(type='int'))
    required_if = [('state', 'join', ['advertise_addr', 'remote_addrs', 'join_token']), ('state', 'remove', ['node_id'])]
    option_minimal_versions = dict(labels=dict(docker_py_version='2.6.0', docker_api_version='1.32'), signing_ca_cert=dict(docker_py_version='2.6.0', docker_api_version='1.30'), signing_ca_key=dict(docker_py_version='2.6.0', docker_api_version='1.30'), ca_force_rotate=dict(docker_py_version='2.6.0', docker_api_version='1.30'), autolock_managers=dict(docker_py_version='2.6.0'), log_driver=dict(docker_py_version='2.6.0'), remove_operation=dict(docker_py_version='2.4.0', detect_usage=_detect_remove_operation, usage_msg='remove swarm nodes'), default_addr_pool=dict(docker_py_version='4.0.0', docker_api_version='1.39'), subnet_size=dict(docker_py_version='4.0.0', docker_api_version='1.39'))
    client = AnsibleDockerSwarmClient(argument_spec=argument_spec, supports_check_mode=True, required_if=required_if, min_docker_version='1.10.0', min_docker_api_version='1.25', option_minimal_versions=option_minimal_versions)
    try:
        results = dict(changed=False, result='', actions=[])
        SwarmManager(client, results)()
        client.module.exit_json(**results)
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())
    except RequestException as e:
        client.fail('An unexpected requests error occurred when docker-py tried to talk to the docker daemon: {0}'.format(e), exception=traceback.format_exc())
if __name__ == '__main__':
    main()

def test_TaskParameters_from_ansible_params():
    ret = TaskParameters().from_ansible_params()

def test_TaskParameters_update_from_swarm_info():
    ret = TaskParameters().update_from_swarm_info()

def test_TaskParameters_update_parameters():
    ret = TaskParameters().update_parameters()

def test_TaskParameters_compare_to_active():
    ret = TaskParameters().compare_to_active()

def test_SwarmManager___call__():
    ret = SwarmManager().__call__()

def test_SwarmManager_inspect_swarm():
    ret = SwarmManager().inspect_swarm()

def test_SwarmManager_get_unlock_key():
    ret = SwarmManager().get_unlock_key()

def test_SwarmManager_has_swarm_lock_changed():
    ret = SwarmManager().has_swarm_lock_changed()

def test_SwarmManager_init_swarm():
    ret = SwarmManager().init_swarm()

def test_SwarmManager___update_swarm():
    ret = SwarmManager().__update_swarm()

def test_SwarmManager_join():
    ret = SwarmManager().join()

def test_SwarmManager_leave():
    ret = SwarmManager().leave()

def test_SwarmManager_remove():
    ret = SwarmManager().remove()