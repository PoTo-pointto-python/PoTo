from __future__ import absolute_import, division, print_function
__metaclass__ = type
import binascii
import io
import os
import tempfile
from binascii import hexlify
import pytest
from units.compat import unittest
from units.compat.mock import patch, MagicMock
from ansible import errors
from ansible.module_utils import six
from ansible.module_utils._text import to_bytes, to_text
from ansible.parsing import vault
from units.mock.loader import DictDataLoader
from units.mock.vault_helper import TextVaultSecret

class TestUnhexlify(unittest.TestCase):

    def test(self):
        b_plain_data = b'some text to hexlify'
        b_data = hexlify(b_plain_data)
        res = vault._unhexlify(b_data)
        self.assertEqual(res, b_plain_data)

    def test_odd_length(self):
        b_data = b'123456789abcdefghijklmnopqrstuvwxyz'
        self.assertRaisesRegexp(vault.AnsibleVaultFormatError, '.*Vault format unhexlify error.*', vault._unhexlify, b_data)

    def test_nonhex(self):
        b_data = b'6z36316566653264333665333637623064303639353237620a636366633565663263336335656532'
        self.assertRaisesRegexp(vault.AnsibleVaultFormatError, '.*Vault format unhexlify error.*Non-hexadecimal digit found', vault._unhexlify, b_data)

class TestParseVaulttext(unittest.TestCase):

    def test(self):
        vaulttext_envelope = u'$ANSIBLE_VAULT;1.1;AES256\n33363965326261303234626463623963633531343539616138316433353830356566396130353436\n3562643163366231316662386565383735653432386435610a306664636137376132643732393835\n63383038383730306639353234326630666539346233376330303938323639306661313032396437\n6233623062366136310a633866373936313238333730653739323461656662303864663666653563\n3138'
        b_vaulttext_envelope = to_bytes(vaulttext_envelope, errors='strict', encoding='utf-8')
        (b_vaulttext, b_version, cipher_name, vault_id) = vault.parse_vaulttext_envelope(b_vaulttext_envelope)
        res = vault.parse_vaulttext(b_vaulttext)
        self.assertIsInstance(res[0], bytes)
        self.assertIsInstance(res[1], bytes)
        self.assertIsInstance(res[2], bytes)

    def test_non_hex(self):
        vaulttext_envelope = u'$ANSIBLE_VAULT;1.1;AES256\n3336396J326261303234626463623963633531343539616138316433353830356566396130353436\n3562643163366231316662386565383735653432386435610a306664636137376132643732393835\n63383038383730306639353234326630666539346233376330303938323639306661313032396437\n6233623062366136310a633866373936313238333730653739323461656662303864663666653563\n3138'
        b_vaulttext_envelope = to_bytes(vaulttext_envelope, errors='strict', encoding='utf-8')
        (b_vaulttext, b_version, cipher_name, vault_id) = vault.parse_vaulttext_envelope(b_vaulttext_envelope)
        self.assertRaisesRegexp(vault.AnsibleVaultFormatError, '.*Vault format unhexlify error.*Non-hexadecimal digit found', vault.parse_vaulttext, b_vaulttext_envelope)

class TestVaultSecret(unittest.TestCase):

    def test(self):
        secret = vault.VaultSecret()
        secret.load()
        self.assertIsNone(secret._bytes)

    def test_bytes(self):
        some_text = u'私はガラスを食べられます。それは私を傷つけません。'
        _bytes = to_bytes(some_text)
        secret = vault.VaultSecret(_bytes)
        secret.load()
        self.assertEqual(secret.bytes, _bytes)

class TestPromptVaultSecret(unittest.TestCase):

    def test_empty_prompt_formats(self):
        secret = vault.PromptVaultSecret(vault_id='test_id', prompt_formats=[])
        secret.load()
        self.assertIsNone(secret._bytes)

    @patch('ansible.parsing.vault.display.prompt', return_value='the_password')
    def test_prompt_formats_none(self, mock_display_prompt):
        secret = vault.PromptVaultSecret(vault_id='test_id')
        secret.load()
        self.assertEqual(secret._bytes, b'the_password')

    @patch('ansible.parsing.vault.display.prompt', return_value='the_password')
    def test_custom_prompt(self, mock_display_prompt):
        secret = vault.PromptVaultSecret(vault_id='test_id', prompt_formats=['The cow flies at midnight: '])
        secret.load()
        self.assertEqual(secret._bytes, b'the_password')

    @patch('ansible.parsing.vault.display.prompt', side_effect=EOFError)
    def test_prompt_eoferror(self, mock_display_prompt):
        secret = vault.PromptVaultSecret(vault_id='test_id')
        self.assertRaisesRegexp(vault.AnsibleVaultError, 'EOFError.*test_id', secret.load)

    @patch('ansible.parsing.vault.display.prompt', side_effect=['first_password', 'second_password'])
    def test_prompt_passwords_dont_match(self, mock_display_prompt):
        secret = vault.PromptVaultSecret(vault_id='test_id', prompt_formats=['Vault password: ', 'Confirm Vault password: '])
        self.assertRaisesRegexp(errors.AnsibleError, 'Passwords do not match', secret.load)

