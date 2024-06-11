from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from units.compat.mock import patch, MagicMock
from units.mock.loader import DictDataLoader
from ansible.release import __version__
from ansible.parsing import vault
from ansible import cli

class TestCliVersion(unittest.TestCase):

    def test_version_info(self):
        version_info = cli.CLI.version_info()
        self.assertEqual(version_info['string'], __version__)

    def test_version_info_gitinfo(self):
        version_info = cli.CLI.version_info(gitinfo=True)
        self.assertIn('python version', version_info['string'])

class TestCliBuildVaultIds(unittest.TestCase):

    def setUp(self):
        self.tty_patcher = patch('ansible.cli.sys.stdin.isatty', return_value=True)
        self.mock_isatty = self.tty_patcher.start()

    def tearDown(self):
        self.tty_patcher.stop()

    def test(self):
        res = cli.CLI.build_vault_ids(['foo@bar'])
        self.assertEqual(res, ['foo@bar'])

    def test_create_new_password_no_vault_id(self):
        res = cli.CLI.build_vault_ids([], create_new_password=True)
        self.assertEqual(res, ['default@prompt_ask_vault_pass'])

    def test_create_new_password_no_vault_id_no_auto_prompt(self):
        res = cli.CLI.build_vault_ids([], auto_prompt=False, create_new_password=True)
        self.assertEqual(res, [])

    def test_no_vault_id_no_auto_prompt(self):
        res = cli.CLI.build_vault_ids([], auto_prompt=False)
        self.assertEqual(res, [])

    def test_no_vault_ids_auto_prompt(self):
        res = cli.CLI.build_vault_ids([], auto_prompt=True)
        self.assertEqual(res, ['default@prompt_ask_vault_pass'])

    def test_no_vault_ids_auto_prompt_ask_vault_pass(self):
        res = cli.CLI.build_vault_ids([], auto_prompt=True, ask_vault_pass=True)
        self.assertEqual(res, ['default@prompt_ask_vault_pass'])

    def test_create_new_password_auto_prompt(self):
        res = cli.CLI.build_vault_ids([], auto_prompt=True, create_new_password=True)
        self.assertEqual(res, ['default@prompt_ask_vault_pass'])

    def test_create_new_password_no_vault_id_ask_vault_pass(self):
        res = cli.CLI.build_vault_ids([], ask_vault_pass=True, create_new_password=True)
        self.assertEqual(res, ['default@prompt_ask_vault_pass'])

    def test_create_new_password_with_vault_ids(self):
        res = cli.CLI.build_vault_ids(['foo@bar'], create_new_password=True)
        self.assertEqual(res, ['foo@bar'])

    def test_create_new_password_no_vault_ids_password_files(self):
        res = cli.CLI.build_vault_ids([], vault_password_files=['some-password-file'], create_new_password=True)
        self.assertEqual(res, ['default@some-password-file'])

    def test_everything(self):
        res = cli.CLI.build_vault_ids(['blip@prompt', 'baz@prompt_ask_vault_pass', 'some-password-file', 'qux@another-password-file'], vault_password_files=['yet-another-password-file', 'one-more-password-file'], ask_vault_pass=True, create_new_password=True, auto_prompt=False)
        self.assertEqual(set(res), set(['blip@prompt', 'baz@prompt_ask_vault_pass', 'default@prompt_ask_vault_pass', 'some-password-file', 'qux@another-password-file', 'default@yet-another-password-file', 'default@one-more-password-file']))

