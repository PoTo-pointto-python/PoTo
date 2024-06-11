from __future__ import absolute_import, division, print_function
__metaclass__ = type
import json
import os
import shutil
import tempfile
import pytest
from units.compat.mock import patch, MagicMock
from ansible.module_utils._text import to_bytes
from ansible.module_utils import basic

class TestAnsibleModuleSetCwd:

    def test_set_cwd(self, monkeypatch):
        """make sure /tmp is used"""

        def mock_getcwd():
            return '/tmp'

        def mock_access(path, perm):
            return True

        def mock_chdir(path):
            pass
        monkeypatch.setattr(os, 'getcwd', mock_getcwd)
        monkeypatch.setattr(os, 'access', mock_access)
        monkeypatch.setattr(basic, '_ANSIBLE_ARGS', to_bytes(json.dumps({'ANSIBLE_MODULE_ARGS': {}})))
        with patch('time.time', return_value=42):
            am = basic.AnsibleModule(argument_spec={})
        result = am._set_cwd()
        assert result == '/tmp'

    def test_set_cwd_unreadable_use_self_tmpdir(self, monkeypatch):
        """pwd is not readable, use instance's tmpdir property"""

        def mock_getcwd():
            return '/tmp'

        def mock_access(path, perm):
            if path == '/tmp' and perm == 4:
                return False
            return True

        def mock_expandvars(var):
            if var == '$HOME':
                return '/home/foobar'
            return var

        def mock_gettempdir():
            return '/tmp/testdir'

        def mock_chdir(path):
            if path == '/tmp':
                raise Exception()
            return
        monkeypatch.setattr(os, 'getcwd', mock_getcwd)
        monkeypatch.setattr(os, 'chdir', mock_chdir)
        monkeypatch.setattr(os, 'access', mock_access)
        monkeypatch.setattr(os.path, 'expandvars', mock_expandvars)
        monkeypatch.setattr(basic, '_ANSIBLE_ARGS', to_bytes(json.dumps({'ANSIBLE_MODULE_ARGS': {}})))
        with patch('time.time', return_value=42):
            am = basic.AnsibleModule(argument_spec={})
        am._tmpdir = '/tmp2'
        result = am._set_cwd()
        assert result == am._tmpdir

    def test_set_cwd_unreadable_use_home(self, monkeypatch):
        """cwd and instance tmpdir are unreadable, use home"""

        def mock_getcwd():
            return '/tmp'

        def mock_access(path, perm):
            if path in ['/tmp', '/tmp2'] and perm == 4:
                return False
            return True

        def mock_expandvars(var):
            if var == '$HOME':
                return '/home/foobar'
            return var

        def mock_gettempdir():
            return '/tmp/testdir'

        def mock_chdir(path):
            if path == '/tmp':
                raise Exception()
            return
        monkeypatch.setattr(os, 'getcwd', mock_getcwd)
        monkeypatch.setattr(os, 'chdir', mock_chdir)
        monkeypatch.setattr(os, 'access', mock_access)
        monkeypatch.setattr(os.path, 'expandvars', mock_expandvars)
        monkeypatch.setattr(basic, '_ANSIBLE_ARGS', to_bytes(json.dumps({'ANSIBLE_MODULE_ARGS': {}})))
        with patch('time.time', return_value=42):
            am = basic.AnsibleModule(argument_spec={})
        am._tmpdir = '/tmp2'
        result = am._set_cwd()
        assert result == '/home/foobar'

    def test_set_cwd_unreadable_use_gettempdir(self, monkeypatch):
        """fallback to tempfile.gettempdir"""
        thisdir = None

        def mock_getcwd():
            return '/tmp'

        def mock_access(path, perm):
            if path in ['/tmp', '/tmp2', '/home/foobar'] and perm == 4:
                return False
            return True

        def mock_expandvars(var):
            if var == '$HOME':
                return '/home/foobar'
            return var

        def mock_gettempdir():
            return '/tmp3'

        def mock_chdir(path):
            if path == '/tmp':
                raise Exception()
            thisdir = path
        monkeypatch.setattr(os, 'getcwd', mock_getcwd)
        monkeypatch.setattr(os, 'chdir', mock_chdir)
        monkeypatch.setattr(os, 'access', mock_access)
        monkeypatch.setattr(os.path, 'expandvars', mock_expandvars)
        monkeypatch.setattr(basic, '_ANSIBLE_ARGS', to_bytes(json.dumps({'ANSIBLE_MODULE_ARGS': {}})))
        with patch('time.time', return_value=42):
            am = basic.AnsibleModule(argument_spec={})
        am._tmpdir = '/tmp2'
        monkeypatch.setattr(tempfile, 'gettempdir', mock_gettempdir)
        result = am._set_cwd()
        assert result == '/tmp3'

    def test_set_cwd_unreadable_use_None(self, monkeypatch):
        """all paths are unreable, should return None and not an exception"""

        def mock_getcwd():
            return '/tmp'

        def mock_access(path, perm):
            if path in ['/tmp', '/tmp2', '/tmp3', '/home/foobar'] and perm == 4:
                return False
            return True

        def mock_expandvars(var):
            if var == '$HOME':
                return '/home/foobar'
            return var

        def mock_gettempdir():
            return '/tmp3'

        def mock_chdir(path):
            if path == '/tmp':
                raise Exception()
        monkeypatch.setattr(os, 'getcwd', mock_getcwd)
        monkeypatch.setattr(os, 'chdir', mock_chdir)
        monkeypatch.setattr(os, 'access', mock_access)
        monkeypatch.setattr(os.path, 'expandvars', mock_expandvars)
        monkeypatch.setattr(basic, '_ANSIBLE_ARGS', to_bytes(json.dumps({'ANSIBLE_MODULE_ARGS': {}})))
        with patch('time.time', return_value=42):
            am = basic.AnsibleModule(argument_spec={})
        am._tmpdir = '/tmp2'
        monkeypatch.setattr(tempfile, 'gettempdir', mock_gettempdir)
        result = am._set_cwd()
        assert result is None