class TestFileVaultSecret(unittest.TestCase):

    def setUp(self):
        self.vault_password = 'test-vault-password'
        text_secret = TextVaultSecret(self.vault_password)
        self.vault_secrets = [('foo', text_secret)]

    def test(self):
        secret = vault.FileVaultSecret()
        self.assertIsNone(secret._bytes)
        self.assertIsNone(secret._text)

    def test_repr_empty(self):
        secret = vault.FileVaultSecret()
        self.assertEqual(repr(secret), 'FileVaultSecret()')

    def test_repr(self):
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        fake_loader = DictDataLoader({tmp_file.name: 'sdfadf'})
        secret = vault.FileVaultSecret(loader=fake_loader, filename=tmp_file.name)
        filename = tmp_file.name
        tmp_file.close()
        self.assertEqual(repr(secret), "FileVaultSecret(filename='%s')" % filename)

    def test_empty_bytes(self):
        secret = vault.FileVaultSecret()
        self.assertIsNone(secret.bytes)

    def test_file(self):
        password = 'some password'
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write(to_bytes(password))
        tmp_file.close()
        fake_loader = DictDataLoader({tmp_file.name: 'sdfadf'})
        secret = vault.FileVaultSecret(loader=fake_loader, filename=tmp_file.name)
        secret.load()
        os.unlink(tmp_file.name)
        self.assertEqual(secret.bytes, to_bytes(password))

    def test_file_empty(self):
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write(to_bytes(''))
        tmp_file.close()
        fake_loader = DictDataLoader({tmp_file.name: ''})
        secret = vault.FileVaultSecret(loader=fake_loader, filename=tmp_file.name)
        self.assertRaisesRegexp(vault.AnsibleVaultPasswordError, 'Invalid vault password was provided from file.*%s' % tmp_file.name, secret.load)
        os.unlink(tmp_file.name)

    def test_file_encrypted(self):
        vault_password = 'test-vault-password'
        text_secret = TextVaultSecret(vault_password)
        vault_secrets = [('foo', text_secret)]
        password = 'some password'
        password_file_content = '$ANSIBLE_VAULT;1.1;AES256\n61393863643638653437313566313632306462383837303132346434616433313438353634613762\n3334363431623364386164616163326537366333353663650a663634306232363432626162353665\n39623061353266373631636331643761306665343731376633623439313138396330346237653930\n6432643864346136640a653364386634666461306231353765636662316335613235383565306437\n3737\n'
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write(to_bytes(password_file_content))
        tmp_file.close()
        fake_loader = DictDataLoader({tmp_file.name: 'sdfadf'})
        fake_loader._vault.secrets = vault_secrets
        secret = vault.FileVaultSecret(loader=fake_loader, filename=tmp_file.name)
        secret.load()
        os.unlink(tmp_file.name)
        self.assertEqual(secret.bytes, to_bytes(password))

    def test_file_not_a_directory(self):
        filename = '/dev/null/foobar'
        fake_loader = DictDataLoader({filename: 'sdfadf'})
        secret = vault.FileVaultSecret(loader=fake_loader, filename=filename)
        self.assertRaisesRegexp(errors.AnsibleError, '.*Could not read vault password file.*/dev/null/foobar.*Not a directory', secret.load)

    def test_file_not_found(self):
        tmp_file = tempfile.NamedTemporaryFile()
        filename = os.path.realpath(tmp_file.name)
        tmp_file.close()
        fake_loader = DictDataLoader({filename: 'sdfadf'})
        secret = vault.FileVaultSecret(loader=fake_loader, filename=filename)
        self.assertRaisesRegexp(errors.AnsibleError, '.*Could not read vault password file.*%s.*' % filename, secret.load)

class TestScriptVaultSecret(unittest.TestCase):

    def test(self):
        secret = vault.ScriptVaultSecret()
        self.assertIsNone(secret._bytes)
        self.assertIsNone(secret._text)

    def _mock_popen(self, mock_popen, return_code=0, stdout=b'', stderr=b''):

        def communicate():
            return (stdout, stderr)
        mock_popen.return_value = MagicMock(returncode=return_code)
        mock_popen_instance = mock_popen.return_value
        mock_popen_instance.communicate = communicate

    @patch('ansible.parsing.vault.subprocess.Popen')
    def test_read_file(self, mock_popen):
        self._mock_popen(mock_popen, stdout=b'some_password')
        secret = vault.ScriptVaultSecret()
        with patch.object(secret, 'loader') as mock_loader:
            mock_loader.is_executable = MagicMock(return_value=True)
            secret.load()

    @patch('ansible.parsing.vault.subprocess.Popen')
    def test_read_file_empty(self, mock_popen):
        self._mock_popen(mock_popen, stdout=b'')
        secret = vault.ScriptVaultSecret()
        with patch.object(secret, 'loader') as mock_loader:
            mock_loader.is_executable = MagicMock(return_value=True)
            self.assertRaisesRegexp(vault.AnsibleVaultPasswordError, 'Invalid vault password was provided from script', secret.load)

    @patch('ansible.parsing.vault.subprocess.Popen')
    def test_read_file_os_error(self, mock_popen):
        self._mock_popen(mock_popen)
        mock_popen.side_effect = OSError('That is not an executable')
        secret = vault.ScriptVaultSecret()
        with patch.object(secret, 'loader') as mock_loader:
            mock_loader.is_executable = MagicMock(return_value=True)
            self.assertRaisesRegexp(errors.AnsibleError, 'Problem running vault password script.*', secret.load)

    @patch('ansible.parsing.vault.subprocess.Popen')
    def test_read_file_not_executable(self, mock_popen):
        self._mock_popen(mock_popen)
        secret = vault.ScriptVaultSecret()
        with patch.object(secret, 'loader') as mock_loader:
            mock_loader.is_executable = MagicMock(return_value=False)
            self.assertRaisesRegexp(vault.AnsibleVaultError, 'The vault password script .* was not executable', secret.load)

    @patch('ansible.parsing.vault.subprocess.Popen')
    def test_read_file_non_zero_return_code(self, mock_popen):
        stderr = b'That did not work for a random reason'
        rc = 37
        self._mock_popen(mock_popen, return_code=rc, stderr=stderr)
        secret = vault.ScriptVaultSecret(filename='/dev/null/some_vault_secret')
        with patch.object(secret, 'loader') as mock_loader:
            mock_loader.is_executable = MagicMock(return_value=True)
            self.assertRaisesRegexp(errors.AnsibleError, 'Vault password script.*returned non-zero \\(%s\\): %s' % (rc, stderr), secret.load)

class TestScriptIsClient(unittest.TestCase):

    def test_randomname(self):
        filename = 'randomname'
        res = vault.script_is_client(filename)
        self.assertFalse(res)

    def test_something_dash_client(self):
        filename = 'something-client'
        res = vault.script_is_client(filename)
        self.assertTrue(res)

    def test_something_dash_client_somethingelse(self):
        filename = 'something-client-somethingelse'
        res = vault.script_is_client(filename)
        self.assertFalse(res)

    def test_something_dash_client_py(self):
        filename = 'something-client.py'
        res = vault.script_is_client(filename)
        self.assertTrue(res)

    def test_full_path_something_dash_client_py(self):
        filename = '/foo/bar/something-client.py'
        res = vault.script_is_client(filename)
        self.assertTrue(res)

    def test_full_path_something_dash_client(self):
        filename = '/foo/bar/something-client'
        res = vault.script_is_client(filename)
        self.assertTrue(res)

    def test_full_path_something_dash_client_in_dir(self):
        filename = '/foo/bar/something-client/but/not/filename'
        res = vault.script_is_client(filename)
        self.assertFalse(res)

