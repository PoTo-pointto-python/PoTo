from __future__ import absolute_import, division, print_function
__metaclass__ = type
import os
from units.compat import unittest
from units.compat.mock import patch, mock_open
from ansible.errors import AnsibleParserError, yaml_strings, AnsibleFileNotFound
from ansible.parsing.vault import AnsibleVaultError
from ansible.module_utils._text import to_text
from ansible.module_utils.six import PY3
from units.mock.vault_helper import TextVaultSecret
from ansible.parsing.dataloader import DataLoader
from units.mock.path import mock_unfrackpath_noop

class TestDataLoader(unittest.TestCase):

    def setUp(self):
        self._loader = DataLoader()

    @patch('os.path.exists')
    def test__is_role(self, p_exists):
        p_exists.side_effect = lambda p: p == b'test_path/tasks/main.yml'
        self.assertTrue(self._loader._is_role('test_path/tasks'))
        self.assertTrue(self._loader._is_role('test_path/'))

    @patch.object(DataLoader, '_get_file_contents')
    def test_parse_json_from_file(self, mock_def):
        mock_def.return_value = (b'{"a": 1, "b": 2, "c": 3}', True)
        output = self._loader.load_from_file('dummy_json.txt')
        self.assertEqual(output, dict(a=1, b=2, c=3))

    @patch.object(DataLoader, '_get_file_contents')
    def test_parse_yaml_from_file(self, mock_def):
        mock_def.return_value = (b'\n        a: 1\n        b: 2\n        c: 3\n        ', True)
        output = self._loader.load_from_file('dummy_yaml.txt')
        self.assertEqual(output, dict(a=1, b=2, c=3))

    @patch.object(DataLoader, '_get_file_contents')
    def test_parse_fail_from_file(self, mock_def):
        mock_def.return_value = (b'\n        TEXT:\n            ***\n               NOT VALID\n        ', True)
        self.assertRaises(AnsibleParserError, self._loader.load_from_file, 'dummy_yaml_bad.txt')

    @patch('ansible.errors.AnsibleError._get_error_lines_from_file')
    @patch.object(DataLoader, '_get_file_contents')
    def test_tab_error(self, mock_def, mock_get_error_lines):
        mock_def.return_value = (u'---\nhosts: localhost\nvars:\n  foo: bar\n\tblip: baz', True)
        mock_get_error_lines.return_value = ('\tblip: baz', '..foo: bar')
        with self.assertRaises(AnsibleParserError) as cm:
            self._loader.load_from_file('dummy_yaml_text.txt')
        self.assertIn(yaml_strings.YAML_COMMON_LEADING_TAB_ERROR, str(cm.exception))
        self.assertIn('foo: bar', str(cm.exception))

    @patch('ansible.parsing.dataloader.unfrackpath', mock_unfrackpath_noop)
    @patch.object(DataLoader, '_is_role')
    def test_path_dwim_relative(self, mock_is_role):
        """
        simulate a nested dynamic include:

        playbook.yml:
        - hosts: localhost
          roles:
            - { role: 'testrole' }

        testrole/tasks/main.yml:
        - include: "include1.yml"
          static: no

        testrole/tasks/include1.yml:
        - include: include2.yml
          static: no

        testrole/tasks/include2.yml:
        - debug: msg="blah"
        """
        mock_is_role.return_value = False
        with patch('os.path.exists') as mock_os_path_exists:
            mock_os_path_exists.return_value = False
            self._loader.path_dwim_relative('/tmp/roles/testrole/tasks', 'tasks', 'included2.yml')
            called_args = [os.path.normpath(to_text(call[0][0])) for call in mock_os_path_exists.call_args_list]
            self.assertIn('/tmp/roles/testrole/tasks/included2.yml', called_args)
            self.assertIn('/tmp/roles/testrole/tasks/tasks/included2.yml', called_args)
            self.assertIn('tasks/included2.yml', called_args)
            self.assertIn('included2.yml', called_args)

    def test_path_dwim_root(self):
        self.assertEqual(self._loader.path_dwim('/'), '/')

    def test_path_dwim_home(self):
        self.assertEqual(self._loader.path_dwim('~'), os.path.expanduser('~'))

    def test_path_dwim_tilde_slash(self):
        self.assertEqual(self._loader.path_dwim('~/'), os.path.expanduser('~'))

    def test_get_real_file(self):
        self.assertEqual(self._loader.get_real_file(__file__), __file__)

    def test_is_file(self):
        self.assertTrue(self._loader.is_file(__file__))

    def test_is_directory_positive(self):
        self.assertTrue(self._loader.is_directory(os.path.dirname(__file__)))

    def test_get_file_contents_none_path(self):
        self.assertRaisesRegexp(AnsibleParserError, 'Invalid filename', self._loader._get_file_contents, None)

    def test_get_file_contents_non_existent_path(self):
        self.assertRaises(AnsibleFileNotFound, self._loader._get_file_contents, '/non_existent_file')