class TestCliSetupVaultSecrets(unittest.TestCase):

    def setUp(self):
        self.fake_loader = DictDataLoader({})
        self.tty_patcher = patch('ansible.cli.sys.stdin.isatty', return_value=True)
        self.mock_isatty = self.tty_patcher.start()
        self.display_v_patcher = patch('ansible.cli.display.verbosity', return_value=6)
        self.mock_display_v = self.display_v_patcher.start()
        cli.display.verbosity = 5

    def tearDown(self):
        self.tty_patcher.stop()
        self.display_v_patcher.stop()
        cli.display.verbosity = 0

    def test(self):
        res = cli.CLI.setup_vault_secrets(None, None, auto_prompt=False)
        self.assertIsInstance(res, list)

    @patch('ansible.cli.get_file_vault_secret')
    def test_password_file(self, mock_file_secret):
        filename = '/dev/null/secret'
        mock_file_secret.return_value = MagicMock(bytes=b'file1_password', vault_id='file1', filename=filename)
        res = cli.CLI.setup_vault_secrets(loader=self.fake_loader, vault_ids=['secret1@%s' % filename, 'secret2'], vault_password_files=[filename])
        self.assertIsInstance(res, list)
        matches = vault.match_secrets(res, ['secret1'])
        self.assertIn('secret1', [x[0] for x in matches])
        match = matches[0][1]
        self.assertEqual(match.bytes, b'file1_password')

    @patch('ansible.cli.PromptVaultSecret')
    def test_prompt(self, mock_prompt_secret):
        mock_prompt_secret.return_value = MagicMock(bytes=b'prompt1_password', vault_id='prompt1')
        res = cli.CLI.setup_vault_secrets(loader=self.fake_loader, vault_ids=['prompt1@prompt'], ask_vault_pass=True, auto_prompt=False)
        self.assertIsInstance(res, list)
        matches = vault.match_secrets(res, ['prompt1'])
        self.assertIn('prompt1', [x[0] for x in matches])
        match = matches[0][1]
        self.assertEqual(match.bytes, b'prompt1_password')

    @patch('ansible.cli.PromptVaultSecret')
    def test_prompt_no_tty(self, mock_prompt_secret):
        self.mock_isatty.return_value = False
        mock_prompt_secret.return_value = MagicMock(bytes=b'prompt1_password', vault_id='prompt1', name='bytes_should_be_prompt1_password', spec=vault.PromptVaultSecret)
        res = cli.CLI.setup_vault_secrets(loader=self.fake_loader, vault_ids=['prompt1@prompt'], ask_vault_pass=True, auto_prompt=False)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 2)
        matches = vault.match_secrets(res, ['prompt1'])
        self.assertIn('prompt1', [x[0] for x in matches])
        self.assertEqual(len(matches), 1)

    @patch('ansible.cli.get_file_vault_secret')
    @patch('ansible.cli.PromptVaultSecret')
    def test_prompt_no_tty_and_password_file(self, mock_prompt_secret, mock_file_secret):
        self.mock_isatty.return_value = False
        mock_prompt_secret.return_value = MagicMock(bytes=b'prompt1_password', vault_id='prompt1')
        filename = '/dev/null/secret'
        mock_file_secret.return_value = MagicMock(bytes=b'file1_password', vault_id='file1', filename=filename)
        res = cli.CLI.setup_vault_secrets(loader=self.fake_loader, vault_ids=['prompt1@prompt', 'file1@/dev/null/secret'], ask_vault_pass=True)
        self.assertIsInstance(res, list)
        matches = vault.match_secrets(res, ['file1'])
        self.assertIn('file1', [x[0] for x in matches])
        self.assertNotIn('prompt1', [x[0] for x in matches])
        match = matches[0][1]
        self.assertEqual(match.bytes, b'file1_password')

    def _assert_ids(self, vault_id_names, res, password=b'prompt1_password'):
        self.assertIsInstance(res, list)
        len_ids = len(vault_id_names)
        matches = vault.match_secrets(res, vault_id_names)
        self.assertEqual(len(res), len_ids, 'len(res):%s does not match len_ids:%s' % (len(res), len_ids))
        self.assertEqual(len(matches), len_ids)
        for (index, prompt) in enumerate(vault_id_names):
            self.assertIn(prompt, [x[0] for x in matches])
            self.assertEqual(matches[index][1].bytes, password)

    @patch('ansible.cli.PromptVaultSecret')
    def test_multiple_prompts(self, mock_prompt_secret):
        mock_prompt_secret.return_value = MagicMock(bytes=b'prompt1_password', vault_id='prompt1')
        res = cli.CLI.setup_vault_secrets(loader=self.fake_loader, vault_ids=['prompt1@prompt', 'prompt2@prompt'], ask_vault_pass=False)
        vault_id_names = ['prompt1', 'prompt2']
        self._assert_ids(vault_id_names, res)

    @patch('ansible.cli.PromptVaultSecret')
    def test_multiple_prompts_and_ask_vault_pass(self, mock_prompt_secret):
        self.mock_isatty.return_value = False
        mock_prompt_secret.return_value = MagicMock(bytes=b'prompt1_password', vault_id='prompt1')
        res = cli.CLI.setup_vault_secrets(loader=self.fake_loader, vault_ids=['prompt1@prompt', 'prompt2@prompt', 'prompt3@prompt_ask_vault_pass'], ask_vault_pass=True)
        vault_id_names = ['prompt1', 'prompt2', 'prompt3', 'default']
        self._assert_ids(vault_id_names, res)

    @patch('ansible.cli.C')
    @patch('ansible.cli.get_file_vault_secret')
    @patch('ansible.cli.PromptVaultSecret')
    def test_default_file_vault(self, mock_prompt_secret, mock_file_secret, mock_config):
        mock_prompt_secret.return_value = MagicMock(bytes=b'prompt1_password', vault_id='default')
        mock_file_secret.return_value = MagicMock(bytes=b'file1_password', vault_id='default')
        mock_config.DEFAULT_VAULT_PASSWORD_FILE = '/dev/null/faux/vault_password_file'
        mock_config.DEFAULT_VAULT_IDENTITY = 'default'
        res = cli.CLI.setup_vault_secrets(loader=self.fake_loader, vault_ids=[], create_new_password=False, ask_vault_pass=False)
        self.assertIsInstance(res, list)
        matches = vault.match_secrets(res, ['default'])
        self.assertEqual(matches[0][1].bytes, b'file1_password')
        self.assertEqual(len(matches), 1)
        res = cli.CLI.setup_vault_secrets(loader=self.fake_loader, vault_ids=[], create_new_password=False, ask_vault_pass=True, auto_prompt=True)
        self.assertIsInstance(res, list)
        matches = vault.match_secrets(res, ['default'])
        self.assertEqual(matches[0][1].bytes, b'file1_password')
        self.assertEqual(matches[1][1].bytes, b'prompt1_password')
        self.assertEqual(len(matches), 2)

    @patch('ansible.cli.get_file_vault_secret')
    @patch('ansible.cli.PromptVaultSecret')
    def test_default_file_vault_identity_list(self, mock_prompt_secret, mock_file_secret):
        default_vault_ids = ['some_prompt@prompt', 'some_file@/dev/null/secret']
        mock_prompt_secret.return_value = MagicMock(bytes=b'some_prompt_password', vault_id='some_prompt')
        filename = '/dev/null/secret'
        mock_file_secret.return_value = MagicMock(bytes=b'some_file_password', vault_id='some_file', filename=filename)
        vault_ids = default_vault_ids
        res = cli.CLI.setup_vault_secrets(loader=self.fake_loader, vault_ids=vault_ids, create_new_password=False, ask_vault_pass=True)
        self.assertIsInstance(res, list)
        matches = vault.match_secrets(res, ['some_file'])
        self.assertEqual(matches[0][1].bytes, b'some_file_password')
        matches = vault.match_secrets(res, ['some_prompt'])
        self.assertEqual(matches[0][1].bytes, b'some_prompt_password')

    @patch('ansible.cli.PromptVaultSecret')
    def test_prompt_just_ask_vault_pass(self, mock_prompt_secret):
        mock_prompt_secret.return_value = MagicMock(bytes=b'prompt1_password', vault_id='default')
        res = cli.CLI.setup_vault_secrets(loader=self.fake_loader, vault_ids=[], create_new_password=False, ask_vault_pass=True)
        self.assertIsInstance(res, list)
        match = vault.match_secrets(res, ['default'])[0][1]
        self.assertEqual(match.bytes, b'prompt1_password')

    @patch('ansible.cli.PromptVaultSecret')
    def test_prompt_new_password_ask_vault_pass(self, mock_prompt_secret):
        mock_prompt_secret.return_value = MagicMock(bytes=b'prompt1_password', vault_id='default')
        res = cli.CLI.setup_vault_secrets(loader=self.fake_loader, vault_ids=[], create_new_password=True, ask_vault_pass=True)
        self.assertIsInstance(res, list)
        match = vault.match_secrets(res, ['default'])[0][1]
        self.assertEqual(match.bytes, b'prompt1_password')

    @patch('ansible.cli.PromptVaultSecret')
    def test_prompt_new_password_vault_id_prompt(self, mock_prompt_secret):
        mock_prompt_secret.return_value = MagicMock(bytes=b'prompt1_password', vault_id='some_vault_id')
        res = cli.CLI.setup_vault_secrets(loader=self.fake_loader, vault_ids=['some_vault_id@prompt'], create_new_password=True, ask_vault_pass=False)
        self.assertIsInstance(res, list)
        match = vault.match_secrets(res, ['some_vault_id'])[0][1]
        self.assertEqual(match.bytes, b'prompt1_password')

    @patch('ansible.cli.PromptVaultSecret')
    def test_prompt_new_password_vault_id_prompt_ask_vault_pass(self, mock_prompt_secret):
        mock_prompt_secret.return_value = MagicMock(bytes=b'prompt1_password', vault_id='default')
        res = cli.CLI.setup_vault_secrets(loader=self.fake_loader, vault_ids=['some_vault_id@prompt_ask_vault_pass'], create_new_password=True, ask_vault_pass=False)
        self.assertIsInstance(res, list)
        match = vault.match_secrets(res, ['some_vault_id'])[0][1]
        self.assertEqual(match.bytes, b'prompt1_password')

    @patch('ansible.cli.PromptVaultSecret')
    def test_prompt_new_password_vault_id_prompt_ask_vault_pass_ask_vault_pass(self, mock_prompt_secret):
        mock_prompt_secret.return_value = MagicMock(bytes=b'prompt1_password', vault_id='default')
        res = cli.CLI.setup_vault_secrets(loader=self.fake_loader, vault_ids=['some_vault_id@prompt_ask_vault_pass'], create_new_password=True, ask_vault_pass=True)
        self.assertIsInstance(res, list)
        match = vault.match_secrets(res, ['some_vault_id'])[0][1]
        self.assertEqual(match.bytes, b'prompt1_password')