class TestGetFileVaultSecret(unittest.TestCase):

    def test_file(self):
        password = 'some password'
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write(to_bytes(password))
        tmp_file.close()
        fake_loader = DictDataLoader({tmp_file.name: 'sdfadf'})
        secret = vault.get_file_vault_secret(filename=tmp_file.name, loader=fake_loader)
        secret.load()
        os.unlink(tmp_file.name)
        self.assertEqual(secret.bytes, to_bytes(password))

    def test_file_not_a_directory(self):
        filename = '/dev/null/foobar'
        fake_loader = DictDataLoader({filename: 'sdfadf'})
        self.assertRaisesRegexp(errors.AnsibleError, '.*The vault password file %s was not found.*' % filename, vault.get_file_vault_secret, filename=filename, loader=fake_loader)

    def test_file_not_found(self):
        tmp_file = tempfile.NamedTemporaryFile()
        filename = os.path.realpath(tmp_file.name)
        tmp_file.close()
        fake_loader = DictDataLoader({filename: 'sdfadf'})
        self.assertRaisesRegexp(errors.AnsibleError, '.*The vault password file %s was not found.*' % filename, vault.get_file_vault_secret, filename=filename, loader=fake_loader)

class TestVaultIsEncrypted(unittest.TestCase):

    def test_bytes_not_encrypted(self):
        b_data = b'foobar'
        self.assertFalse(vault.is_encrypted(b_data))

    def test_bytes_encrypted(self):
        b_data = b'$ANSIBLE_VAULT;9.9;TEST\n%s' % hexlify(b'ansible')
        self.assertTrue(vault.is_encrypted(b_data))

    def test_text_not_encrypted(self):
        b_data = to_text(b'foobar')
        self.assertFalse(vault.is_encrypted(b_data))

    def test_text_encrypted(self):
        b_data = to_text(b'$ANSIBLE_VAULT;9.9;TEST\n%s' % hexlify(b'ansible'))
        self.assertTrue(vault.is_encrypted(b_data))

    def test_invalid_text_not_ascii(self):
        data = u'$ANSIBLE_VAULT;9.9;TEST\n%s' % u'ァ ア ィ イ ゥ ウ ェ エ ォ オ カ ガ キ ギ ク グ ケ '
        self.assertFalse(vault.is_encrypted(data))

    def test_invalid_bytes_not_ascii(self):
        data = u'$ANSIBLE_VAULT;9.9;TEST\n%s' % u'ァ ア ィ イ ゥ ウ ェ エ ォ オ カ ガ キ ギ ク グ ケ '
        b_data = to_bytes(data, encoding='utf-8')
        self.assertFalse(vault.is_encrypted(b_data))

class TestVaultIsEncryptedFile(unittest.TestCase):

    def test_binary_file_handle_not_encrypted(self):
        b_data = b'foobar'
        b_data_fo = io.BytesIO(b_data)
        self.assertFalse(vault.is_encrypted_file(b_data_fo))

    def test_text_file_handle_not_encrypted(self):
        data = u'foobar'
        data_fo = io.StringIO(data)
        self.assertFalse(vault.is_encrypted_file(data_fo))

    def test_binary_file_handle_encrypted(self):
        b_data = b'$ANSIBLE_VAULT;9.9;TEST\n%s' % hexlify(b'ansible')
        b_data_fo = io.BytesIO(b_data)
        self.assertTrue(vault.is_encrypted_file(b_data_fo))

    def test_text_file_handle_encrypted(self):
        data = u'$ANSIBLE_VAULT;9.9;TEST\n%s' % to_text(hexlify(b'ansible'))
        data_fo = io.StringIO(data)
        self.assertTrue(vault.is_encrypted_file(data_fo))

    def test_binary_file_handle_invalid(self):
        data = u'$ANSIBLE_VAULT;9.9;TEST\n%s' % u'ァ ア ィ イ ゥ ウ ェ エ ォ オ カ ガ キ ギ ク グ ケ '
        b_data = to_bytes(data)
        b_data_fo = io.BytesIO(b_data)
        self.assertFalse(vault.is_encrypted_file(b_data_fo))

    def test_text_file_handle_invalid(self):
        data = u'$ANSIBLE_VAULT;9.9;TEST\n%s' % u'ァ ア ィ イ ゥ ウ ェ エ ォ オ カ ガ キ ギ ク グ ケ '
        data_fo = io.StringIO(data)
        self.assertFalse(vault.is_encrypted_file(data_fo))

    def test_file_already_read_from_finds_header(self):
        b_data = b'$ANSIBLE_VAULT;9.9;TEST\n%s' % hexlify(b'ansible\ntesting\nfile pos')
        b_data_fo = io.BytesIO(b_data)
        b_data_fo.read(42)
        self.assertTrue(vault.is_encrypted_file(b_data_fo))

    def test_file_already_read_from_saves_file_pos(self):
        b_data = b'$ANSIBLE_VAULT;9.9;TEST\n%s' % hexlify(b'ansible\ntesting\nfile pos')
        b_data_fo = io.BytesIO(b_data)
        b_data_fo.read(69)
        vault.is_encrypted_file(b_data_fo)
        self.assertEqual(b_data_fo.tell(), 69)

    def test_file_with_offset(self):
        b_data = b'JUNK$ANSIBLE_VAULT;9.9;TEST\n%s' % hexlify(b'ansible\ntesting\nfile pos')
        b_data_fo = io.BytesIO(b_data)
        self.assertTrue(vault.is_encrypted_file(b_data_fo, start_pos=4))

    def test_file_with_count(self):
        b_data = b'$ANSIBLE_VAULT;9.9;TEST\n%s' % hexlify(b'ansible\ntesting\nfile pos')
        vault_length = len(b_data)
        b_data = b_data + u'ァ ア'.encode('utf-8')
        b_data_fo = io.BytesIO(b_data)
        self.assertTrue(vault.is_encrypted_file(b_data_fo, count=vault_length))

    def test_file_with_offset_and_count(self):
        b_data = b'$ANSIBLE_VAULT;9.9;TEST\n%s' % hexlify(b'ansible\ntesting\nfile pos')
        vault_length = len(b_data)
        b_data = b'JUNK' + b_data + u'ァ ア'.encode('utf-8')
        b_data_fo = io.BytesIO(b_data)
        self.assertTrue(vault.is_encrypted_file(b_data_fo, start_pos=4, count=vault_length))