class TestPathDwimRelativeDataLoader(unittest.TestCase):

    def setUp(self):
        self._loader = DataLoader()

    def test_all_slash(self):
        self.assertEqual(self._loader.path_dwim_relative('/', '/', '/'), '/')

    def test_path_endswith_role(self):
        self.assertEqual(self._loader.path_dwim_relative(path='foo/bar/tasks/', dirname='/', source='/'), '/')

    def test_path_endswith_role_main_yml(self):
        self.assertIn('main.yml', self._loader.path_dwim_relative(path='foo/bar/tasks/', dirname='/', source='main.yml'))

    def test_path_endswith_role_source_tilde(self):
        self.assertEqual(self._loader.path_dwim_relative(path='foo/bar/tasks/', dirname='/', source='~/'), os.path.expanduser('~'))

class TestPathDwimRelativeStackDataLoader(unittest.TestCase):

    def setUp(self):
        self._loader = DataLoader()

    def test_none(self):
        self.assertRaisesRegexp(AnsibleFileNotFound, 'on the Ansible Controller', self._loader.path_dwim_relative_stack, None, None, None)

    def test_empty_strings(self):
        self.assertEqual(self._loader.path_dwim_relative_stack('', '', ''), './')

    def test_empty_lists(self):
        self.assertEqual(self._loader.path_dwim_relative_stack([], '', '~/'), os.path.expanduser('~'))

    def test_all_slash(self):
        self.assertEqual(self._loader.path_dwim_relative_stack('/', '/', '/'), '/')

    def test_path_endswith_role(self):
        self.assertEqual(self._loader.path_dwim_relative_stack(paths=['foo/bar/tasks/'], dirname='/', source='/'), '/')

    def test_path_endswith_role_source_tilde(self):
        self.assertEqual(self._loader.path_dwim_relative_stack(paths=['foo/bar/tasks/'], dirname='/', source='~/'), os.path.expanduser('~'))

    def test_path_endswith_role_source_main_yml(self):
        self.assertRaises(AnsibleFileNotFound, self._loader.path_dwim_relative_stack, ['foo/bar/tasks/'], '/', 'main.yml')

    def test_path_endswith_role_source_main_yml_source_in_dirname(self):
        self.assertRaises(AnsibleFileNotFound, self._loader.path_dwim_relative_stack, 'foo/bar/tasks/', 'tasks', 'tasks/main.yml')

class TestDataLoaderWithVault(unittest.TestCase):

    def setUp(self):
        self._loader = DataLoader()
        vault_secrets = [('default', TextVaultSecret('ansible'))]
        self._loader.set_vault_secrets(vault_secrets)
        self.test_vault_data_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'vault.yml')

    def tearDown(self):
        pass

    def test_get_real_file_vault(self):
        real_file_path = self._loader.get_real_file(self.test_vault_data_path)
        self.assertTrue(os.path.exists(real_file_path))

    def test_get_real_file_vault_no_vault(self):
        self._loader.set_vault_secrets(None)
        self.assertRaises(AnsibleParserError, self._loader.get_real_file, self.test_vault_data_path)

    def test_get_real_file_vault_wrong_password(self):
        wrong_vault = [('default', TextVaultSecret('wrong_password'))]
        self._loader.set_vault_secrets(wrong_vault)
        self.assertRaises(AnsibleVaultError, self._loader.get_real_file, self.test_vault_data_path)

    def test_get_real_file_not_a_path(self):
        self.assertRaisesRegexp(AnsibleParserError, 'Invalid filename', self._loader.get_real_file, None)

    @patch.multiple(DataLoader, path_exists=lambda s, x: True, is_file=lambda s, x: True)
    def test_parse_from_vault_1_1_file(self):
        vaulted_data = '$ANSIBLE_VAULT;1.1;AES256\n33343734386261666161626433386662623039356366656637303939306563376130623138626165\n6436333766346533353463636566313332623130383662340a393835656134633665333861393331\n37666233346464636263636530626332623035633135363732623332313534306438393366323966\n3135306561356164310a343937653834643433343734653137383339323330626437313562306630\n3035\n'
        if PY3:
            builtins_name = 'builtins'
        else:
            builtins_name = '__builtin__'
        with patch(builtins_name + '.open', mock_open(read_data=vaulted_data.encode('utf-8'))):
            output = self._loader.load_from_file('dummy_vault.txt')
            self.assertEqual(output, dict(foo='bar'))

def test_TestDataLoader_setUp():
    ret = TestDataLoader().setUp()

def test_TestDataLoader_test__is_role():
    ret = TestDataLoader().test__is_role()

def test_TestDataLoader_test_parse_json_from_file():
    ret = TestDataLoader().test_parse_json_from_file()

