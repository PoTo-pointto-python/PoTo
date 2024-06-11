from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\n    connection: fakelocal\n    short_description: dont execute anything\n    description:\n        - This connection plugin just verifies parameters passed in\n    author: ansible (@core)\n    version_added: histerical\n    options:\n      password:\n          description: Authentication password for the C(remote_user). Can be supplied as CLI option.\n          vars:\n              - name: ansible_password\n      remote_user:\n          description:\n              - User name with which to login to the remote server, normally set by the remote_user keyword.\n          ini:\n            - section: defaults\n              key: remote_user\n          vars:\n              - name: ansible_user\n'
from ansible.errors import AnsibleConnectionFailure
from ansible.plugins.connection import ConnectionBase
from ansible.utils.display import Display
display = Display()

class Connection(ConnectionBase):
    """ Local based connections """
    transport = 'fakelocal'
    has_pipelining = True

    def __init__(self, *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)
        self.cwd = None

    def _connect(self):
        """ verify """
        if self.get_option('remote_user') == 'invaliduser' and self.get_option('password') == 'badpassword':
            raise AnsibleConnectionFailure('Got invaliduser and badpassword')
        if not self._connected:
            display.vvv(u'ESTABLISH FAKELOCAL CONNECTION FOR USER: {0}'.format(self._play_context.remote_user), host=self._play_context.remote_addr)
            self._connected = True
        return self

    def exec_command(self, cmd, in_data=None, sudoable=True):
        """ run a command on the local host """
        super(Connection, self).exec_command(cmd, in_data=in_data, sudoable=sudoable)
        return (0, '{"msg": "ALL IS GOOD"}', '')

    def put_file(self, in_path, out_path):
        """ transfer a file from local to local """
        super(Connection, self).put_file(in_path, out_path)

    def fetch_file(self, in_path, out_path):
        """ fetch a file from local to local -- for compatibility """
        super(Connection, self).fetch_file(in_path, out_path)

    def close(self):
        """ terminate the connection; nothing to do here """
        self._connected = False

def test_Connection__connect():
    ret = Connection()._connect()

def test_Connection_exec_command():
    ret = Connection().exec_command()

def test_Connection_put_file():
    ret = Connection().put_file()

def test_Connection_fetch_file():
    ret = Connection().fetch_file()

def test_Connection_close():
    ret = Connection().close()