def test_TestCliVersion_test_version_info():
    ret = TestCliVersion().test_version_info()

def test_TestCliVersion_test_version_info_gitinfo():
    ret = TestCliVersion().test_version_info_gitinfo()

def test_TestCliBuildVaultIds_setUp():
    ret = TestCliBuildVaultIds().setUp()

def test_TestCliBuildVaultIds_tearDown():
    ret = TestCliBuildVaultIds().tearDown()

def test_TestCliBuildVaultIds_test():
    ret = TestCliBuildVaultIds().test()

def test_TestCliBuildVaultIds_test_create_new_password_no_vault_id():
    ret = TestCliBuildVaultIds().test_create_new_password_no_vault_id()

def test_TestCliBuildVaultIds_test_create_new_password_no_vault_id_no_auto_prompt():
    ret = TestCliBuildVaultIds().test_create_new_password_no_vault_id_no_auto_prompt()

def test_TestCliBuildVaultIds_test_no_vault_id_no_auto_prompt():
    ret = TestCliBuildVaultIds().test_no_vault_id_no_auto_prompt()

def test_TestCliBuildVaultIds_test_no_vault_ids_auto_prompt():
    ret = TestCliBuildVaultIds().test_no_vault_ids_auto_prompt()

def test_TestCliBuildVaultIds_test_no_vault_ids_auto_prompt_ask_vault_pass():
    ret = TestCliBuildVaultIds().test_no_vault_ids_auto_prompt_ask_vault_pass()

