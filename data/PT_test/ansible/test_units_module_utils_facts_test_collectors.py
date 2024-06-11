from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat.mock import Mock, patch
from .base import BaseFactsTest
from ansible.module_utils.facts import collector
from ansible.module_utils.facts.system.apparmor import ApparmorFactCollector
from ansible.module_utils.facts.system.caps import SystemCapabilitiesFactCollector
from ansible.module_utils.facts.system.cmdline import CmdLineFactCollector
from ansible.module_utils.facts.system.distribution import DistributionFactCollector
from ansible.module_utils.facts.system.dns import DnsFactCollector
from ansible.module_utils.facts.system.env import EnvFactCollector
from ansible.module_utils.facts.system.fips import FipsFactCollector
from ansible.module_utils.facts.system.pkg_mgr import PkgMgrFactCollector, OpenBSDPkgMgrFactCollector
from ansible.module_utils.facts.system.platform import PlatformFactCollector
from ansible.module_utils.facts.system.python import PythonFactCollector
from ansible.module_utils.facts.system.selinux import SelinuxFactCollector
from ansible.module_utils.facts.system.service_mgr import ServiceMgrFactCollector
from ansible.module_utils.facts.system.ssh_pub_keys import SshPubKeyFactCollector
from ansible.module_utils.facts.system.user import UserFactCollector
from ansible.module_utils.facts.virtual.base import VirtualCollector
from ansible.module_utils.facts.network.base import NetworkCollector
from ansible.module_utils.facts.hardware.base import HardwareCollector

class CollectorException(Exception):
    pass

class ExceptionThrowingCollector(collector.BaseFactCollector):
    name = 'exc_throwing'

    def __init__(self, collectors=None, namespace=None, exception=None):
        super(ExceptionThrowingCollector, self).__init__(collectors, namespace)
        self._exception = exception or CollectorException('collection failed')

    def collect(self, module=None, collected_facts=None):
        raise self._exception

class TestExceptionThrowingCollector(BaseFactsTest):
    __test__ = True
    gather_subset = ['exc_throwing']
    valid_subsets = ['exc_throwing']
    collector_class = ExceptionThrowingCollector

    def test_collect(self):
        module = self._mock_module()
        fact_collector = self.collector_class()
        self.assertRaises(CollectorException, fact_collector.collect, module=module, collected_facts=self.collected_facts)

    def test_collect_with_namespace(self):
        module = self._mock_module()
        fact_collector = self.collector_class()
        self.assertRaises(CollectorException, fact_collector.collect_with_namespace, module=module, collected_facts=self.collected_facts)

class TestApparmorFacts(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'apparmor']
    valid_subsets = ['apparmor']
    fact_namespace = 'ansible_apparmor'
    collector_class = ApparmorFactCollector

    def test_collect(self):
        facts_dict = super(TestApparmorFacts, self).test_collect()
        self.assertIn('status', facts_dict['apparmor'])

class TestCapsFacts(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'caps']
    valid_subsets = ['caps']
    fact_namespace = 'ansible_system_capabilities'
    collector_class = SystemCapabilitiesFactCollector

    def _mock_module(self):
        mock_module = Mock()
        mock_module.params = {'gather_subset': self.gather_subset, 'gather_timeout': 10, 'filter': '*'}
        mock_module.get_bin_path = Mock(return_value='/usr/sbin/capsh')
        mock_module.run_command = Mock(return_value=(0, 'Current: =ep', ''))
        return mock_module

class TestCmdLineFacts(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'cmdline']
    valid_subsets = ['cmdline']
    fact_namespace = 'ansible_cmdline'
    collector_class = CmdLineFactCollector

    def test_parse_proc_cmdline_uefi(self):
        uefi_cmdline = 'initrd=\\70ef65e1a04a47aea04f7b5145ea3537\\4.10.0-19-generic\\initrd root=UUID=50973b75-4a66-4bf0-9764-2b7614489e64 ro quiet'
        expected = {'initrd': '\\70ef65e1a04a47aea04f7b5145ea3537\\4.10.0-19-generic\\initrd', 'root': 'UUID=50973b75-4a66-4bf0-9764-2b7614489e64', 'quiet': True, 'ro': True}
        fact_collector = self.collector_class()
        facts_dict = fact_collector._parse_proc_cmdline(uefi_cmdline)
        self.assertDictEqual(facts_dict, expected)

    def test_parse_proc_cmdline_fedora(self):
        cmdline_fedora = 'BOOT_IMAGE=/vmlinuz-4.10.16-200.fc25.x86_64 root=/dev/mapper/fedora-root ro rd.lvm.lv=fedora/root rd.luks.uuid=luks-c80b7537-358b-4a07-b88c-c59ef187479b rd.lvm.lv=fedora/swap rhgb quiet LANG=en_US.UTF-8'
        expected = {'BOOT_IMAGE': '/vmlinuz-4.10.16-200.fc25.x86_64', 'LANG': 'en_US.UTF-8', 'quiet': True, 'rd.luks.uuid': 'luks-c80b7537-358b-4a07-b88c-c59ef187479b', 'rd.lvm.lv': 'fedora/swap', 'rhgb': True, 'ro': True, 'root': '/dev/mapper/fedora-root'}
        fact_collector = self.collector_class()
        facts_dict = fact_collector._parse_proc_cmdline(cmdline_fedora)
        self.assertDictEqual(facts_dict, expected)

    def test_parse_proc_cmdline_dup_console(self):
        example = 'BOOT_IMAGE=/boot/vmlinuz-4.4.0-72-generic root=UUID=e12e46d9-06c9-4a64-a7b3-60e24b062d90 ro console=tty1 console=ttyS0'
        expected = {'BOOT_IMAGE': '/boot/vmlinuz-4.4.0-72-generic', 'root': 'UUID=e12e46d9-06c9-4a64-a7b3-60e24b062d90', 'ro': True, 'console': 'ttyS0'}
        fact_collector = self.collector_class()
        facts_dict = fact_collector._parse_proc_cmdline(example)
        self.assertDictEqual(facts_dict, expected)

