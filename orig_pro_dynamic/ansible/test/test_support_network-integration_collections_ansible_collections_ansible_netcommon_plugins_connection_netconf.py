from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = 'author: Ansible Networking Team\nconnection: netconf\nshort_description: Provides a persistent connection using the netconf protocol\ndescription:\n- This connection plugin provides a connection to remote devices over the SSH NETCONF\n  subsystem.  This connection plugin is typically used by network devices for sending\n  and receiving RPC calls over NETCONF.\n- Note this connection plugin requires ncclient to be installed on the local Ansible\n  controller.\nrequirements:\n- ncclient\noptions:\n  host:\n    description:\n    - Specifies the remote device FQDN or IP address to establish the SSH connection\n      to.\n    default: inventory_hostname\n    vars:\n    - name: ansible_host\n  port:\n    type: int\n    description:\n    - Specifies the port on the remote device that listens for connections when establishing\n      the SSH connection.\n    default: 830\n    ini:\n    - section: defaults\n      key: remote_port\n    env:\n    - name: ANSIBLE_REMOTE_PORT\n    vars:\n    - name: ansible_port\n  network_os:\n    description:\n    - Configures the device platform network operating system.  This value is used\n      to load a device specific netconf plugin.  If this option is not configured\n      (or set to C(auto)), then Ansible will attempt to guess the correct network_os\n      to use. If it can not guess a network_os correctly it will use C(default).\n    vars:\n    - name: ansible_network_os\n  remote_user:\n    description:\n    - The username used to authenticate to the remote device when the SSH connection\n      is first established.  If the remote_user is not specified, the connection will\n      use the username of the logged in user.\n    - Can be configured from the CLI via the C(--user) or C(-u) options.\n    ini:\n    - section: defaults\n      key: remote_user\n    env:\n    - name: ANSIBLE_REMOTE_USER\n    vars:\n    - name: ansible_user\n  password:\n    description:\n    - Configures the user password used to authenticate to the remote device when\n      first establishing the SSH connection.\n    vars:\n    - name: ansible_password\n    - name: ansible_ssh_pass\n    - name: ansible_ssh_password\n    - name: ansible_netconf_password\n  private_key_file:\n    description:\n    - The private SSH key or certificate file used to authenticate to the remote device\n      when first establishing the SSH connection.\n    ini:\n    - section: defaults\n      key: private_key_file\n    env:\n    - name: ANSIBLE_PRIVATE_KEY_FILE\n    vars:\n    - name: ansible_private_key_file\n  look_for_keys:\n    default: true\n    description:\n    - Enables looking for ssh keys in the usual locations for ssh keys (e.g. :file:`~/.ssh/id_*`).\n    env:\n    - name: ANSIBLE_PARAMIKO_LOOK_FOR_KEYS\n    ini:\n    - section: paramiko_connection\n      key: look_for_keys\n    type: boolean\n  host_key_checking:\n    description: Set this to "False" if you want to avoid host key checking by the\n      underlying tools Ansible uses to connect to the host\n    type: boolean\n    default: true\n    env:\n    - name: ANSIBLE_HOST_KEY_CHECKING\n    - name: ANSIBLE_SSH_HOST_KEY_CHECKING\n    - name: ANSIBLE_NETCONF_HOST_KEY_CHECKING\n    ini:\n    - section: defaults\n      key: host_key_checking\n    - section: paramiko_connection\n      key: host_key_checking\n    vars:\n    - name: ansible_host_key_checking\n    - name: ansible_ssh_host_key_checking\n    - name: ansible_netconf_host_key_checking\n  persistent_connect_timeout:\n    type: int\n    description:\n    - Configures, in seconds, the amount of time to wait when trying to initially\n      establish a persistent connection.  If this value expires before the connection\n      to the remote device is completed, the connection will fail.\n    default: 30\n    ini:\n    - section: persistent_connection\n      key: connect_timeout\n    env:\n    - name: ANSIBLE_PERSISTENT_CONNECT_TIMEOUT\n    vars:\n    - name: ansible_connect_timeout\n  persistent_command_timeout:\n    type: int\n    description:\n    - Configures, in seconds, the amount of time to wait for a command to return from\n      the remote device.  If this timer is exceeded before the command returns, the\n      connection plugin will raise an exception and close.\n    default: 30\n    ini:\n    - section: persistent_connection\n      key: command_timeout\n    env:\n    - name: ANSIBLE_PERSISTENT_COMMAND_TIMEOUT\n    vars:\n    - name: ansible_command_timeout\n  netconf_ssh_config:\n    description:\n    - This variable is used to enable bastion/jump host with netconf connection. If\n      set to True the bastion/jump host ssh settings should be present in ~/.ssh/config\n      file, alternatively it can be set to custom ssh configuration file path to read\n      the bastion/jump host settings.\n    ini:\n    - section: netconf_connection\n      key: ssh_config\n      version_added: \'2.7\'\n    env:\n    - name: ANSIBLE_NETCONF_SSH_CONFIG\n    vars:\n    - name: ansible_netconf_ssh_config\n      version_added: \'2.7\'\n  persistent_log_messages:\n    type: boolean\n    description:\n    - This flag will enable logging the command executed and response received from\n      target device in the ansible log file. For this option to work \'log_path\' ansible\n      configuration option is required to be set to a file path with write access.\n    - Be sure to fully understand the security implications of enabling this option\n      as it could create a security vulnerability by logging sensitive information\n      in log file.\n    default: false\n    ini:\n    - section: persistent_connection\n      key: log_messages\n    env:\n    - name: ANSIBLE_PERSISTENT_LOG_MESSAGES\n    vars:\n    - name: ansible_persistent_log_messages\n'
import os
import logging
import json
from ansible.errors import AnsibleConnectionFailure, AnsibleError
from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.module_utils.basic import missing_required_lib
from ansible.module_utils.parsing.convert_bool import BOOLEANS_TRUE, BOOLEANS_FALSE
from ansible.plugins.loader import netconf_loader
from ansible.plugins.connection import NetworkConnectionBase, ensure_connect
try:
    from ncclient import manager
    from ncclient.operations import RPCError
    from ncclient.transport.errors import SSHUnknownHostError
    from ncclient.xml_ import to_ele, to_xml
    HAS_NCCLIENT = True
    NCCLIENT_IMP_ERR = None
