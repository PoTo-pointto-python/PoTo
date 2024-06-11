from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pytest
from ansible.module_utils.common.process import get_bin_path

def test_get_bin_path(mocker):
    path = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
    mocker.patch.dict('os.environ', {'PATH': path})
    mocker.patch('os.pathsep', ':')
    mocker.patch('os.path.isdir', return_value=False)
    mocker.patch('ansible.module_utils.common.process.is_executable', return_value=True)
    mocker.patch('os.path.exists', side_effect=[False, True])
    assert '/usr/local/bin/notacommand' == get_bin_path('notacommand')

def test_get_path_path_raise_valueerror(mocker):
    mocker.patch.dict('os.environ', {'PATH': ''})
    mocker.patch('os.path.exists', return_value=False)
    mocker.patch('os.path.isdir', return_value=False)
    mocker.patch('ansible.module_utils.common.process.is_executable', return_value=True)
    with pytest.raises(ValueError, match='Failed to find required executable notacommand'):
        get_bin_path('notacommand')