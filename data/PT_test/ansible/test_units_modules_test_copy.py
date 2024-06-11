from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pytest
from ansible.modules.copy import AnsibleModuleError, split_pre_existing_dir
from ansible.module_utils.basic import AnsibleModule
THREE_DIRS_DATA = (('/dir1/dir2', None, ('/', ['dir1', 'dir2']), ('/dir1', ['dir2']), ('/dir1/dir2', [])), ('/dir1/dir2/', None, ('/', ['dir1', 'dir2']), ('/dir1', ['dir2']), ('/dir1/dir2', [])))
TWO_DIRS_DATA = (('dir1/dir2', ('.', ['dir1', 'dir2']), ('dir1', ['dir2']), ('dir1/dir2', [])), ('dir1/dir2/', ('.', ['dir1', 'dir2']), ('dir1', ['dir2']), ('dir1/dir2', [])), ('/dir1', None, ('/', ['dir1']), ('/dir1', [])), ('/dir1/', None, ('/', ['dir1']), ('/dir1', []))) + THREE_DIRS_DATA
ONE_DIR_DATA = (('dir1', ('.', ['dir1']), ('dir1', [])), ('dir1/', ('.', ['dir1']), ('dir1', []))) + TWO_DIRS_DATA

@pytest.mark.parametrize('directory, expected', ((d[0], d[4]) for d in THREE_DIRS_DATA))
def test_split_pre_existing_dir_three_levels_exist(directory, expected, mocker):
    (directory,  expected) = ((d[0], d[4]) for d in THREE_DIRS_DATA)[0]
    mocker.patch('os.path.exists', side_effect=[True, True, True])
    split_pre_existing_dir(directory) == expected

@pytest.mark.parametrize('directory, expected', ((d[0], d[3]) for d in TWO_DIRS_DATA))
def test_split_pre_existing_dir_two_levels_exist(directory, expected, mocker):
    (directory,  expected) = ((d[0], d[3]) for d in TWO_DIRS_DATA)[0]
    mocker.patch('os.path.exists', side_effect=[True, True, False])
    split_pre_existing_dir(directory) == expected

@pytest.mark.parametrize('directory, expected', ((d[0], d[2]) for d in ONE_DIR_DATA))
def test_split_pre_existing_dir_one_level_exists(directory, expected, mocker):
    (directory,  expected) = ((d[0], d[2]) for d in ONE_DIR_DATA)[0]
    mocker.patch('os.path.exists', side_effect=[True, False, False])
    split_pre_existing_dir(directory) == expected

@pytest.mark.parametrize('directory', (d[0] for d in ONE_DIR_DATA if d[1] is None))
def test_split_pre_existing_dir_root_does_not_exist(directory, mocker):
    directory = (d[0] for d in ONE_DIR_DATA if d[1] is None)[0]
    mocker.patch('os.path.exists', return_value=False)
    with pytest.raises(AnsibleModuleError) as excinfo:
        split_pre_existing_dir(directory)
    assert excinfo.value.results['msg'].startswith("The '/' directory doesn't exist on this machine.")

@pytest.mark.parametrize('directory, expected', ((d[0], d[1]) for d in ONE_DIR_DATA if not d[0].startswith('/')))
def test_split_pre_existing_dir_working_dir_exists(directory, expected, mocker):
    (directory,  expected) = ((d[0], d[1]) for d in ONE_DIR_DATA if not d[0].startswith('/'))[0]
    mocker.patch('os.path.exists', return_value=False)
    split_pre_existing_dir(directory) == expected
DATA = ((16384, u'a+rwx', 511), (16384, u'u+rwx,g+rwx,o+rwx', 511), (16384, u'o+rwx', 7), (16384, u'g+rwx', 56), (16384, u'u+rwx', 448), (16895, u'a-rwx', 0), (16895, u'u-rwx,g-rwx,o-rwx', 0), (16895, u'o-rwx', 504), (16895, u'g-rwx', 455), (16895, u'u-rwx', 63), (16384, u'a=rwx', 511), (16384, u'u=rwx,g=rwx,o=rwx', 511), (16384, u'o=rwx', 7), (16384, u'g=rwx', 56), (16384, u'u=rwx', 448), (16384, u'a+X', 73), (32768, u'a+X', 0), (16384, u'a=X', 73), (32768, u'a=X', 0), (16895, u'a-X', 438), (33279, u'a-X', 438), (16384, u'u=rw-x+X,g=r-x+X,o=r-x+X', 493), (32768, u'u=rw-x+X,g=r-x+X,o=r-x+X', 420))
UMASK_DATA = ((32768, '+rwx', 504), (33279, '-rwx', 7))
INVALID_DATA = ((16384, u'a=foo', 'bad symbolic permission for mode: a=foo'), (16384, u'f=rwx', 'bad symbolic permission for mode: f=rwx'))

@pytest.mark.parametrize('stat_info, mode_string, expected', DATA)
def test_good_symbolic_modes(mocker, stat_info, mode_string, expected):
    (stat_info,  mode_string,  expected) = DATA[0]
    mock_stat = mocker.MagicMock()
    mock_stat.st_mode = stat_info
    assert AnsibleModule._symbolic_mode_to_octal(mock_stat, mode_string) == expected

@pytest.mark.parametrize('stat_info, mode_string, expected', UMASK_DATA)
def test_umask_with_symbolic_modes(mocker, stat_info, mode_string, expected):
    (stat_info,  mode_string,  expected) = UMASK_DATA[0]
    mock_umask = mocker.patch('os.umask')
    mock_umask.return_value = 7
    mock_stat = mocker.MagicMock()
    mock_stat.st_mode = stat_info
    assert AnsibleModule._symbolic_mode_to_octal(mock_stat, mode_string) == expected

@pytest.mark.parametrize('stat_info, mode_string, expected', INVALID_DATA)
def test_invalid_symbolic_modes(mocker, stat_info, mode_string, expected):
    (stat_info,  mode_string,  expected) = INVALID_DATA[0]
    mock_stat = mocker.MagicMock()
    mock_stat.st_mode = stat_info
    with pytest.raises(ValueError) as exc:
        assert AnsibleModule._symbolic_mode_to_octal(mock_stat, mode_string) == 'blah'
    assert exc.match(expected)