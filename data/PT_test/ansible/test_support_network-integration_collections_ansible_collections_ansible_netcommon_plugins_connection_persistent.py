from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = 'author: Ansible Core Team\nconnection: persistent\nshort_description: Use a persistent unix socket for connection\ndescription:\n- This is a helper plugin to allow making other connections persistent.\noptions:\n  persistent_command_timeout:\n    type: int\n    description:\n    - Configures, in seconds, the amount of time to wait for a command to return from\n      the remote device.  If this timer is exceeded before the command returns, the\n      connection plugin will raise an exception and close\n    default: 10\n    ini:\n    - section: persistent_connection\n      key: command_timeout\n    env:\n    - name: ANSIBLE_PERSISTENT_COMMAND_TIMEOUT\n    vars:\n    - name: ansible_command_timeout\n'
from ansible.executor.task_executor import start_connection
from ansible.plugins.connection import ConnectionBase
from ansible.module_utils._text import to_text
from ansible.module_utils.connection import Connection as SocketConnection
from ansible.utils.display import Display
display = Display()

class Connection(ConnectionBase):
    """ Local based connections """
    transport = 'ansible.netcommon.persistent'
    has_pipelining = False

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)
        self._task_uuid = to_text(kwargs.get('task_uuid', ''))

    def _connect(self):
        self._connected = True
        return self

    def exec_command(self, cmd, in_data=None, sudoable=True):
        display.vvvv('exec_command(), socket_path=%s' % self.socket_path, host=self._play_context.remote_addr)
        connection = SocketConnection(self.socket_path)
        out = connection.exec_command(cmd, in_data=in_data, sudoable=sudoable)
        return (0, out, '')

    def put_file(self, in_path, out_path):
        pass

    def fetch_file(self, in_path, out_path):
        pass

    def close(self):
        self._connected = False

    def run(self):
        """Returns the path of the persistent connection socket.

        Attempts to ensure (within playcontext.timeout seconds) that the
        socket path exists. If the path exists (or the timeout has expired),
        returns the socket path.
        """
        display.vvvv('starting connection from persistent connection plugin', host=self._play_context.remote_addr)
        variables = {'ansible_command_timeout': self.get_option('persistent_command_timeout')}
        socket_path = start_connection(self._play_context, variables, self._task_uuid)
        display.vvvv('local domain socket path is %s' % socket_path, host=self._play_context.remote_addr)
        setattr(self, '_socket_path', socket_path)
        return socket_path

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

def test_Connection_run():
    ret = Connection().run()