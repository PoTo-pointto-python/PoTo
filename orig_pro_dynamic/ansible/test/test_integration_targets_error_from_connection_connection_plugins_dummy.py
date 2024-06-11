from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\n    author:\n        - John Doe\n    connection: dummy\n    short_description: defective connection plugin\n    description:\n        - defective connection plugin\n    version_added: "2.0"\n    options: {}\n'
import ansible.constants as C
from ansible.errors import AnsibleError
from ansible.plugins.connection import ConnectionBase

class Connection(ConnectionBase):
    transport = 'dummy'
    has_pipelining = True

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)
        raise AnsibleError('an error with {{ some Jinja }}')

    def _connect(self):
        pass

    def exec_command(self, cmd, in_data=None, sudoable=True):
        pass

    def put_file(self, in_path, out_path):
        pass

    def fetch_file(self, in_path, out_path):
        pass

    def close(self):
        pass

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