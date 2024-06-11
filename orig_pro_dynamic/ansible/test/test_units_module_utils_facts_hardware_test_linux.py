from __future__ import absolute_import, division, print_function
__metaclass__ = type
import os
from units.compat import unittest
from units.compat.mock import Mock, patch
from ansible.module_utils.facts import timeout
from ansible.module_utils.facts.hardware import linux
from .linux_data import LSBLK_OUTPUT, LSBLK_OUTPUT_2, LSBLK_UUIDS, MTAB, MTAB_ENTRIES, BIND_MOUNTS, STATVFS_INFO, UDEVADM_UUID, UDEVADM_OUTPUT
with open(os.path.join(os.path.dirname(__file__), '../fixtures/findmount_output.txt')) as f:
    FINDMNT_OUTPUT = f.read()
GET_MOUNT_SIZE = {}

def mock_get_mount_size(mountpoint):
    return STATVFS_INFO.get(mountpoint, {})

class TestFactsLinuxHardwareGetMountFacts(unittest.TestCase):

    def setUp(self):
        timeout.GATHER_TIMEOUT = 10

    def tearDown(self):
        timeout.GATHER_TIMEOUT = None

    @patch('ansible.module_utils.facts.hardware.linux.LinuxHardware._mtab_entries', return_value=MTAB_ENTRIES)
    @patch('ansible.module_utils.facts.hardware.linux.LinuxHardware._find_bind_mounts', return_value=BIND_MOUNTS)
    @patch('ansible.module_utils.facts.hardware.linux.LinuxHardware._lsblk_uuid', return_value=LSBLK_UUIDS)
    @patch('ansible.module_utils.facts.hardware.linux.get_mount_size', side_effect=mock_get_mount_size)
    @patch('ansible.module_utils.facts.hardware.linux.LinuxHardware._udevadm_uuid', return_value=UDEVADM_UUID)
    def test_get_mount_facts(self, mock_get_mount_size, mock_lsblk_uuid, mock_find_bind_mounts, mock_mtab_entries, mock_udevadm_uuid):
        module = Mock()
        lh = linux.LinuxHardware(module=module, load_on_init=False)
        mount_facts = lh.get_mount_facts()
        self.assertIsInstance(mount_facts, dict)
        self.assertIn('mounts', mount_facts)
        self.assertIsInstance(mount_facts['mounts'], list)
        self.assertIsInstance(mount_facts['mounts'][0], dict)
        home_expected = {'block_available': 1001578731, 'block_size': 4096, 'block_total': 105871006, 'block_used': 5713133, 'device': '/dev/mapper/fedora_dhcp129--186-home', 'fstype': 'ext4', 'inode_available': 26860880, 'inode_total': 26902528, 'inode_used': 41648, 'mount': '/home', 'options': 'rw,seclabel,relatime,data=ordered', 'size_available': 410246647808, 'size_total': 433647640576, 'uuid': 'N/A'}
        home_info = [x for x in mount_facts['mounts'] if x['mount'] == '/home'][0]
        self.maxDiff = 4096
        self.assertDictEqual(home_info, home_expected)

    @patch('ansible.module_utils.facts.hardware.linux.get_file_content', return_value=MTAB)
    def test_get_mtab_entries(self, mock_get_file_content):
        module = Mock()
        lh = linux.LinuxHardware(module=module, load_on_init=False)
        mtab_entries = lh._mtab_entries()
        self.assertIsInstance(mtab_entries, list)
        self.assertIsInstance(mtab_entries[0], list)
        self.assertEqual(len(mtab_entries), 38)

    @patch('ansible.module_utils.facts.hardware.linux.LinuxHardware._run_findmnt', return_value=(0, FINDMNT_OUTPUT, ''))
    def test_find_bind_mounts(self, mock_run_findmnt):
        module = Mock()
        lh = linux.LinuxHardware(module=module, load_on_init=False)
        bind_mounts = lh._find_bind_mounts()
        self.assertIsInstance(bind_mounts, set)
        self.assertEqual(len(bind_mounts), 1)
        self.assertIn('/not/a/real/bind_mount', bind_mounts)

    @patch('ansible.module_utils.facts.hardware.linux.LinuxHardware._run_findmnt', return_value=(37, '', ''))
    def test_find_bind_mounts_non_zero(self, mock_run_findmnt):
        module = Mock()
        lh = linux.LinuxHardware(module=module, load_on_init=False)
        bind_mounts = lh._find_bind_mounts()
        self.assertIsInstance(bind_mounts, set)
        self.assertEqual(len(bind_mounts), 0)

    def test_find_bind_mounts_no_findmnts(self):
        module = Mock()
        module.get_bin_path = Mock(return_value=None)
        lh = linux.LinuxHardware(module=module, load_on_init=False)
        bind_mounts = lh._find_bind_mounts()
        self.assertIsInstance(bind_mounts, set)
        self.assertEqual(len(bind_mounts), 0)

    @patch('ansible.module_utils.facts.hardware.linux.LinuxHardware._run_lsblk', return_value=(0, LSBLK_OUTPUT, ''))
    def test_lsblk_uuid(self, mock_run_lsblk):
        module = Mock()
        lh = linux.LinuxHardware(module=module, load_on_init=False)
        lsblk_uuids = lh._lsblk_uuid()
        self.assertIsInstance(lsblk_uuids, dict)
        self.assertIn(b'/dev/loop9', lsblk_uuids)
        self.assertIn(b'/dev/sda1', lsblk_uuids)
        self.assertEqual(lsblk_uuids[b'/dev/sda1'], b'32caaec3-ef40-4691-a3b6-438c3f9bc1c0')

    @patch('ansible.module_utils.facts.hardware.linux.LinuxHardware._run_lsblk', return_value=(37, LSBLK_OUTPUT, ''))
    def test_lsblk_uuid_non_zero(self, mock_run_lsblk):
        module = Mock()
        lh = linux.LinuxHardware(module=module, load_on_init=False)
        lsblk_uuids = lh._lsblk_uuid()
        self.assertIsInstance(lsblk_uuids, dict)
        self.assertEqual(len(lsblk_uuids), 0)

    def test_lsblk_uuid_no_lsblk(self):
        module = Mock()
        module.get_bin_path = Mock(return_value=None)
        lh = linux.LinuxHardware(module=module, load_on_init=False)
        lsblk_uuids = lh._lsblk_uuid()
        self.assertIsInstance(lsblk_uuids, dict)
        self.assertEqual(len(lsblk_uuids), 0)

    @patch('ansible.module_utils.facts.hardware.linux.LinuxHardware._run_lsblk', return_value=(0, LSBLK_OUTPUT_2, ''))
    def test_lsblk_uuid_dev_with_space_in_name(self, mock_run_lsblk):
        module = Mock()
        lh = linux.LinuxHardware(module=module, load_on_init=False)
        lsblk_uuids = lh._lsblk_uuid()
        self.assertIsInstance(lsblk_uuids, dict)
        self.assertIn(b'/dev/loop0', lsblk_uuids)
        self.assertIn(b'/dev/sda1', lsblk_uuids)
        self.assertEqual(lsblk_uuids[b'/dev/mapper/an-example-mapper with a space in the name'], b'84639acb-013f-4d2f-9392-526a572b4373')
        self.assertEqual(lsblk_uuids[b'/dev/sda1'], b'32caaec3-ef40-4691-a3b6-438c3f9bc1c0')

    def test_udevadm_uuid(self):
        module = Mock()
        module.run_command = Mock(return_value=(0, UDEVADM_OUTPUT, ''))
        lh = linux.LinuxHardware(module=module, load_on_init=False)
        udevadm_uuid = lh._udevadm_uuid('mock_device')
        self.assertEqual(udevadm_uuid, '57b1a3e7-9019-4747-9809-7ec52bba9179')

