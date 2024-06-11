from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: hcloud_server\n\nshort_description: Create and manage cloud servers on the Hetzner Cloud.\n\nversion_added: "2.8"\n\ndescription:\n    - Create, update and manage cloud servers on the Hetzner Cloud.\n\nauthor:\n    - Lukas Kaemmerling (@LKaemmerling)\n\noptions:\n    id:\n        description:\n            - The ID of the Hetzner Cloud server to manage.\n            - Only required if no server I(name) is given\n        type: int\n    name:\n        description:\n            - The Name of the Hetzner Cloud server to manage.\n            - Only required if no server I(id) is given or a server does not exists.\n        type: str\n    server_type:\n        description:\n            - The Server Type of the Hetzner Cloud server to manage.\n            - Required if server does not exists.\n        type: str\n    ssh_keys:\n        description:\n            - List of SSH key names\n            - The key names correspond to the SSH keys configured for your\n              Hetzner Cloud account access.\n        type: list\n    volumes:\n        description:\n            - List of Volumes IDs that should be attached to the server on server creation.\n        type: list\n    image:\n        description:\n            - Image the server should be created from.\n            - Required if server does not exists.\n        type: str\n    location:\n        description:\n            - Location of Server.\n            - Required if no I(datacenter) is given and server does not exists.\n        type: str\n    datacenter:\n        description:\n            - Datacenter of Server.\n            - Required of no I(location) is given and server does not exists.\n        type: str\n    backups:\n        description:\n            - Enable or disable Backups for the given Server.\n        type: bool\n        default: no\n    upgrade_disk:\n        description:\n            - Resize the disk size, when resizing a server.\n            - If you want to downgrade the server later, this value should be False.\n        type: bool\n        default: no\n    force_upgrade:\n        description:\n            - Force the upgrade of the server.\n            - Power off the server if it is running on upgrade.\n        type: bool\n        default: no\n    user_data:\n        description:\n            - User Data to be passed to the server on creation.\n            - Only used if server does not exists.\n        type: str\n    rescue_mode:\n        description:\n            - Add the Hetzner rescue system type you want the server to be booted into.\n        type: str\n        version_added: 2.9\n    labels:\n        description:\n            - User-defined labels (key-value pairs).\n        type: dict\n    delete_protection:\n        description:\n            - Protect the Server for deletion.\n            - Needs to be the same as I(rebuild_protection).\n        type: bool\n        version_added: "2.10"\n    rebuild_protection:\n        description:\n            - Protect the Server for rebuild.\n            - Needs to be the same as I(delete_protection).\n        type: bool\n        version_added: "2.10"\n    state:\n        description:\n            - State of the server.\n        default: present\n        choices: [ absent, present, restarted, started, stopped, rebuild ]\n        type: str\nextends_documentation_fragment: hcloud\n'
EXAMPLES = '\n- name: Create a basic server\n  hcloud_server:\n    name: my-server\n    server_type: cx11\n    image: ubuntu-18.04\n    state: present\n\n- name: Create a basic server with ssh key\n  hcloud_server:\n    name: my-server\n    server_type: cx11\n    image: ubuntu-18.04\n    location: fsn1\n    ssh_keys:\n      - me@myorganisation\n    state: present\n\n- name: Resize an existing server\n  hcloud_server:\n    name: my-server\n    server_type: cx21\n    upgrade_disk: yes\n    state: present\n\n- name: Ensure the server is absent (remove if needed)\n  hcloud_server:\n    name: my-server\n    state: absent\n\n- name: Ensure the server is started\n  hcloud_server:\n    name: my-server\n    state: started\n\n- name: Ensure the server is stopped\n  hcloud_server:\n    name: my-server\n    state: stopped\n\n- name: Ensure the server is restarted\n  hcloud_server:\n    name: my-server\n    state: restarted\n\n- name: Ensure the server is will be booted in rescue mode and therefore restarted\n  hcloud_server:\n    name: my-server\n    rescue_mode: linux64\n    state: restarted\n\n- name: Ensure the server is rebuild\n  hcloud_server:\n    name: my-server\n    image: ubuntu-18.04\n    state: rebuild\n'
RETURN = '\nhcloud_server:\n    description: The server instance\n    returned: Always\n    type: complex\n    contains:\n        id:\n            description: Numeric identifier of the server\n            returned: always\n            type: int\n            sample: 1937415\n        name:\n            description: Name of the server\n            returned: always\n            type: str\n            sample: my-server\n        status:\n            description: Status of the server\n            returned: always\n            type: str\n            sample: running\n        server_type:\n            description: Name of the server type of the server\n            returned: always\n            type: str\n            sample: cx11\n        ipv4_address:\n            description: Public IPv4 address of the server\n            returned: always\n            type: str\n            sample: 116.203.104.109\n        ipv6:\n            description: IPv6 network of the server\n            returned: always\n            type: str\n            sample: 2a01:4f8:1c1c:c140::/64\n        location:\n            description: Name of the location of the server\n            returned: always\n            type: str\n            sample: fsn1\n        datacenter:\n            description: Name of the datacenter of the server\n            returned: always\n            type: str\n            sample: fsn1-dc14\n        rescue_enabled:\n            description: True if rescue mode is enabled, Server will then boot into rescue system on next reboot\n            returned: always\n            type: bool\n            sample: false\n        backup_window:\n            description: Time window (UTC) in which the backup will run, or null if the backups are not enabled\n            returned: always\n            type: bool\n            sample: 22-02\n        labels:\n            description: User-defined labels (key-value pairs)\n            returned: always\n            type: dict\n        delete_protection:\n            description: True if server is protected for deletion\n            type: bool\n            returned: always\n            sample: false\n            version_added: "2.10"\n        rebuild_protection:\n            description: True if server is protected for rebuild\n            type: bool\n            returned: always\n            sample: false\n            version_added: "2.10"\n'
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible.module_utils.hcloud import Hcloud
try:
    from hcloud.volumes.domain import Volume
    from hcloud.ssh_keys.domain import SSHKey
    from hcloud.servers.domain import Server
    from hcloud import APIException
