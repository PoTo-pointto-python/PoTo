from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\nconnection: test_connection_override\nshort_description: test connection plugin used in tests\ndescription:\n- This is a test connection plugin used for shell testing\nauthor: ansible (@core)\nversion_added: historical\noptions:\n'
from ansible.plugins.connection import ConnectionBase

class Connection(ConnectionBase):
    """ test connection """
    transport = 'test_connection_override'

    def __init__(self, *args, **kwargs):
        self._shell_type = 'powershell'
        super(Connection, self).__init__(*args, **kwargs)

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