def test_TestDataLoader_test_parse_yaml_from_file():
    ret = TestDataLoader().test_parse_yaml_from_file()

def test_TestDataLoader_test_parse_fail_from_file():
    ret = TestDataLoader().test_parse_fail_from_file()

def test_TestDataLoader_test_tab_error():
    ret = TestDataLoader().test_tab_error()

def test_TestDataLoader_test_path_dwim_relative():
    ret = TestDataLoader().test_path_dwim_relative()

def test_TestDataLoader_test_path_dwim_root():
    ret = TestDataLoader().test_path_dwim_root()

def test_TestDataLoader_test_path_dwim_home():
    ret = TestDataLoader().test_path_dwim_home()

def test_TestDataLoader_test_path_dwim_tilde_slash():
    ret = TestDataLoader().test_path_dwim_tilde_slash()

def test_TestDataLoader_test_get_real_file():
    ret = TestDataLoader().test_get_real_file()

def test_TestDataLoader_test_is_file():
    ret = TestDataLoader().test_is_file()

def test_TestDataLoader_test_is_directory_positive():
    ret = TestDataLoader().test_is_directory_positive()

def test_TestDataLoader_test_get_file_contents_none_path():
    ret = TestDataLoader().test_get_file_contents_none_path()

def test_TestDataLoader_test_get_file_contents_non_existent_path():
    ret = TestDataLoader().test_get_file_contents_non_existent_path()

def test_TestPathDwimRelativeDataLoader_setUp():
    ret = TestPathDwimRelativeDataLoader().setUp()

def test_TestPathDwimRelativeDataLoader_test_all_slash():
    ret = TestPathDwimRelativeDataLoader().test_all_slash()

def test_TestPathDwimRelativeDataLoader_test_path_endswith_role():
    ret = TestPathDwimRelativeDataLoader().test_path_endswith_role()

def test_TestPathDwimRelativeDataLoader_test_path_endswith_role_main_yml():
    ret = TestPathDwimRelativeDataLoader().test_path_endswith_role_main_yml()

def test_TestPathDwimRelativeDataLoader_test_path_endswith_role_source_tilde():
    ret = TestPathDwimRelativeDataLoader().test_path_endswith_role_source_tilde()

def test_TestPathDwimRelativeStackDataLoader_setUp():
    ret = TestPathDwimRelativeStackDataLoader().setUp()

def test_TestPathDwimRelativeStackDataLoader_test_none():
    ret = TestPathDwimRelativeStackDataLoader().test_none()

def test_TestPathDwimRelativeStackDataLoader_test_empty_strings():
    ret = TestPathDwimRelativeStackDataLoader().test_empty_strings()

def test_TestPathDwimRelativeStackDataLoader_test_empty_lists():
    ret = TestPathDwimRelativeStackDataLoader().test_empty_lists()

def test_TestPathDwimRelativeStackDataLoader_test_all_slash():
    ret = TestPathDwimRelativeStackDataLoader().test_all_slash()

def test_TestPathDwimRelativeStackDataLoader_test_path_endswith_role():
    ret = TestPathDwimRelativeStackDataLoader().test_path_endswith_role()

def test_TestPathDwimRelativeStackDataLoader_test_path_endswith_role_source_tilde():
    ret = TestPathDwimRelativeStackDataLoader().test_path_endswith_role_source_tilde()

def test_TestPathDwimRelativeStackDataLoader_test_path_endswith_role_source_main_yml():
    ret = TestPathDwimRelativeStackDataLoader().test_path_endswith_role_source_main_yml()

def test_TestPathDwimRelativeStackDataLoader_test_path_endswith_role_source_main_yml_source_in_dirname():
    ret = TestPathDwimRelativeStackDataLoader().test_path_endswith_role_source_main_yml_source_in_dirname()

def test_TestDataLoaderWithVault_setUp():
    ret = TestDataLoaderWithVault().setUp()

def test_TestDataLoaderWithVault_tearDown():
    ret = TestDataLoaderWithVault().tearDown()

def test_TestDataLoaderWithVault_test_get_real_file_vault():
    ret = TestDataLoaderWithVault().test_get_real_file_vault()

def test_TestDataLoaderWithVault_test_get_real_file_vault_no_vault():
    ret = TestDataLoaderWithVault().test_get_real_file_vault_no_vault()

def test_TestDataLoaderWithVault_test_get_real_file_vault_wrong_password():
    ret = TestDataLoaderWithVault().test_get_real_file_vault_wrong_password()

def test_TestDataLoaderWithVault_test_get_real_file_not_a_path():
    ret = TestDataLoaderWithVault().test_get_real_file_not_a_path()

def test_TestDataLoaderWithVault_test_parse_from_vault_1_1_file():
    ret = TestDataLoaderWithVault().test_parse_from_vault_1_1_file()