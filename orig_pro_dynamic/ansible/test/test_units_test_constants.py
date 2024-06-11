from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pwd
import os
import pytest
from ansible import constants
from ansible.module_utils.six import StringIO
from ansible.module_utils.six.moves import configparser
from ansible.module_utils._text import to_text

@pytest.fixture
def cfgparser():
    CFGDATA = StringIO("\n[defaults]\ndefaults_one = 'data_defaults_one'\n\n[level1]\nlevel1_one = 'data_level1_one'\n    ")
    p = configparser.ConfigParser()
    p.readfp(CFGDATA)
    return p

@pytest.fixture
def user():
    user = {}
    user['uid'] = os.geteuid()
    pwd_entry = pwd.getpwuid(user['uid'])
    user['username'] = pwd_entry.pw_name
    user['home'] = pwd_entry.pw_dir
    return user

@pytest.fixture
def cfg_file():
    data = '/ansible/test/cfg/path'
    old_cfg_file = constants.CONFIG_FILE
    constants.CONFIG_FILE = os.path.join(data, 'ansible.cfg')
    yield data
    constants.CONFIG_FILE = old_cfg_file

@pytest.fixture
def null_cfg_file():
    old_cfg_file = constants.CONFIG_FILE
    del constants.CONFIG_FILE
    yield
    constants.CONFIG_FILE = old_cfg_file

@pytest.fixture
def cwd():
    data = '/ansible/test/cwd/'
    old_cwd = os.getcwd
    os.getcwd = lambda : data
    old_cwdu = None
    if hasattr(os, 'getcwdu'):
        old_cwdu = os.getcwdu
        os.getcwdu = lambda : to_text(data)
    yield data
    os.getcwd = old_cwd
    if hasattr(os, 'getcwdu'):
        os.getcwdu = old_cwdu