def test_TestFactsLinuxHardwareGetMountFacts_setUp():
    ret = TestFactsLinuxHardwareGetMountFacts().setUp()

def test_TestFactsLinuxHardwareGetMountFacts_tearDown():
    ret = TestFactsLinuxHardwareGetMountFacts().tearDown()

def test_TestFactsLinuxHardwareGetMountFacts_test_get_mount_facts():
    ret = TestFactsLinuxHardwareGetMountFacts().test_get_mount_facts()

def test_TestFactsLinuxHardwareGetMountFacts_test_get_mtab_entries():
    ret = TestFactsLinuxHardwareGetMountFacts().test_get_mtab_entries()

def test_TestFactsLinuxHardwareGetMountFacts_test_find_bind_mounts():
    ret = TestFactsLinuxHardwareGetMountFacts().test_find_bind_mounts()

def test_TestFactsLinuxHardwareGetMountFacts_test_find_bind_mounts_non_zero():
    ret = TestFactsLinuxHardwareGetMountFacts().test_find_bind_mounts_non_zero()

def test_TestFactsLinuxHardwareGetMountFacts_test_find_bind_mounts_no_findmnts():
    ret = TestFactsLinuxHardwareGetMountFacts().test_find_bind_mounts_no_findmnts()

def test_TestFactsLinuxHardwareGetMountFacts_test_lsblk_uuid():
    ret = TestFactsLinuxHardwareGetMountFacts().test_lsblk_uuid()

def test_TestFactsLinuxHardwareGetMountFacts_test_lsblk_uuid_non_zero():
    ret = TestFactsLinuxHardwareGetMountFacts().test_lsblk_uuid_non_zero()

def test_TestFactsLinuxHardwareGetMountFacts_test_lsblk_uuid_no_lsblk():
    ret = TestFactsLinuxHardwareGetMountFacts().test_lsblk_uuid_no_lsblk()

def test_TestFactsLinuxHardwareGetMountFacts_test_lsblk_uuid_dev_with_space_in_name():
    ret = TestFactsLinuxHardwareGetMountFacts().test_lsblk_uuid_dev_with_space_in_name()

def test_TestFactsLinuxHardwareGetMountFacts_test_udevadm_uuid():
    ret = TestFactsLinuxHardwareGetMountFacts().test_udevadm_uuid()