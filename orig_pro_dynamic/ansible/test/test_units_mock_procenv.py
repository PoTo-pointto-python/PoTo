from __future__ import absolute_import, division, print_function
__metaclass__ = type
import sys
import json
from contextlib import contextmanager
from io import BytesIO, StringIO
from units.compat import unittest
from ansible.module_utils.six import PY3
from ansible.module_utils._text import to_bytes

@contextmanager
def swap_stdin_and_argv(stdin_data='', argv_data=tuple()):
    """
    context manager that temporarily masks the test runner's values for stdin and argv
    """
    real_stdin = sys.stdin
    real_argv = sys.argv
    if PY3:
        fake_stream = StringIO(stdin_data)
        fake_stream.buffer = BytesIO(to_bytes(stdin_data))
    else:
        fake_stream = BytesIO(to_bytes(stdin_data))
    try:
        sys.stdin = fake_stream
        sys.argv = argv_data
        yield
    finally:
        sys.stdin = real_stdin
        sys.argv = real_argv

@contextmanager
def swap_stdout():
    """
    context manager that temporarily replaces stdout for tests that need to verify output
    """
    old_stdout = sys.stdout
    if PY3:
        fake_stream = StringIO()
    else:
        fake_stream = BytesIO()
    try:
        sys.stdout = fake_stream
        yield fake_stream
    finally:
        sys.stdout = old_stdout

class ModuleTestCase(unittest.TestCase):

    def setUp(self, module_args=None):
        if module_args is None:
            module_args = {'_ansible_remote_tmp': '/tmp', '_ansible_keep_remote_files': False}
        args = json.dumps(dict(ANSIBLE_MODULE_ARGS=module_args))
        self.stdin_swap = swap_stdin_and_argv(stdin_data=args)
        self.stdin_swap.__enter__()

    def tearDown(self):
        self.stdin_swap.__exit__(None, None, None)

def test_ModuleTestCase_setUp():
    ret = ModuleTestCase().setUp()

def test_ModuleTestCase_tearDown():
    ret = ModuleTestCase().tearDown()