@pytest.mark.skipif(not vault.HAS_CRYPTOGRAPHY, reason='Skipping cryptography tests because cryptography is not installed')
class TestVaultCipherAes256(unittest.TestCase):

    def setUp(self):
        self.vault_cipher = vault.VaultAES256()

    def test(self):
        self.assertIsInstance(self.vault_cipher, vault.VaultAES256)

    def test_create_key_cryptography(self):
        b_password = b'hunter42'
        b_salt = os.urandom(32)
        b_key_cryptography = self.vault_cipher._create_key_cryptography(b_password, b_salt, key_length=32, iv_length=16)
        self.assertIsInstance(b_key_cryptography, six.binary_type)

    @pytest.mark.skipif(not vault.HAS_PYCRYPTO, reason='Not testing pycrypto key as pycrypto is not installed')
    def test_create_key_pycrypto(self):
        b_password = b'hunter42'
        b_salt = os.urandom(32)
        b_key_pycrypto = self.vault_cipher._create_key_pycrypto(b_password, b_salt, key_length=32, iv_length=16)
        self.assertIsInstance(b_key_pycrypto, six.binary_type)

    @pytest.mark.skipif(not vault.HAS_PYCRYPTO, reason='Not comparing cryptography key to pycrypto key as pycrypto is not installed')
    def test_compare_new_keys(self):
        b_password = b'hunter42'
        b_salt = os.urandom(32)
        b_key_cryptography = self.vault_cipher._create_key_cryptography(b_password, b_salt, key_length=32, iv_length=16)
        b_key_pycrypto = self.vault_cipher._create_key_pycrypto(b_password, b_salt, key_length=32, iv_length=16)
        self.assertEqual(b_key_cryptography, b_key_pycrypto)

    def test_create_key_known_cryptography(self):
        b_password = b'hunter42'
        b_salt = b'q' * 32
        b_key_1 = self.vault_cipher._create_key_cryptography(b_password, b_salt, key_length=32, iv_length=16)
        self.assertIsInstance(b_key_1, six.binary_type)
        b_key_2 = self.vault_cipher._create_key_cryptography(b_password, b_salt, key_length=32, iv_length=16)
        self.assertIsInstance(b_key_2, six.binary_type)
        self.assertEqual(b_key_1, b_key_2)
        b_key_3 = self.vault_cipher._create_key_pycrypto(b_password, b_salt, key_length=32, iv_length=16)
        self.assertIsInstance(b_key_3, six.binary_type)
        b_key_4 = self.vault_cipher._create_key_pycrypto(b_password, b_salt, key_length=32, iv_length=16)
        self.assertIsInstance(b_key_4, six.binary_type)
        self.assertEqual(b_key_3, b_key_4)
        self.assertEqual(b_key_1, b_key_4)

    def test_create_key_known_pycrypto(self):
        b_password = b'hunter42'
        b_salt = b'q' * 32
        b_key_3 = self.vault_cipher._create_key_pycrypto(b_password, b_salt, key_length=32, iv_length=16)
        self.assertIsInstance(b_key_3, six.binary_type)
        b_key_4 = self.vault_cipher._create_key_pycrypto(b_password, b_salt, key_length=32, iv_length=16)
        self.assertIsInstance(b_key_4, six.binary_type)
        self.assertEqual(b_key_3, b_key_4)

    def test_is_equal_is_equal(self):
        self.assertTrue(self.vault_cipher._is_equal(b'abcdefghijklmnopqrstuvwxyz', b'abcdefghijklmnopqrstuvwxyz'))

    def test_is_equal_unequal_length(self):
        self.assertFalse(self.vault_cipher._is_equal(b'abcdefghijklmnopqrstuvwxyz', b'abcdefghijklmnopqrstuvwx and sometimes y'))

    def test_is_equal_not_equal(self):
        self.assertFalse(self.vault_cipher._is_equal(b'abcdefghijklmnopqrstuvwxyz', b'AbcdefghijKlmnopQrstuvwxZ'))

    def test_is_equal_empty(self):
        self.assertTrue(self.vault_cipher._is_equal(b'', b''))

    def test_is_equal_non_ascii_equal(self):
        utf8_data = to_bytes(u'私はガラスを食べられます。それは私を傷つけません。')
        self.assertTrue(self.vault_cipher._is_equal(utf8_data, utf8_data))

    def test_is_equal_non_ascii_unequal(self):
        utf8_data = to_bytes(u'私はガラスを食べられます。それは私を傷つけません。')
        utf8_data2 = to_bytes(u'Pot să mănânc sticlă și ea nu mă rănește.')
        self.assertFalse(self.vault_cipher._is_equal(utf8_data, utf8_data2))
        self.assertFalse(self.vault_cipher._is_equal(utf8_data, utf8_data[:-1] + b'P'))

    def test_is_equal_non_bytes(self):
        """ Anything not a byte string should raise a TypeError """
        self.assertRaises(TypeError, self.vault_cipher._is_equal, u'One fish', b'two fish')
        self.assertRaises(TypeError, self.vault_cipher._is_equal, b'One fish', u'two fish')
        self.assertRaises(TypeError, self.vault_cipher._is_equal, 1, b'red fish')
        self.assertRaises(TypeError, self.vault_cipher._is_equal, b'blue fish', 2)

@pytest.mark.skipif(not vault.HAS_PYCRYPTO, reason='Skipping Pycrypto tests because pycrypto is not installed')
class TestVaultCipherAes256PyCrypto(TestVaultCipherAes256):

    def setUp(self):
        self.has_cryptography = vault.HAS_CRYPTOGRAPHY
        vault.HAS_CRYPTOGRAPHY = False
        super(TestVaultCipherAes256PyCrypto, self).setUp()

    def tearDown(self):
        vault.HAS_CRYPTOGRAPHY = self.has_cryptography
        super(TestVaultCipherAes256PyCrypto, self).tearDown()

class TestMatchSecrets(unittest.TestCase):

    def test_empty_tuple(self):
        secrets = [tuple()]
        vault_ids = ['vault_id_1']
        self.assertRaises(ValueError, vault.match_secrets, secrets, vault_ids)

    def test_empty_secrets(self):
        matches = vault.match_secrets([], ['vault_id_1'])
        self.assertEqual(matches, [])

    def test_single_match(self):
        secret = TextVaultSecret('password')
        matches = vault.match_secrets([('default', secret)], ['default'])
        self.assertEqual(matches, [('default', secret)])

    def test_no_matches(self):
        secret = TextVaultSecret('password')
        matches = vault.match_secrets([('default', secret)], ['not_default'])
        self.assertEqual(matches, [])

    def test_multiple_matches(self):
        secrets = [('vault_id1', TextVaultSecret('password1')), ('vault_id2', TextVaultSecret('password2')), ('vault_id1', TextVaultSecret('password3')), ('vault_id4', TextVaultSecret('password4'))]
        vault_ids = ['vault_id1', 'vault_id4']
        matches = vault.match_secrets(secrets, vault_ids)
        self.assertEqual(len(matches), 3)
        expected = [('vault_id1', TextVaultSecret('password1')), ('vault_id1', TextVaultSecret('password3')), ('vault_id4', TextVaultSecret('password4'))]
        self.assertEqual([x for (x, y) in matches], [a for (a, b) in expected])

