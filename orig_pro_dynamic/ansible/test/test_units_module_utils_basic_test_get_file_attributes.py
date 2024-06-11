from __future__ import absolute_import, division, print_function
__metaclass__ = type
from itertools import product
from ansible.module_utils.basic import AnsibleModule
import pytest
DATA = (('3353595900 --------------e---- /usr/lib32', {'attr_flags': 'e', 'version': '3353595900', 'attributes': ['extents']}), ('78053594 -----------I--e---- /usr/lib', {'attr_flags': 'Ie', 'version': '78053594', 'attributes': ['indexed', 'extents']}), ('15711607 -------A------e---- /tmp/test', {'attr_flags': 'Ae', 'version': '15711607', 'attributes': ['noatime', 'extents']}), ('78053594   -----------I--e---- /usr/lib', {'attr_flags': 'Ie', 'version': '78053594', 'attributes': ['indexed', 'extents']}), ('15711607   -------A------e---- /tmp/test', {'attr_flags': 'Ae', 'version': '15711607', 'attributes': ['noatime', 'extents']}))

@pytest.mark.parametrize('stdin, data', product(({},), DATA), indirect=['stdin'])
def test_get_file_attributes(am, stdin, mocker, data):
    (stdin,  data) = product(({},), DATA)[0]
    mocker.patch.object(AnsibleModule, 'get_bin_path', return_value=(0, '/usr/bin/lsattr', ''))
    mocker.patch.object(AnsibleModule, 'run_command', return_value=(0, data[0], ''))
    result = am.get_file_attributes('/path/to/file')
    for (key, value) in data[1].items():
        assert key in result and result[key] == value