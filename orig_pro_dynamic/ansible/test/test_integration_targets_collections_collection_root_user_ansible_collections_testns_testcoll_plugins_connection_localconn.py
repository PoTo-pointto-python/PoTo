from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.module_utils._text import to_native
from ansible.plugins.connection import ConnectionBase
DOCUMENTATION = '\n    connection: localconn\n    short_description: do stuff local\n    description:\n        - does stuff\n    options:\n      connectionvar:\n        description:\n            - something we set\n        default: the_default\n        vars:\n            - name: ansible_localconn_connectionvar\n'

class Connection(ConnectionBase):
    transport = 'local'
    has_pipelining = True

    def _connect(self):
        return self

    def exec_command(self, cmd, in_data=None, sudoable=True):
        stdout = 'localconn ran {0}'.format(to_native(cmd))
        stderr = 'connectionvar is {0}'.format(to_native(self.get_option('connectionvar')))
        return (0, stdout, stderr)

    def put_file(self, in_path, out_path):
        raise NotImplementedError('just a test')

    def fetch_file(self, in_path, out_path):
        raise NotImplementedError('just a test')

    def close(self):
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