except ImportError:
    pass

class AnsibleHcloudServer(Hcloud):

    def __init__(self, module):
        Hcloud.__init__(self, module, 'hcloud_server')
        self.hcloud_server = None

    def _prepare_result(self):
        image = None if self.hcloud_server.image is None else to_native(self.hcloud_server.image.name)
        return {'id': to_native(self.hcloud_server.id), 'name': to_native(self.hcloud_server.name), 'ipv4_address': to_native(self.hcloud_server.public_net.ipv4.ip), 'ipv6': to_native(self.hcloud_server.public_net.ipv6.ip), 'image': image, 'server_type': to_native(self.hcloud_server.server_type.name), 'datacenter': to_native(self.hcloud_server.datacenter.name), 'location': to_native(self.hcloud_server.datacenter.location.name), 'rescue_enabled': self.hcloud_server.rescue_enabled, 'backup_window': to_native(self.hcloud_server.backup_window), 'labels': self.hcloud_server.labels, 'delete_protection': self.hcloud_server.protection['delete'], 'rebuild_protection': self.hcloud_server.protection['rebuild'], 'status': to_native(self.hcloud_server.status)}

    def _get_server(self):
        try:
            if self.module.params.get('id') is not None:
                self.hcloud_server = self.client.servers.get_by_id(self.module.params.get('id'))
            else:
                self.hcloud_server = self.client.servers.get_by_name(self.module.params.get('name'))
        except APIException as e:
            self.module.fail_json(msg=e.message)

    def _create_server(self):
        self.module.fail_on_missing_params(required_params=['name', 'server_type', 'image'])
        params = {'name': self.module.params.get('name'), 'server_type': self.client.server_types.get_by_name(self.module.params.get('server_type')), 'user_data': self.module.params.get('user_data'), 'labels': self.module.params.get('labels')}
        if self.client.images.get_by_name(self.module.params.get('image')) is not None:
            params['image'] = self.client.images.get_by_name(self.module.params.get('image'))
        else:
            params['image'] = self.client.images.get_by_id(self.module.params.get('image'))
        if self.module.params.get('ssh_keys') is not None:
            params['ssh_keys'] = [SSHKey(name=ssh_key_name) for ssh_key_name in self.module.params.get('ssh_keys')]
        if self.module.params.get('volumes') is not None:
            params['volumes'] = [Volume(id=volume_id) for volume_id in self.module.params.get('volumes')]
        if self.module.params.get('location') is None and self.module.params.get('datacenter') is None:
            params['location'] = None
            params['datacenter'] = None
        elif self.module.params.get('location') is not None and self.module.params.get('datacenter') is None:
            params['location'] = self.client.locations.get_by_name(self.module.params.get('location'))
        elif self.module.params.get('location') is None and self.module.params.get('datacenter') is not None:
            params['datacenter'] = self.client.datacenters.get_by_name(self.module.params.get('datacenter'))
        if not self.module.check_mode:
            resp = self.client.servers.create(**params)
            self.result['root_password'] = resp.root_password
            resp.action.wait_until_finished(max_retries=1000)
            [action.wait_until_finished() for action in resp.next_actions]
            rescue_mode = self.module.params.get('rescue_mode')
            if rescue_mode:
                self._get_server()
                self._set_rescue_mode(rescue_mode)
        self._mark_as_changed()
        self._get_server()

    def _update_server(self):
        try:
            rescue_mode = self.module.params.get('rescue_mode')
            if rescue_mode and self.hcloud_server.rescue_enabled is False:
                if not self.module.check_mode:
                    self._set_rescue_mode(rescue_mode)
                self._mark_as_changed()
            elif not rescue_mode and self.hcloud_server.rescue_enabled is True:
                if not self.module.check_mode:
                    self.hcloud_server.disable_rescue().wait_until_finished()
                self._mark_as_changed()
            if self.module.params.get('backups') and self.hcloud_server.backup_window is None:
                if not self.module.check_mode:
                    self.hcloud_server.enable_backup().wait_until_finished()
                self._mark_as_changed()
            elif not self.module.params.get('backups') and self.hcloud_server.backup_window is not None:
                if not self.module.check_mode:
                    self.hcloud_server.disable_backup().wait_until_finished()
                self._mark_as_changed()
            labels = self.module.params.get('labels')
            if labels is not None and labels != self.hcloud_server.labels:
                if not self.module.check_mode:
                    self.hcloud_server.update(labels=labels)
                self._mark_as_changed()
            server_type = self.module.params.get('server_type')
            if server_type is not None and self.hcloud_server.server_type.name != server_type:
                previous_server_status = self.hcloud_server.status
                state = self.module.params.get('state')
                if previous_server_status == Server.STATUS_RUNNING:
                    if not self.module.check_mode:
                        if self.module.params.get('force_upgrade') or state == 'stopped':
                            self.stop_server()
                        else:
                            self.module.warn('You can not upgrade a running instance %s. You need to stop the instance or use force_upgrade=yes.' % self.hcloud_server.name)
                timeout = 100
                if self.module.params.get('upgrade_disk'):
                    timeout = 1000
                if not self.module.check_mode:
                    self.hcloud_server.change_type(server_type=self.client.server_types.get_by_name(server_type), upgrade_disk=self.module.params.get('upgrade_disk')).wait_until_finished(timeout)
                    if state == 'present' and previous_server_status == Server.STATUS_RUNNING or state == 'started':
                        self.start_server()
                self._mark_as_changed()
            delete_protection = self.module.params.get('delete_protection')
            rebuild_protection = self.module.params.get('rebuild_protection')
            if (delete_protection is not None and rebuild_protection is not None) and (delete_protection != self.hcloud_server.protection['delete'] or rebuild_protection != self.hcloud_server.protection['rebuild']):
                if not self.module.check_mode:
                    self.hcloud_server.change_protection(delete=delete_protection, rebuild=rebuild_protection).wait_until_finished()
                self._mark_as_changed()
            self._get_server()
        except APIException as e:
            self.module.fail_json(msg=e.message)

    def _set_rescue_mode(self, rescue_mode):
        if self.module.params.get('ssh_keys'):
            resp = self.hcloud_server.enable_rescue(type=rescue_mode, ssh_keys=[self.client.ssh_keys.get_by_name(ssh_key_name).id for ssh_key_name in self.module.params.get('ssh_keys')])
        else:
            resp = self.hcloud_server.enable_rescue(type=rescue_mode)
        resp.action.wait_until_finished()
        self.result['root_password'] = resp.root_password

    def start_server(self):
        try:
            if self.hcloud_server.status != Server.STATUS_RUNNING:
                if not self.module.check_mode:
                    self.client.servers.power_on(self.hcloud_server).wait_until_finished()
                self._mark_as_changed()
            self._get_server()
        except APIException as e:
            self.module.fail_json(msg=e.message)

    def stop_server(self):
        try:
            if self.hcloud_server.status != Server.STATUS_OFF:
                if not self.module.check_mode:
                    self.client.servers.power_off(self.hcloud_server).wait_until_finished()
                self._mark_as_changed()
            self._get_server()
        except APIException as e:
            self.module.fail_json(msg=e.message)

    def rebuild_server(self):
        self.module.fail_on_missing_params(required_params=['image'])
        try:
            if not self.module.check_mode:
                self.client.servers.rebuild(self.hcloud_server, self.client.images.get_by_name(self.module.params.get('image'))).wait_until_finished()
            self._mark_as_changed()
            self._get_server()
        except APIException as e:
            self.module.fail_json(msg=e.message)

    def present_server(self):
        self._get_server()
        if self.hcloud_server is None:
            self._create_server()
        else:
            self._update_server()

    def delete_server(self):
        try:
            self._get_server()
            if self.hcloud_server is not None:
                if not self.module.check_mode:
                    self.client.servers.delete(self.hcloud_server).wait_until_finished()
                self._mark_as_changed()
            self.hcloud_server = None
        except APIException as e:
            self.module.fail_json(msg=e.message)

    @staticmethod
    def define_module():
        return AnsibleModule(argument_spec=dict(id={'type': 'int'}, name={'type': 'str'}, image={'type': 'str'}, server_type={'type': 'str'}, location={'type': 'str'}, datacenter={'type': 'str'}, user_data={'type': 'str'}, ssh_keys={'type': 'list'}, volumes={'type': 'list'}, labels={'type': 'dict'}, backups={'type': 'bool', 'default': False}, upgrade_disk={'type': 'bool', 'default': False}, force_upgrade={'type': 'bool', 'default': False}, rescue_mode={'type': 'str'}, delete_protection={'type': 'bool'}, rebuild_protection={'type': 'bool'}, state={'choices': ['absent', 'present', 'restarted', 'started', 'stopped', 'rebuild'], 'default': 'present'}, **Hcloud.base_module_arguments()), required_one_of=[['id', 'name']], mutually_exclusive=[['location', 'datacenter']], required_together=[['delete_protection', 'rebuild_protection']], supports_check_mode=True)