@pytest.mark.skipif(not vault.HAS_CRYPTOGRAPHY, reason='Skipping cryptography tests because cryptography is not installed')
class TestVaultLib(unittest.TestCase):

    def setUp(self):
        self.vault_password = 'test-vault-password'
        text_secret = TextVaultSecret(self.vault_password)
        self.vault_secrets = [('default', text_secret), ('test_id', text_secret)]
        self.v = vault.VaultLib(self.vault_secrets)

    def _vault_secrets(self, vault_id, secret):
        return [(vault_id, secret)]

    def _vault_secrets_from_password(self, vault_id, password):
        return [(vault_id, TextVaultSecret(password))]

    def test_encrypt(self):
        plaintext = u'Some text to encrypt in a café'
        b_vaulttext = self.v.encrypt(plaintext)
        self.assertIsInstance(b_vaulttext, six.binary_type)
        b_header = b'$ANSIBLE_VAULT;1.1;AES256\n'
        self.assertEqual(b_vaulttext[:len(b_header)], b_header)

    def test_encrypt_vault_id(self):
        plaintext = u'Some text to encrypt in a café'
        b_vaulttext = self.v.encrypt(plaintext, vault_id='test_id')
        self.assertIsInstance(b_vaulttext, six.binary_type)
        b_header = b'$ANSIBLE_VAULT;1.2;AES256;test_id\n'
        self.assertEqual(b_vaulttext[:len(b_header)], b_header)

    def test_encrypt_bytes(self):
        plaintext = to_bytes(u'Some text to encrypt in a café')
        b_vaulttext = self.v.encrypt(plaintext)
        self.assertIsInstance(b_vaulttext, six.binary_type)
        b_header = b'$ANSIBLE_VAULT;1.1;AES256\n'
        self.assertEqual(b_vaulttext[:len(b_header)], b_header)

    def test_encrypt_no_secret_empty_secrets(self):
        vault_secrets = []
        v = vault.VaultLib(vault_secrets)
        plaintext = u'Some text to encrypt in a café'
        self.assertRaisesRegexp(vault.AnsibleVaultError, '.*A vault password must be specified to encrypt data.*', v.encrypt, plaintext)

    def test_format_vaulttext_envelope(self):
        cipher_name = 'TEST'
        b_ciphertext = b'ansible'
        b_vaulttext = vault.format_vaulttext_envelope(b_ciphertext, cipher_name, version=self.v.b_version, vault_id='default')
        b_lines = b_vaulttext.split(b'\n')
        self.assertGreater(len(b_lines), 1, msg='failed to properly add header')
        b_header = b_lines[0]
        b_header_parts = b_header.split(b';')
        self.assertEqual(len(b_header_parts), 4, msg='header has the wrong number of parts')
        self.assertEqual(b_header_parts[0], b'$ANSIBLE_VAULT', msg='header does not start with $ANSIBLE_VAULT')
        self.assertEqual(b_header_parts[1], self.v.b_version, msg='header version is incorrect')
        self.assertEqual(b_header_parts[2], b'TEST', msg='header does not end with cipher name')
        (b_ciphertext2, b_version2, cipher_name2, vault_id2) = vault.parse_vaulttext_envelope(b_vaulttext)
        self.assertEqual(b_ciphertext, b_ciphertext2)
        self.assertEqual(self.v.b_version, b_version2)
        self.assertEqual(cipher_name, cipher_name2)
        self.assertEqual('default', vault_id2)

    def test_parse_vaulttext_envelope(self):
        b_vaulttext = b'$ANSIBLE_VAULT;9.9;TEST\nansible'
        (b_ciphertext, b_version, cipher_name, vault_id) = vault.parse_vaulttext_envelope(b_vaulttext)
        b_lines = b_ciphertext.split(b'\n')
        self.assertEqual(b_lines[0], b'ansible', msg='Payload was not properly split from the header')
        self.assertEqual(cipher_name, u'TEST', msg='cipher name was not properly set')
        self.assertEqual(b_version, b'9.9', msg='version was not properly set')

    def test_parse_vaulttext_envelope_crlf(self):
        b_vaulttext = b'$ANSIBLE_VAULT;9.9;TEST\r\nansible'
        (b_ciphertext, b_version, cipher_name, vault_id) = vault.parse_vaulttext_envelope(b_vaulttext)
        b_lines = b_ciphertext.split(b'\n')
        self.assertEqual(b_lines[0], b'ansible', msg='Payload was not properly split from the header')
        self.assertEqual(cipher_name, u'TEST', msg='cipher name was not properly set')
        self.assertEqual(b_version, b'9.9', msg='version was not properly set')

    def test_encrypt_decrypt_aes256(self):
        self.v.cipher_name = u'AES256'
        plaintext = u'foobar'
        b_vaulttext = self.v.encrypt(plaintext)
        b_plaintext = self.v.decrypt(b_vaulttext)
        self.assertNotEqual(b_vaulttext, b'foobar', msg='encryption failed')
        self.assertEqual(b_plaintext, b'foobar', msg='decryption failed')

    def test_encrypt_decrypt_aes256_none_secrets(self):
        vault_secrets = self._vault_secrets_from_password('default', 'ansible')
        v = vault.VaultLib(vault_secrets)
        plaintext = u'foobar'
        b_vaulttext = v.encrypt(plaintext)
        v_none = vault.VaultLib(None)
        v_none.secrets = None
        self.assertRaisesRegexp(vault.AnsibleVaultError, '.*A vault password must be specified to decrypt data.*', v_none.decrypt, b_vaulttext)

    def test_encrypt_decrypt_aes256_empty_secrets(self):
        vault_secrets = self._vault_secrets_from_password('default', 'ansible')
        v = vault.VaultLib(vault_secrets)
        plaintext = u'foobar'
        b_vaulttext = v.encrypt(plaintext)
        vault_secrets_empty = []
        v_none = vault.VaultLib(vault_secrets_empty)
        self.assertRaisesRegexp(vault.AnsibleVaultError, '.*Attempting to decrypt but no vault secrets found.*', v_none.decrypt, b_vaulttext)

    def test_encrypt_decrypt_aes256_multiple_secrets_all_wrong(self):
        plaintext = u'Some text to encrypt in a café'
        b_vaulttext = self.v.encrypt(plaintext)
        vault_secrets = [('default', TextVaultSecret('another-wrong-password')), ('wrong-password', TextVaultSecret('wrong-password'))]
        v_multi = vault.VaultLib(vault_secrets)
        self.assertRaisesRegexp(errors.AnsibleError, '.*Decryption failed.*', v_multi.decrypt, b_vaulttext, filename='/dev/null/fake/filename')

    def test_encrypt_decrypt_aes256_multiple_secrets_one_valid(self):
        plaintext = u'Some text to encrypt in a café'
        b_vaulttext = self.v.encrypt(plaintext)
        correct_secret = TextVaultSecret(self.vault_password)
        wrong_secret = TextVaultSecret('wrong-password')
        vault_secrets = [('default', wrong_secret), ('corect_secret', correct_secret), ('wrong_secret', wrong_secret)]
        v_multi = vault.VaultLib(vault_secrets)
        b_plaintext = v_multi.decrypt(b_vaulttext)
        self.assertNotEqual(b_vaulttext, to_bytes(plaintext), msg='encryption failed')
        self.assertEqual(b_plaintext, to_bytes(plaintext), msg='decryption failed')

    def test_encrypt_decrypt_aes256_existing_vault(self):
        self.v.cipher_name = u'AES256'
        b_orig_plaintext = b'Setec Astronomy'
        vaulttext = u'$ANSIBLE_VAULT;1.1;AES256\n33363965326261303234626463623963633531343539616138316433353830356566396130353436\n3562643163366231316662386565383735653432386435610a306664636137376132643732393835\n63383038383730306639353234326630666539346233376330303938323639306661313032396437\n6233623062366136310a633866373936313238333730653739323461656662303864663666653563\n3138'
        b_plaintext = self.v.decrypt(vaulttext)
        self.assertEqual(b_plaintext, b_plaintext, msg='decryption failed')
        b_vaulttext = to_bytes(vaulttext, encoding='ascii', errors='strict')
        b_plaintext = self.v.decrypt(b_vaulttext)
        self.assertEqual(b_plaintext, b_orig_plaintext, msg='decryption failed')

    @pytest.mark.skip(reason='This test is not ready yet')
    def test_encrypt_decrypt_aes256_bad_hmac(self):
        self.v.cipher_name = 'AES256'
        enc_data = '$ANSIBLE_VAULT;1.1;AES256\n33363965326261303234626463623963633531343539616138316433353830356566396130353436\n3562643163366231316662386565383735653432386435610a306664636137376132643732393835\n63383038383730306639353234326630666539346233376330303938323639306661313032396437\n6233623062366136310a633866373936313238333730653739323461656662303864663666653563\n3138'
        b_data = to_bytes(enc_data, errors='strict', encoding='utf-8')
        b_data = self.v._split_header(b_data)
        foo = binascii.unhexlify(b_data)
        lines = foo.splitlines()
        b_salt = lines[0]
        b_hmac = lines[1]
        b_ciphertext_data = b'\n'.join(lines[2:])
        b_ciphertext = binascii.unhexlify(b_ciphertext_data)
        b_ciphertext_data = binascii.hexlify(b_ciphertext)
        b_payload = b'\n'.join([b_salt, b_hmac, b_ciphertext_data])
        b_invalid_ciphertext = self.v._format_output(b_payload)
        self.v.decrypt(b_invalid_ciphertext)

    def test_decrypt_and_get_vault_id(self):
        b_expected_plaintext = to_bytes('foo bar\n')
        vaulttext = '$ANSIBLE_VAULT;1.2;AES256;ansible_devel\n65616435333934613466373335363332373764363365633035303466643439313864663837393234\n3330656363343637313962633731333237313636633534630a386264363438363362326132363239\n39363166646664346264383934393935653933316263333838386362633534326664646166663736\n6462303664383765650a356637643633366663643566353036303162386237336233393065393164\n6264'
        vault_secrets = self._vault_secrets_from_password('ansible_devel', 'ansible')
        v = vault.VaultLib(vault_secrets)
        b_vaulttext = to_bytes(vaulttext)
        (b_plaintext, vault_id_used, vault_secret_used) = v.decrypt_and_get_vault_id(b_vaulttext)
        self.assertEqual(b_expected_plaintext, b_plaintext)
        self.assertEqual(vault_id_used, 'ansible_devel')
        self.assertEqual(vault_secret_used.text, 'ansible')

    def test_decrypt_non_default_1_2(self):
        b_expected_plaintext = to_bytes('foo bar\n')
        vaulttext = '$ANSIBLE_VAULT;1.2;AES256;ansible_devel\n65616435333934613466373335363332373764363365633035303466643439313864663837393234\n3330656363343637313962633731333237313636633534630a386264363438363362326132363239\n39363166646664346264383934393935653933316263333838386362633534326664646166663736\n6462303664383765650a356637643633366663643566353036303162386237336233393065393164\n6264'
        vault_secrets = self._vault_secrets_from_password('default', 'ansible')
        v = vault.VaultLib(vault_secrets)
        b_vaulttext = to_bytes(vaulttext)
        b_plaintext = v.decrypt(b_vaulttext)
        self.assertEqual(b_expected_plaintext, b_plaintext)
        (b_ciphertext, b_version, cipher_name, vault_id) = vault.parse_vaulttext_envelope(b_vaulttext)
        self.assertEqual('ansible_devel', vault_id)
        self.assertEqual(b'1.2', b_version)

    def test_decrypt_decrypted(self):
        plaintext = u'ansible'
        self.assertRaises(errors.AnsibleError, self.v.decrypt, plaintext)
        b_plaintext = b'ansible'
        self.assertRaises(errors.AnsibleError, self.v.decrypt, b_plaintext)

    def test_cipher_not_set(self):
        plaintext = u'ansible'
        self.v.encrypt(plaintext)
        self.assertEqual(self.v.cipher_name, 'AES256')

