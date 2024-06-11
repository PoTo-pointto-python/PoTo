from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = "author: Ansible Networking Team\nconnection: httpapi\nshort_description: Use httpapi to run command on network appliances\ndescription:\n- This connection plugin provides a connection to remote devices over a HTTP(S)-based\n  api.\noptions:\n  host:\n    description:\n    - Specifies the remote device FQDN or IP address to establish the HTTP(S) connection\n      to.\n    default: inventory_hostname\n    vars:\n    - name: ansible_host\n  port:\n    type: int\n    description:\n    - Specifies the port on the remote device that listens for connections when establishing\n      the HTTP(S) connection.\n    - When unspecified, will pick 80 or 443 based on the value of use_ssl.\n    ini:\n    - section: defaults\n      key: remote_port\n    env:\n    - name: ANSIBLE_REMOTE_PORT\n    vars:\n    - name: ansible_httpapi_port\n  network_os:\n    description:\n    - Configures the device platform network operating system.  This value is used\n      to load the correct httpapi plugin to communicate with the remote device\n    vars:\n    - name: ansible_network_os\n  remote_user:\n    description:\n    - The username used to authenticate to the remote device when the API connection\n      is first established.  If the remote_user is not specified, the connection will\n      use the username of the logged in user.\n    - Can be configured from the CLI via the C(--user) or C(-u) options.\n    ini:\n    - section: defaults\n      key: remote_user\n    env:\n    - name: ANSIBLE_REMOTE_USER\n    vars:\n    - name: ansible_user\n  password:\n    description:\n    - Configures the user password used to authenticate to the remote device when\n      needed for the device API.\n    vars:\n    - name: ansible_password\n    - name: ansible_httpapi_pass\n    - name: ansible_httpapi_password\n  use_ssl:\n    type: boolean\n    description:\n    - Whether to connect using SSL (HTTPS) or not (HTTP).\n    default: false\n    vars:\n    - name: ansible_httpapi_use_ssl\n  validate_certs:\n    type: boolean\n    description:\n    - Whether to validate SSL certificates\n    default: true\n    vars:\n    - name: ansible_httpapi_validate_certs\n  use_proxy:\n    type: boolean\n    description:\n    - Whether to use https_proxy for requests.\n    default: true\n    vars:\n    - name: ansible_httpapi_use_proxy\n  become:\n    type: boolean\n    description:\n    - The become option will instruct the CLI session to attempt privilege escalation\n      on platforms that support it.  Normally this means transitioning from user mode\n      to C(enable) mode in the CLI session. If become is set to True and the remote\n      device does not support privilege escalation or the privilege has already been\n      elevated, then this option is silently ignored.\n    - Can be configured from the CLI via the C(--become) or C(-b) options.\n    default: false\n    ini:\n    - section: privilege_escalation\n      key: become\n    env:\n    - name: ANSIBLE_BECOME\n    vars:\n    - name: ansible_become\n  become_method:\n    description:\n    - This option allows the become method to be specified in for handling privilege\n      escalation.  Typically the become_method value is set to C(enable) but could\n      be defined as other values.\n    default: sudo\n    ini:\n    - section: privilege_escalation\n      key: become_method\n    env:\n    - name: ANSIBLE_BECOME_METHOD\n    vars:\n    - name: ansible_become_method\n  persistent_connect_timeout:\n    type: int\n    description:\n    - Configures, in seconds, the amount of time to wait when trying to initially\n      establish a persistent connection.  If this value expires before the connection\n      to the remote device is completed, the connection will fail.\n    default: 30\n    ini:\n    - section: persistent_connection\n      key: connect_timeout\n    env:\n    - name: ANSIBLE_PERSISTENT_CONNECT_TIMEOUT\n    vars:\n    - name: ansible_connect_timeout\n  persistent_command_timeout:\n    type: int\n    description:\n    - Configures, in seconds, the amount of time to wait for a command to return from\n      the remote device.  If this timer is exceeded before the command returns, the\n      connection plugin will raise an exception and close.\n    default: 30\n    ini:\n    - section: persistent_connection\n      key: command_timeout\n    env:\n    - name: ANSIBLE_PERSISTENT_COMMAND_TIMEOUT\n    vars:\n    - name: ansible_command_timeout\n  persistent_log_messages:\n    type: boolean\n    description:\n    - This flag will enable logging the command executed and response received from\n      target device in the ansible log file. For this option to work 'log_path' ansible\n      configuration option is required to be set to a file path with write access.\n    - Be sure to fully understand the security implications of enabling this option\n      as it could create a security vulnerability by logging sensitive information\n      in log file.\n    default: false\n    ini:\n    - section: persistent_connection\n      key: log_messages\n    env:\n    - name: ANSIBLE_PERSISTENT_LOG_MESSAGES\n    vars:\n    - name: ansible_persistent_log_messages\n"
from io import BytesIO
from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_bytes
from ansible.module_utils.six import PY3
from ansible.module_utils.six.moves import cPickle
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils.urls import open_url
from ansible.playbook.play_context import PlayContext
from ansible.plugins.loader import httpapi_loader
from ansible.plugins.connection import NetworkConnectionBase, ensure_connect