def main():
    module = AnsibleHcloudServer.define_module()
    hcloud = AnsibleHcloudServer(module)
    state = module.params.get('state')
    if state == 'absent':
        hcloud.delete_server()
    elif state == 'present':
        hcloud.present_server()
    elif state == 'started':
        hcloud.present_server()
        hcloud.start_server()
    elif state == 'stopped':
        hcloud.present_server()
        hcloud.stop_server()
    elif state == 'restarted':
        hcloud.present_server()
        hcloud.stop_server()
        hcloud.start_server()
    elif state == 'rebuild':
        hcloud.present_server()
        hcloud.rebuild_server()
    module.exit_json(**hcloud.get_result())
if __name__ == '__main__':
    main()

def test_AnsibleHcloudServer__prepare_result():
    ret = AnsibleHcloudServer()._prepare_result()

def test_AnsibleHcloudServer__get_server():
    ret = AnsibleHcloudServer()._get_server()

def test_AnsibleHcloudServer__create_server():
    ret = AnsibleHcloudServer()._create_server()

def test_AnsibleHcloudServer__update_server():
    ret = AnsibleHcloudServer()._update_server()

def test_AnsibleHcloudServer__set_rescue_mode():
    ret = AnsibleHcloudServer()._set_rescue_mode()

def test_AnsibleHcloudServer_start_server():
    ret = AnsibleHcloudServer().start_server()

def test_AnsibleHcloudServer_stop_server():
    ret = AnsibleHcloudServer().stop_server()

def test_AnsibleHcloudServer_rebuild_server():
    ret = AnsibleHcloudServer().rebuild_server()

def test_AnsibleHcloudServer_present_server():
    ret = AnsibleHcloudServer().present_server()

def test_AnsibleHcloudServer_delete_server():
    ret = AnsibleHcloudServer().delete_server()

def test_AnsibleHcloudServer_define_module():
    ret = AnsibleHcloudServer().define_module()