def test_TestCliBuildVaultIds_test_create_new_password_auto_prompt():
    ret = TestCliBuildVaultIds().test_create_new_password_auto_prompt()

def test_TestCliBuildVaultIds_test_create_new_password_no_vault_id_ask_vault_pass():
    ret = TestCliBuildVaultIds().test_create_new_password_no_vault_id_ask_vault_pass()

def test_TestCliBuildVaultIds_test_create_new_password_with_vault_ids():
    ret = TestCliBuildVaultIds().test_create_new_password_with_vault_ids()

def test_TestCliBuildVaultIds_test_create_new_password_no_vault_ids_password_files():
    ret = TestCliBuildVaultIds().test_create_new_password_no_vault_ids_password_files()

def test_TestCliBuildVaultIds_test_everything():
    ret = TestCliBuildVaultIds().test_everything()

def test_TestCliSetupVaultSecrets_setUp():
    ret = TestCliSetupVaultSecrets().setUp()

def test_TestCliSetupVaultSecrets_tearDown():
    ret = TestCliSetupVaultSecrets().tearDown()

def test_TestCliSetupVaultSecrets_test():
    ret = TestCliSetupVaultSecrets().test()

def test_TestCliSetupVaultSecrets_test_password_file():
    ret = TestCliSetupVaultSecrets().test_password_file()