except (ImportError, AttributeError) as err:
    HAS_NCCLIENT = False
    NCCLIENT_IMP_ERR = err
logging.getLogger('ncclient').setLevel(logging.INFO)

class Connection(NetworkConnectionBase):
    """NetConf connections"""
    transport = 'ansible.netcommon.netconf'
    has_pipelining = False

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)
        self._network_os = self._network_os or 'auto'
        self.netconf = netconf_loader.get(self._network_os, self)
        if self.netconf:
            self._sub_plugin = {'type': 'netconf', 'name': self.netconf._load_name, 'obj': self.netconf}
            self.queue_message('vvvv', 'loaded netconf plugin %s from path %s for network_os %s' % (self.netconf._load_name, self.netconf._original_path, self._network_os))
        else:
            self.netconf = netconf_loader.get('default', self)
            self._sub_plugin = {'type': 'netconf', 'name': 'default', 'obj': self.netconf}
            self.queue_message('display', 'unable to load netconf plugin for network_os %s, falling back to default plugin' % self._network_os)
        self.queue_message('log', 'network_os is set to %s' % self._network_os)
        self._manager = None
        self.key_filename = None
        self._ssh_config = None

    def exec_command(self, cmd, in_data=None, sudoable=True):
        """Sends the request to the node and returns the reply
        The method accepts two forms of request.  The first form is as a byte
        string that represents xml string be send over netconf session.
        The second form is a json-rpc (2.0) byte string.
        """
        if self._manager:
            request = to_ele(to_native(cmd, errors='surrogate_or_strict'))
            if request is None:
                return 'unable to parse request'
            try:
                reply = self._manager.rpc(request)
            except RPCError as exc:
                error = self.internal_error(data=to_text(to_xml(exc.xml), errors='surrogate_or_strict'))
                return json.dumps(error)
            return reply.data_xml
        else:
            return super(Connection, self).exec_command(cmd, in_data, sudoable)

    @property
    @ensure_connect
    def manager(self):
        return self._manager

    def _connect(self):
        if not HAS_NCCLIENT:
            raise AnsibleError('%s: %s' % (missing_required_lib('ncclient'), to_native(NCCLIENT_IMP_ERR)))
        self.queue_message('log', 'ssh connection done, starting ncclient')
        allow_agent = True
        if self._play_context.password is not None:
            allow_agent = False
        setattr(self._play_context, 'allow_agent', allow_agent)
        self.key_filename = self._play_context.private_key_file or self.get_option('private_key_file')
        if self.key_filename:
            self.key_filename = str(os.path.expanduser(self.key_filename))
        self._ssh_config = self.get_option('netconf_ssh_config')
        if self._ssh_config in BOOLEANS_TRUE:
            self._ssh_config = True
        elif self._ssh_config in BOOLEANS_FALSE:
            self._ssh_config = None
        if self._network_os == 'auto':
            for cls in netconf_loader.all(class_only=True):
                network_os = cls.guess_network_os(self)
                if network_os:
                    self.queue_message('vvv', 'discovered network_os %s' % network_os)
                    self._network_os = network_os
        if self._network_os == 'auto':
            self.queue_message('vvv', 'Unable to discover network_os. Falling back to default.')
            self._network_os = 'default'
        try:
            ncclient_device_handler = self.netconf.get_option('ncclient_device_handler')
        except KeyError:
            ncclient_device_handler = 'default'
        self.queue_message('vvv', 'identified ncclient device handler: %s.' % ncclient_device_handler)
        device_params = {'name': ncclient_device_handler}
        try:
            port = self._play_context.port or 830
            self.queue_message('vvv', 'ESTABLISH NETCONF SSH CONNECTION FOR USER: %s on PORT %s TO %s WITH SSH_CONFIG = %s' % (self._play_context.remote_user, port, self._play_context.remote_addr, self._ssh_config))
            self._manager = manager.connect(host=self._play_context.remote_addr, port=port, username=self._play_context.remote_user, password=self._play_context.password, key_filename=self.key_filename, hostkey_verify=self.get_option('host_key_checking'), look_for_keys=self.get_option('look_for_keys'), device_params=device_params, allow_agent=self._play_context.allow_agent, timeout=self.get_option('persistent_connect_timeout'), ssh_config=self._ssh_config)
            self._manager._timeout = self.get_option('persistent_command_timeout')
        except SSHUnknownHostError as exc:
            raise AnsibleConnectionFailure(to_native(exc))
        except ImportError:
            raise AnsibleError('connection=netconf is not supported on {0}'.format(self._network_os))
        if not self._manager.connected:
            return (1, b'', b'not connected')
        self.queue_message('log', 'ncclient manager object created successfully')
        self._connected = True
        super(Connection, self)._connect()
        return (0, to_bytes(self._manager.session_id, errors='surrogate_or_strict'), b'')

    def close(self):
        if self._manager:
            self._manager.close_session()
        super(Connection, self).close()

def test_Connection_exec_command():
    ret = Connection().exec_command()

def test_Connection_manager():
    ret = Connection().manager()

def test_Connection__connect():
    ret = Connection()._connect()

def test_Connection_close():
    ret = Connection().close()