@pytest.mark.skipif(not vault.HAS_PYCRYPTO, reason='Skipping Pycrypto tests because pycrypto is not installed')
class TestVaultLibPyCrypto(TestVaultLib):

    def setUp(self):
        self.has_cryptography = vault.HAS_CRYPTOGRAPHY
        vault.HAS_CRYPTOGRAPHY = False
        super(TestVaultLibPyCrypto, self).setUp()

    def tearDown(self):
        vault.HAS_CRYPTOGRAPHY = self.has_cryptography
        super(TestVaultLibPyCrypto, self).tearDown()

def test_TestUnhexlify_test():
    ret = TestUnhexlify().test()

def test_TestUnhexlify_test_odd_length():
    ret = TestUnhexlify().test_odd_length()

def test_TestUnhexlify_test_nonhex():
    ret = TestUnhexlify().test_nonhex()

def test_TestParseVaulttext_test():
    ret = TestParseVaulttext().test()

def test_TestParseVaulttext_test_non_hex():
    ret = TestParseVaulttext().test_non_hex()

def test_TestVaultSecret_test():
    ret = TestVaultSecret().test()

def test_TestVaultSecret_test_bytes():
    ret = TestVaultSecret().test_bytes()

def test_TestPromptVaultSecret_test_empty_prompt_formats():
    ret = TestPromptVaultSecret().test_empty_prompt_formats()