class Connection(NetworkConnectionBase):
    """Network API connection"""
    transport = 'ansible.netcommon.httpapi'
    has_pipelining = True

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)
        self._url = None
        self._auth = None
        if self._network_os:
            self.httpapi = httpapi_loader.get(self._network_os, self)
            if self.httpapi:
                self._sub_plugin = {'type': 'httpapi', 'name': self.httpapi._load_name, 'obj': self.httpapi}
                self.queue_message('vvvv', 'loaded API plugin %s from path %s for network_os %s' % (self.httpapi._load_name, self.httpapi._original_path, self._network_os))
            else:
                raise AnsibleConnectionFailure('unable to load API plugin for network_os %s' % self._network_os)
        else:
            raise AnsibleConnectionFailure('Unable to automatically determine host network os. Please manually configure ansible_network_os value for this host')
        self.queue_message('log', 'network_os is set to %s' % self._network_os)

    def update_play_context(self, pc_data):
        """Updates the play context information for the connection"""
        pc_data = to_bytes(pc_data)
        if PY3:
            pc_data = cPickle.loads(pc_data, encoding='bytes')
        else:
            pc_data = cPickle.loads(pc_data)
        play_context = PlayContext()
        play_context.deserialize(pc_data)
        self.queue_message('vvvv', 'updating play_context for connection')
        if self._play_context.become ^ play_context.become:
            self.set_become(play_context)
            if play_context.become is True:
                self.queue_message('vvvv', 'authorizing connection')
            else:
                self.queue_message('vvvv', 'deauthorizing connection')
        self._play_context = play_context

    def _connect(self):
        if not self.connected:
            protocol = 'https' if self.get_option('use_ssl') else 'http'
            host = self.get_option('host')
            port = self.get_option('port') or (443 if protocol == 'https' else 80)
            self._url = '%s://%s:%s' % (protocol, host, port)
            self.queue_message('vvv', 'ESTABLISH HTTP(S) CONNECTFOR USER: %s TO %s' % (self._play_context.remote_user, self._url))
            self.httpapi.set_become(self._play_context)
            self._connected = True
            self.httpapi.login(self.get_option('remote_user'), self.get_option('password'))

    def close(self):
        """
        Close the active session to the device
        """
        if self._connected:
            self.queue_message('vvvv', 'closing http(s) connection to device')
            self.logout()
        super(Connection, self).close()

    @ensure_connect
    def send(self, path, data, **kwargs):
        """
        Sends the command to the device over api
        """
        url_kwargs = dict(timeout=self.get_option('persistent_command_timeout'), validate_certs=self.get_option('validate_certs'), use_proxy=self.get_option('use_proxy'), headers={})
        url_kwargs.update(kwargs)
        if self._auth:
            headers = dict(kwargs.get('headers', {}))
            headers.update(self._auth)
            url_kwargs['headers'] = headers
        else:
            url_kwargs['force_basic_auth'] = True
            url_kwargs['url_username'] = self.get_option('remote_user')
            url_kwargs['url_password'] = self.get_option('password')
        try:
            url = self._url + path
            self._log_messages("send url '%s' with data '%s' and kwargs '%s'" % (url, data, url_kwargs))
            response = open_url(url, data=data, **url_kwargs)
        except HTTPError as exc:
            is_handled = self.handle_httperror(exc)
            if is_handled is True:
                return self.send(path, data, **kwargs)
            elif is_handled is False:
                raise
            else:
                response = is_handled
        except URLError as exc:
            raise AnsibleConnectionFailure('Could not connect to {0}: {1}'.format(self._url + path, exc.reason))
        response_buffer = BytesIO()
        resp_data = response.read()
        self._log_messages("received response: '%s'" % resp_data)
        response_buffer.write(resp_data)
        self._auth = self.update_auth(response, response_buffer) or self._auth
        response_buffer.seek(0)
        return (response, response_buffer)

def test_Connection_update_play_context():
    ret = Connection().update_play_context()

def test_Connection__connect():
    ret = Connection()._connect()

def test_Connection_close():
    ret = Connection().close()

def test_Connection_send():
    ret = Connection().send()