class TestDistributionFacts(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'distribution']
    valid_subsets = ['distribution']
    fact_namespace = 'ansible_distribution'
    collector_class = DistributionFactCollector

class TestDnsFacts(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'dns']
    valid_subsets = ['dns']
    fact_namespace = 'ansible_dns'
    collector_class = DnsFactCollector

class TestEnvFacts(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'env']
    valid_subsets = ['env']
    fact_namespace = 'ansible_env'
    collector_class = EnvFactCollector

    def test_collect(self):
        facts_dict = super(TestEnvFacts, self).test_collect()
        self.assertIn('HOME', facts_dict['env'])

class TestFipsFacts(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'fips']
    valid_subsets = ['fips']
    fact_namespace = 'ansible_fips'
    collector_class = FipsFactCollector

class TestHardwareCollector(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'hardware']
    valid_subsets = ['hardware']
    fact_namespace = 'ansible_hardware'
    collector_class = HardwareCollector
    collected_facts = {'ansible_architecture': 'x86_64'}

class TestNetworkCollector(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'network']
    valid_subsets = ['network']
    fact_namespace = 'ansible_network'
    collector_class = NetworkCollector

class TestPkgMgrFacts(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'pkg_mgr']
    valid_subsets = ['pkg_mgr']
    fact_namespace = 'ansible_pkgmgr'
    collector_class = PkgMgrFactCollector
    collected_facts = {'ansible_distribution': 'Fedora', 'ansible_distribution_major_version': '28', 'ansible_os_family': 'RedHat'}

    def test_collect(self):
        module = self._mock_module()
        fact_collector = self.collector_class()
        facts_dict = fact_collector.collect(module=module, collected_facts=self.collected_facts)
        self.assertIsInstance(facts_dict, dict)
        self.assertIn('pkg_mgr', facts_dict)

def _sanitize_os_path_apt_get(path):
    if path == '/usr/bin/apt-get':
        return True
    else:
        return False

class TestPkgMgrFactsAptFedora(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'pkg_mgr']
    valid_subsets = ['pkg_mgr']
    fact_namespace = 'ansible_pkgmgr'
    collector_class = PkgMgrFactCollector
    collected_facts = {'ansible_distribution': 'Fedora', 'ansible_distribution_major_version': '28', 'ansible_os_family': 'RedHat', 'ansible_pkg_mgr': 'apt'}

    @patch('ansible.module_utils.facts.system.pkg_mgr.os.path.exists', side_effect=_sanitize_os_path_apt_get)
    def test_collect(self, mock_os_path_exists):
        module = self._mock_module()
        fact_collector = self.collector_class()
        facts_dict = fact_collector.collect(module=module, collected_facts=self.collected_facts)
        self.assertIsInstance(facts_dict, dict)
        self.assertIn('pkg_mgr', facts_dict)

class TestOpenBSDPkgMgrFacts(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'pkg_mgr']
    valid_subsets = ['pkg_mgr']
    fact_namespace = 'ansible_pkgmgr'
    collector_class = OpenBSDPkgMgrFactCollector

    def test_collect(self):
        module = self._mock_module()
        fact_collector = self.collector_class()
        facts_dict = fact_collector.collect(module=module, collected_facts=self.collected_facts)
        self.assertIsInstance(facts_dict, dict)
        self.assertIn('pkg_mgr', facts_dict)
        self.assertEqual(facts_dict['pkg_mgr'], 'openbsd_pkg')

class TestPlatformFactCollector(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'platform']
    valid_subsets = ['platform']
    fact_namespace = 'ansible_platform'
    collector_class = PlatformFactCollector

class TestPythonFactCollector(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'python']
    valid_subsets = ['python']
    fact_namespace = 'ansible_python'
    collector_class = PythonFactCollector

