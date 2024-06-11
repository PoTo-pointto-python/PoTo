from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pytest
from ansible.module_utils.basic import AnsibleModule
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