def test_TestPromptVaultSecret_test_prompt_formats_none():
    ret = TestPromptVaultSecret().test_prompt_formats_none()

def test_TestPromptVaultSecret_test_custom_prompt():
    ret = TestPromptVaultSecret().test_custom_prompt()

def test_TestPromptVaultSecret_test_prompt_eoferror():
    ret = TestPromptVaultSecret().test_prompt_eoferror()

def test_TestPromptVaultSecret_test_prompt_passwords_dont_match():
    ret = TestPromptVaultSecret().test_prompt_passwords_dont_match()

def test_TestFileVaultSecret_setUp():
    ret = TestFileVaultSecret().setUp()

def test_TestFileVaultSecret_test():
    ret = TestFileVaultSecret().test()

def test_TestFileVaultSecret_test_repr_empty():
    ret = TestFileVaultSecret().test_repr_empty()

def test_TestFileVaultSecret_test_repr():
    ret = TestFileVaultSecret().test_repr()

def test_TestFileVaultSecret_test_empty_bytes():
    ret = TestFileVaultSecret().test_empty_bytes()

def test_TestFileVaultSecret_test_file():
    ret = TestFileVaultSecret().test_file()

def test_TestFileVaultSecret_test_file_empty():
    ret = TestFileVaultSecret().test_file_empty()

def test_TestFileVaultSecret_test_file_encrypted():
    ret = TestFileVaultSecret().test_file_encrypted()

def test_TestFileVaultSecret_test_file_not_a_directory():
    ret = TestFileVaultSecret().test_file_not_a_directory()

def test_TestFileVaultSecret_test_file_not_found():
    ret = TestFileVaultSecret().test_file_not_found()

def test_TestScriptVaultSecret_test():
    ret = TestScriptVaultSecret().test()

def test_TestScriptVaultSecret_communicate():
    ret = TestScriptVaultSecret().communicate()

def test_TestScriptVaultSecret__mock_popen():
    ret = TestScriptVaultSecret()._mock_popen()

def test_TestScriptVaultSecret_test_read_file():
    ret = TestScriptVaultSecret().test_read_file()

def test_TestScriptVaultSecret_test_read_file_empty():
    ret = TestScriptVaultSecret().test_read_file_empty()

def test_TestScriptVaultSecret_test_read_file_os_error():
    ret = TestScriptVaultSecret().test_read_file_os_error()

def test_TestScriptVaultSecret_test_read_file_not_executable():
    ret = TestScriptVaultSecret().test_read_file_not_executable()

def test_TestScriptVaultSecret_test_read_file_non_zero_return_code():
    ret = TestScriptVaultSecret().test_read_file_non_zero_return_code()

def test_TestScriptIsClient_test_randomname():
    ret = TestScriptIsClient().test_randomname()

def test_TestScriptIsClient_test_something_dash_client():
    ret = TestScriptIsClient().test_something_dash_client()

def test_TestScriptIsClient_test_something_dash_client_somethingelse():
    ret = TestScriptIsClient().test_something_dash_client_somethingelse()

def test_TestScriptIsClient_test_something_dash_client_py():
    ret = TestScriptIsClient().test_something_dash_client_py()

def test_TestScriptIsClient_test_full_path_something_dash_client_py():
    ret = TestScriptIsClient().test_full_path_something_dash_client_py()

def test_TestScriptIsClient_test_full_path_something_dash_client():
    ret = TestScriptIsClient().test_full_path_something_dash_client()

def test_TestScriptIsClient_test_full_path_something_dash_client_in_dir():
    ret = TestScriptIsClient().test_full_path_something_dash_client_in_dir()

def test_TestGetFileVaultSecret_test_file():
    ret = TestGetFileVaultSecret().test_file()

def test_TestGetFileVaultSecret_test_file_not_a_directory():
    ret = TestGetFileVaultSecret().test_file_not_a_directory()

def test_TestGetFileVaultSecret_test_file_not_found():
    ret = TestGetFileVaultSecret().test_file_not_found()

def test_TestVaultIsEncrypted_test_bytes_not_encrypted():
    ret = TestVaultIsEncrypted().test_bytes_not_encrypted()

def test_TestVaultIsEncrypted_test_bytes_encrypted():
    ret = TestVaultIsEncrypted().test_bytes_encrypted()

def test_TestVaultIsEncrypted_test_text_not_encrypted():
    ret = TestVaultIsEncrypted().test_text_not_encrypted()

def test_TestVaultIsEncrypted_test_text_encrypted():
    ret = TestVaultIsEncrypted().test_text_encrypted()

def test_TestVaultIsEncrypted_test_invalid_text_not_ascii():
    ret = TestVaultIsEncrypted().test_invalid_text_not_ascii()

def test_TestVaultIsEncrypted_test_invalid_bytes_not_ascii():
    ret = TestVaultIsEncrypted().test_invalid_bytes_not_ascii()

def test_TestVaultIsEncryptedFile_test_binary_file_handle_not_encrypted():
    ret = TestVaultIsEncryptedFile().test_binary_file_handle_not_encrypted()

def test_TestVaultIsEncryptedFile_test_text_file_handle_not_encrypted():
    ret = TestVaultIsEncryptedFile().test_text_file_handle_not_encrypted()

def test_TestVaultIsEncryptedFile_test_binary_file_handle_encrypted():
    ret = TestVaultIsEncryptedFile().test_binary_file_handle_encrypted()

def test_TestVaultIsEncryptedFile_test_text_file_handle_encrypted():
    ret = TestVaultIsEncryptedFile().test_text_file_handle_encrypted()

def test_TestVaultIsEncryptedFile_test_binary_file_handle_invalid():
    ret = TestVaultIsEncryptedFile().test_binary_file_handle_invalid()

def test_TestVaultIsEncryptedFile_test_text_file_handle_invalid():
    ret = TestVaultIsEncryptedFile().test_text_file_handle_invalid()

def test_TestVaultIsEncryptedFile_test_file_already_read_from_finds_header():
    ret = TestVaultIsEncryptedFile().test_file_already_read_from_finds_header()