class TestSelinuxFacts(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'selinux']
    valid_subsets = ['selinux']
    fact_namespace = 'ansible_selinux'
    collector_class = SelinuxFactCollector

    def test_no_selinux(self):
        with patch('ansible.module_utils.facts.system.selinux.HAVE_SELINUX', False):
            module = self._mock_module()
            fact_collector = self.collector_class()
            facts_dict = fact_collector.collect(module=module)
            self.assertIsInstance(facts_dict, dict)
            self.assertEqual(facts_dict['selinux']['status'], 'Missing selinux Python library')
            return facts_dict

class TestServiceMgrFacts(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'service_mgr']
    valid_subsets = ['service_mgr']
    fact_namespace = 'ansible_service_mgr'
    collector_class = ServiceMgrFactCollector

    @patch('ansible.module_utils.facts.system.service_mgr.get_file_content', return_value=None)
    def test_no_proc1(self, mock_gfc):
        module = self._mock_module()
        module.run_command = Mock(return_value=(1, '', 'wat'))
        fact_collector = self.collector_class()
        facts_dict = fact_collector.collect(module=module)
        self.assertIsInstance(facts_dict, dict)
        self.assertEqual(facts_dict['service_mgr'], 'service')

    @patch('ansible.module_utils.facts.system.service_mgr.get_file_content', return_value=None)
    def test_no_proc1_ps_random_init(self, mock_gfc):
        module = self._mock_module()
        module.run_command = Mock(return_value=(0, '/sbin/sys11', ''))
        fact_collector = self.collector_class()
        facts_dict = fact_collector.collect(module=module)
        self.assertIsInstance(facts_dict, dict)
        self.assertEqual(facts_dict['service_mgr'], 'sys11')

    @patch('ansible.module_utils.facts.system.service_mgr.get_file_content', return_value=None)
    def test_clowncar(self, mock_gfc):
        module = self._mock_module()
        module.run_command = Mock(return_value=(1, '', ''))
        collected_facts = {'distribution': 'clowncar', 'system': 'ClownCarOS'}
        fact_collector = self.collector_class()
        facts_dict = fact_collector.collect(module=module, collected_facts=collected_facts)
        self.assertIsInstance(facts_dict, dict)
        self.assertEqual(facts_dict['service_mgr'], 'service')

class TestSshPubKeyFactCollector(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'ssh_pub_keys']
    valid_subsets = ['ssh_pub_keys']
    fact_namespace = 'ansible_ssh_pub_leys'
    collector_class = SshPubKeyFactCollector

class TestUserFactCollector(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'user']
    valid_subsets = ['user']
    fact_namespace = 'ansible_user'
    collector_class = UserFactCollector

class TestVirtualFacts(BaseFactsTest):
    __test__ = True
    gather_subset = ['!all', 'virtual']
    valid_subsets = ['virtual']
    fact_namespace = 'ansible_virtual'
    collector_class = VirtualCollector

def test_ExceptionThrowingCollector_collect():
    ret = ExceptionThrowingCollector().collect()

def test_TestExceptionThrowingCollector_test_collect():
    ret = TestExceptionThrowingCollector().test_collect()

def test_TestExceptionThrowingCollector_test_collect_with_namespace():
    ret = TestExceptionThrowingCollector().test_collect_with_namespace()

def test_TestApparmorFacts_test_collect():
    ret = TestApparmorFacts().test_collect()

def test_TestCapsFacts__mock_module():
    ret = TestCapsFacts()._mock_module()

def test_TestCmdLineFacts_test_parse_proc_cmdline_uefi():
    ret = TestCmdLineFacts().test_parse_proc_cmdline_uefi()

def test_TestCmdLineFacts_test_parse_proc_cmdline_fedora():
    ret = TestCmdLineFacts().test_parse_proc_cmdline_fedora()

def test_TestCmdLineFacts_test_parse_proc_cmdline_dup_console():
    ret = TestCmdLineFacts().test_parse_proc_cmdline_dup_console()

def test_TestEnvFacts_test_collect():
    ret = TestEnvFacts().test_collect()

def test_TestPkgMgrFacts_test_collect():
    ret = TestPkgMgrFacts().test_collect()

def test_TestPkgMgrFactsAptFedora_test_collect():
    ret = TestPkgMgrFactsAptFedora().test_collect()

def test_TestOpenBSDPkgMgrFacts_test_collect():
    ret = TestOpenBSDPkgMgrFacts().test_collect()

def test_TestSelinuxFacts_test_no_selinux():
    ret = TestSelinuxFacts().test_no_selinux()

def test_TestServiceMgrFacts_test_no_proc1():
    ret = TestServiceMgrFacts().test_no_proc1()

def test_TestServiceMgrFacts_test_no_proc1_ps_random_init():
    ret = TestServiceMgrFacts().test_no_proc1_ps_random_init()

def test_TestServiceMgrFacts_test_clowncar():
    ret = TestServiceMgrFacts().test_clowncar()