def test_TestCliSetupVaultSecrets_test_prompt():
    ret = TestCliSetupVaultSecrets().test_prompt()

def test_TestCliSetupVaultSecrets_test_prompt_no_tty():
    ret = TestCliSetupVaultSecrets().test_prompt_no_tty()

def test_TestCliSetupVaultSecrets_test_prompt_no_tty_and_password_file():
    ret = TestCliSetupVaultSecrets().test_prompt_no_tty_and_password_file()

def test_TestCliSetupVaultSecrets__assert_ids():
    ret = TestCliSetupVaultSecrets()._assert_ids()

def test_TestCliSetupVaultSecrets_test_multiple_prompts():
    ret = TestCliSetupVaultSecrets().test_multiple_prompts()

def test_TestCliSetupVaultSecrets_test_multiple_prompts_and_ask_vault_pass():
    ret = TestCliSetupVaultSecrets().test_multiple_prompts_and_ask_vault_pass()

def test_TestCliSetupVaultSecrets_test_default_file_vault():
    ret = TestCliSetupVaultSecrets().test_default_file_vault()

def test_TestCliSetupVaultSecrets_test_default_file_vault_identity_list():
    ret = TestCliSetupVaultSecrets().test_default_file_vault_identity_list()

def test_TestCliSetupVaultSecrets_test_prompt_just_ask_vault_pass():
    ret = TestCliSetupVaultSecrets().test_prompt_just_ask_vault_pass()

def test_TestCliSetupVaultSecrets_test_prompt_new_password_ask_vault_pass():
    ret = TestCliSetupVaultSecrets().test_prompt_new_password_ask_vault_pass()

def test_TestCliSetupVaultSecrets_test_prompt_new_password_vault_id_prompt():
    ret = TestCliSetupVaultSecrets().test_prompt_new_password_vault_id_prompt()

def test_TestCliSetupVaultSecrets_test_prompt_new_password_vault_id_prompt_ask_vault_pass():
    ret = TestCliSetupVaultSecrets().test_prompt_new_password_vault_id_prompt_ask_vault_pass()

def test_TestCliSetupVaultSecrets_test_prompt_new_password_vault_id_prompt_ask_vault_pass_ask_vault_pass():
    ret = TestCliSetupVaultSecrets().test_prompt_new_password_vault_id_prompt_ask_vault_pass_ask_vault_pass()