def test_TestAnsibleModuleSetCwd_mock_getcwd():
    ret = TestAnsibleModuleSetCwd().mock_getcwd()

def test_TestAnsibleModuleSetCwd_mock_access():
    ret = TestAnsibleModuleSetCwd().mock_access()

def test_TestAnsibleModuleSetCwd_mock_chdir():
    ret = TestAnsibleModuleSetCwd().mock_chdir()

def test_TestAnsibleModuleSetCwd_test_set_cwd():
    ret = TestAnsibleModuleSetCwd().test_set_cwd()

def test_TestAnsibleModuleSetCwd_mock_getcwd():
    ret = TestAnsibleModuleSetCwd().mock_getcwd()

def test_TestAnsibleModuleSetCwd_mock_access():
    ret = TestAnsibleModuleSetCwd().mock_access()

def test_TestAnsibleModuleSetCwd_mock_expandvars():
    ret = TestAnsibleModuleSetCwd().mock_expandvars()

def test_TestAnsibleModuleSetCwd_mock_gettempdir():
    ret = TestAnsibleModuleSetCwd().mock_gettempdir()

def test_TestAnsibleModuleSetCwd_mock_chdir():
    ret = TestAnsibleModuleSetCwd().mock_chdir()

def test_TestAnsibleModuleSetCwd_test_set_cwd_unreadable_use_self_tmpdir():
    ret = TestAnsibleModuleSetCwd().test_set_cwd_unreadable_use_self_tmpdir()

def test_TestAnsibleModuleSetCwd_mock_getcwd():
    ret = TestAnsibleModuleSetCwd().mock_getcwd()

def test_TestAnsibleModuleSetCwd_mock_access():
    ret = TestAnsibleModuleSetCwd().mock_access()

def test_TestAnsibleModuleSetCwd_mock_expandvars():
    ret = TestAnsibleModuleSetCwd().mock_expandvars()

def test_TestAnsibleModuleSetCwd_mock_gettempdir():
    ret = TestAnsibleModuleSetCwd().mock_gettempdir()

def test_TestAnsibleModuleSetCwd_mock_chdir():
    ret = TestAnsibleModuleSetCwd().mock_chdir()

def test_TestAnsibleModuleSetCwd_test_set_cwd_unreadable_use_home():
    ret = TestAnsibleModuleSetCwd().test_set_cwd_unreadable_use_home()

def test_TestAnsibleModuleSetCwd_mock_getcwd():
    ret = TestAnsibleModuleSetCwd().mock_getcwd()

def test_TestAnsibleModuleSetCwd_mock_access():
    ret = TestAnsibleModuleSetCwd().mock_access()

def test_TestAnsibleModuleSetCwd_mock_expandvars():
    ret = TestAnsibleModuleSetCwd().mock_expandvars()

def test_TestAnsibleModuleSetCwd_mock_gettempdir():
    ret = TestAnsibleModuleSetCwd().mock_gettempdir()

def test_TestAnsibleModuleSetCwd_mock_chdir():
    ret = TestAnsibleModuleSetCwd().mock_chdir()

def test_TestAnsibleModuleSetCwd_test_set_cwd_unreadable_use_gettempdir():
    ret = TestAnsibleModuleSetCwd().test_set_cwd_unreadable_use_gettempdir()

def test_TestAnsibleModuleSetCwd_mock_getcwd():
    ret = TestAnsibleModuleSetCwd().mock_getcwd()

def test_TestAnsibleModuleSetCwd_mock_access():
    ret = TestAnsibleModuleSetCwd().mock_access()

def test_TestAnsibleModuleSetCwd_mock_expandvars():
    ret = TestAnsibleModuleSetCwd().mock_expandvars()

def test_TestAnsibleModuleSetCwd_mock_gettempdir():
    ret = TestAnsibleModuleSetCwd().mock_gettempdir()

def test_TestAnsibleModuleSetCwd_mock_chdir():
    ret = TestAnsibleModuleSetCwd().mock_chdir()

def test_TestAnsibleModuleSetCwd_test_set_cwd_unreadable_use_None():
    ret = TestAnsibleModuleSetCwd().test_set_cwd_unreadable_use_None()