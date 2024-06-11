from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from units.compat.mock import patch
from ansible.module_utils.facts import utils

class TestGetMountSize(unittest.TestCase):

    def test(self):
        mount_info = utils.get_mount_size('/dev/null/not/a/real/mountpoint')
        self.assertIsInstance(mount_info, dict)

    def test_proc(self):
        mount_info = utils.get_mount_size('/proc')
        self.assertIsInstance(mount_info, dict)

    @patch('ansible.module_utils.facts.utils.os.statvfs', side_effect=OSError('intentionally induced os error'))
    def test_oserror_on_statvfs(self, mock_statvfs):
        mount_info = utils.get_mount_size('/dev/null/doesnt/matter')
        self.assertIsInstance(mount_info, dict)
        self.assertDictEqual(mount_info, {})

def test_TestGetMountSize_test():
    ret = TestGetMountSize().test()

def test_TestGetMountSize_test_proc():
    ret = TestGetMountSize().test_proc()

def test_TestGetMountSize_test_oserror_on_statvfs():
    ret = TestGetMountSize().test_oserror_on_statvfs()