def test_TestVaultIsEncryptedFile_test_file_already_read_from_saves_file_pos():
    ret = TestVaultIsEncryptedFile().test_file_already_read_from_saves_file_pos()

def test_TestVaultIsEncryptedFile_test_file_with_offset():
    ret = TestVaultIsEncryptedFile().test_file_with_offset()

def test_TestVaultIsEncryptedFile_test_file_with_count():
    ret = TestVaultIsEncryptedFile().test_file_with_count()

def test_TestVaultIsEncryptedFile_test_file_with_offset_and_count():
    ret = TestVaultIsEncryptedFile().test_file_with_offset_and_count()

def test_TestVaultCipherAes256_setUp():
    ret = TestVaultCipherAes256().setUp()

def test_TestVaultCipherAes256_test():
    ret = TestVaultCipherAes256().test()

def test_TestVaultCipherAes256_test_create_key_cryptography():
    ret = TestVaultCipherAes256().test_create_key_cryptography()

def test_TestVaultCipherAes256_test_create_key_pycrypto():
    ret = TestVaultCipherAes256().test_create_key_pycrypto()

def test_TestVaultCipherAes256_test_compare_new_keys():
    ret = TestVaultCipherAes256().test_compare_new_keys()

def test_TestVaultCipherAes256_test_create_key_known_cryptography():
    ret = TestVaultCipherAes256().test_create_key_known_cryptography()

def test_TestVaultCipherAes256_test_create_key_known_pycrypto():
    ret = TestVaultCipherAes256().test_create_key_known_pycrypto()

def test_TestVaultCipherAes256_test_is_equal_is_equal():
    ret = TestVaultCipherAes256().test_is_equal_is_equal()

def test_TestVaultCipherAes256_test_is_equal_unequal_length():
    ret = TestVaultCipherAes256().test_is_equal_unequal_length()

def test_TestVaultCipherAes256_test_is_equal_not_equal():
    ret = TestVaultCipherAes256().test_is_equal_not_equal()

def test_TestVaultCipherAes256_test_is_equal_empty():
    ret = TestVaultCipherAes256().test_is_equal_empty()

def test_TestVaultCipherAes256_test_is_equal_non_ascii_equal():
    ret = TestVaultCipherAes256().test_is_equal_non_ascii_equal()

def test_TestVaultCipherAes256_test_is_equal_non_ascii_unequal():
    ret = TestVaultCipherAes256().test_is_equal_non_ascii_unequal()

def test_TestVaultCipherAes256_test_is_equal_non_bytes():
    ret = TestVaultCipherAes256().test_is_equal_non_bytes()

def test_TestVaultCipherAes256PyCrypto_setUp():
    ret = TestVaultCipherAes256PyCrypto().setUp()

def test_TestVaultCipherAes256PyCrypto_tearDown():
    ret = TestVaultCipherAes256PyCrypto().tearDown()

def test_TestMatchSecrets_test_empty_tuple():
    ret = TestMatchSecrets().test_empty_tuple()

def test_TestMatchSecrets_test_empty_secrets():
    ret = TestMatchSecrets().test_empty_secrets()

def test_TestMatchSecrets_test_single_match():
    ret = TestMatchSecrets().test_single_match()

def test_TestMatchSecrets_test_no_matches():
    ret = TestMatchSecrets().test_no_matches()

def test_TestMatchSecrets_test_multiple_matches():
    ret = TestMatchSecrets().test_multiple_matches()

def test_TestVaultLib_setUp():
    ret = TestVaultLib().setUp()

def test_TestVaultLib__vault_secrets():
    ret = TestVaultLib()._vault_secrets()

def test_TestVaultLib__vault_secrets_from_password():
    ret = TestVaultLib()._vault_secrets_from_password()

def test_TestVaultLib_test_encrypt():
    ret = TestVaultLib().test_encrypt()

def test_TestVaultLib_test_encrypt_vault_id():
    ret = TestVaultLib().test_encrypt_vault_id()

def test_TestVaultLib_test_encrypt_bytes():
    ret = TestVaultLib().test_encrypt_bytes()

def test_TestVaultLib_test_encrypt_no_secret_empty_secrets():
    ret = TestVaultLib().test_encrypt_no_secret_empty_secrets()

def test_TestVaultLib_test_format_vaulttext_envelope():
    ret = TestVaultLib().test_format_vaulttext_envelope()

def test_TestVaultLib_test_parse_vaulttext_envelope():
    ret = TestVaultLib().test_parse_vaulttext_envelope()

def test_TestVaultLib_test_parse_vaulttext_envelope_crlf():
    ret = TestVaultLib().test_parse_vaulttext_envelope_crlf()

def test_TestVaultLib_test_encrypt_decrypt_aes256():
    ret = TestVaultLib().test_encrypt_decrypt_aes256()

def test_TestVaultLib_test_encrypt_decrypt_aes256_none_secrets():
    ret = TestVaultLib().test_encrypt_decrypt_aes256_none_secrets()

def test_TestVaultLib_test_encrypt_decrypt_aes256_empty_secrets():
    ret = TestVaultLib().test_encrypt_decrypt_aes256_empty_secrets()

def test_TestVaultLib_test_encrypt_decrypt_aes256_multiple_secrets_all_wrong():
    ret = TestVaultLib().test_encrypt_decrypt_aes256_multiple_secrets_all_wrong()

def test_TestVaultLib_test_encrypt_decrypt_aes256_multiple_secrets_one_valid():
    ret = TestVaultLib().test_encrypt_decrypt_aes256_multiple_secrets_one_valid()

def test_TestVaultLib_test_encrypt_decrypt_aes256_existing_vault():
    ret = TestVaultLib().test_encrypt_decrypt_aes256_existing_vault()

def test_TestVaultLib_test_encrypt_decrypt_aes256_bad_hmac():
    ret = TestVaultLib().test_encrypt_decrypt_aes256_bad_hmac()

def test_TestVaultLib_test_decrypt_and_get_vault_id():
    ret = TestVaultLib().test_decrypt_and_get_vault_id()

def test_TestVaultLib_test_decrypt_non_default_1_2():
    ret = TestVaultLib().test_decrypt_non_default_1_2()

def test_TestVaultLib_test_decrypt_decrypted():
    ret = TestVaultLib().test_decrypt_decrypted()

def test_TestVaultLib_test_cipher_not_set():
    ret = TestVaultLib().test_cipher_not_set()

def test_TestVaultLibPyCrypto_setUp():
    ret = TestVaultLibPyCrypto().setUp()

def test_TestVaultLibPyCrypto_tearDown():
    ret = TestVaultLibPyCrypto().tearDown()