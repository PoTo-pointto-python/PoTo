from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.mock.procenv import ModuleTestCase
from units.compat.mock import patch
from ansible.module_utils.six.moves import builtins
realimport = builtins.__import__

class TestGetModulePath(ModuleTestCase):

    def test_module_utils_basic_get_module_path(self):
        from ansible.module_utils.basic import get_module_path
        with patch('os.path.realpath', return_value='/path/to/foo/'):
            self.assertEqual(get_module_path(), '/path/to/foo')

def test_TestGetModulePath_test_module_utils_basic_get_module_path():
    ret = TestGetModulePath().test_module_utils_basic_get_module_path()