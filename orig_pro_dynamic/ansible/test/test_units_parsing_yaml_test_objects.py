from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat import unittest
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native
from ansible.parsing import vault
from ansible.parsing.yaml.loader import AnsibleLoader
from ansible.parsing.yaml import objects
from units.mock.yaml_helper import YamlTestUtils
from units.mock.vault_helper import TextVaultSecret

class TestAnsibleVaultUnicodeNoVault(unittest.TestCase, YamlTestUtils):

    def test_empty_init(self):
        self.assertRaises(TypeError, objects.AnsibleVaultEncryptedUnicode)

    def test_empty_string_init(self):
        seq = ''.encode('utf8')
        self.assert_values(seq)

    def test_empty_byte_string_init(self):
        seq = b''
        self.assert_values(seq)

    def _assert_values(self, avu, seq):
        self.assertIsInstance(avu, objects.AnsibleVaultEncryptedUnicode)
        self.assertTrue(avu.vault is None)
        self.assertNotEquals(avu, seq)

    def assert_values(self, seq):
        avu = objects.AnsibleVaultEncryptedUnicode(seq)
        self._assert_values(avu, seq)

    def test_single_char(self):
        seq = 'a'.encode('utf8')
        self.assert_values(seq)

    def test_string(self):
        seq = 'some letters'
        self.assert_values(seq)

    def test_byte_string(self):
        seq = 'some letters'.encode('utf8')
        self.assert_values(seq)

class TestAnsibleVaultEncryptedUnicode(unittest.TestCase, YamlTestUtils):

    def setUp(self):
        self.good_vault_password = 'hunter42'
        good_vault_secret = TextVaultSecret(self.good_vault_password)
        self.good_vault_secrets = [('good_vault_password', good_vault_secret)]
        self.good_vault = vault.VaultLib(self.good_vault_secrets)
        self.wrong_vault_password = 'not-hunter42'
        wrong_vault_secret = TextVaultSecret(self.wrong_vault_password)
        self.wrong_vault_secrets = [('wrong_vault_password', wrong_vault_secret)]
        self.wrong_vault = vault.VaultLib(self.wrong_vault_secrets)
        self.vault = self.good_vault
        self.vault_secrets = self.good_vault_secrets

    def _loader(self, stream):
        return AnsibleLoader(stream, vault_secrets=self.vault_secrets)

    def test_dump_load_cycle(self):
        aveu = self._from_plaintext('the test string for TestAnsibleVaultEncryptedUnicode.test_dump_load_cycle')
        self._dump_load_cycle(aveu)

    def assert_values(self, avu, seq):
        self.assertIsInstance(avu, objects.AnsibleVaultEncryptedUnicode)
        self.assertEqual(avu, seq)
        self.assertTrue(avu.vault is self.vault)
        self.assertIsInstance(avu.vault, vault.VaultLib)

    def _from_plaintext(self, seq):
        id_secret = vault.match_encrypt_secret(self.good_vault_secrets)
        return objects.AnsibleVaultEncryptedUnicode.from_plaintext(seq, vault=self.vault, secret=id_secret[1])

    def _from_ciphertext(self, ciphertext):
        avu = objects.AnsibleVaultEncryptedUnicode(ciphertext)
        avu.vault = self.vault
        return avu

    def test_empty_init(self):
        self.assertRaises(TypeError, objects.AnsibleVaultEncryptedUnicode)

    def test_empty_string_init_from_plaintext(self):
        seq = ''
        avu = self._from_plaintext(seq)
        self.assert_values(avu, seq)

    def test_empty_unicode_init_from_plaintext(self):
        seq = u''
        avu = self._from_plaintext(seq)
        self.assert_values(avu, seq)

    def test_string_from_plaintext(self):
        seq = 'some letters'
        avu = self._from_plaintext(seq)
        self.assert_values(avu, seq)

    def test_unicode_from_plaintext(self):
        seq = u'some letters'
        avu = self._from_plaintext(seq)
        self.assert_values(avu, seq)

    def test_unicode_from_plaintext_encode(self):
        seq = u'some text here'
        avu = self._from_plaintext(seq)
        b_avu = avu.encode('utf-8', 'strict')
        self.assertIsInstance(avu, objects.AnsibleVaultEncryptedUnicode)
        self.assertEqual(b_avu, seq.encode('utf-8', 'strict'))
        self.assertTrue(avu.vault is self.vault)
        self.assertIsInstance(avu.vault, vault.VaultLib)

    def test_empty_string_wrong_password(self):
        seq = ''
        self.vault = self.wrong_vault
        avu = self._from_plaintext(seq)

        def compare(avu, seq):
            return avu == seq
        self.assertRaises(AnsibleError, compare, avu, seq)

    def test_vaulted_utf8_value_37258(self):
        seq = u'aöffü'
        avu = self._from_plaintext(seq)
        self.assert_values(avu, seq)

    def test_str_vaulted_utf8_value_37258(self):
        seq = u'aöffü'
        avu = self._from_plaintext(seq)
        assert str(avu) == to_native(seq)

def test_TestAnsibleVaultUnicodeNoVault_test_empty_init():
    ret = TestAnsibleVaultUnicodeNoVault().test_empty_init()

def test_TestAnsibleVaultUnicodeNoVault_test_empty_string_init():
    ret = TestAnsibleVaultUnicodeNoVault().test_empty_string_init()

def test_TestAnsibleVaultUnicodeNoVault_test_empty_byte_string_init():
    ret = TestAnsibleVaultUnicodeNoVault().test_empty_byte_string_init()

def test_TestAnsibleVaultUnicodeNoVault__assert_values():
    ret = TestAnsibleVaultUnicodeNoVault()._assert_values()

def test_TestAnsibleVaultUnicodeNoVault_assert_values():
    ret = TestAnsibleVaultUnicodeNoVault().assert_values()

def test_TestAnsibleVaultUnicodeNoVault_test_single_char():
    ret = TestAnsibleVaultUnicodeNoVault().test_single_char()

def test_TestAnsibleVaultUnicodeNoVault_test_string():
    ret = TestAnsibleVaultUnicodeNoVault().test_string()

def test_TestAnsibleVaultUnicodeNoVault_test_byte_string():
    ret = TestAnsibleVaultUnicodeNoVault().test_byte_string()

def test_TestAnsibleVaultEncryptedUnicode_setUp():
    ret = TestAnsibleVaultEncryptedUnicode().setUp()

def test_TestAnsibleVaultEncryptedUnicode__loader():
    ret = TestAnsibleVaultEncryptedUnicode()._loader()

def test_TestAnsibleVaultEncryptedUnicode_test_dump_load_cycle():
    ret = TestAnsibleVaultEncryptedUnicode().test_dump_load_cycle()

def test_TestAnsibleVaultEncryptedUnicode_assert_values():
    ret = TestAnsibleVaultEncryptedUnicode().assert_values()

def test_TestAnsibleVaultEncryptedUnicode__from_plaintext():
    ret = TestAnsibleVaultEncryptedUnicode()._from_plaintext()

def test_TestAnsibleVaultEncryptedUnicode__from_ciphertext():
    ret = TestAnsibleVaultEncryptedUnicode()._from_ciphertext()

def test_TestAnsibleVaultEncryptedUnicode_test_empty_init():
    ret = TestAnsibleVaultEncryptedUnicode().test_empty_init()

def test_TestAnsibleVaultEncryptedUnicode_test_empty_string_init_from_plaintext():
    ret = TestAnsibleVaultEncryptedUnicode().test_empty_string_init_from_plaintext()

def test_TestAnsibleVaultEncryptedUnicode_test_empty_unicode_init_from_plaintext():
    ret = TestAnsibleVaultEncryptedUnicode().test_empty_unicode_init_from_plaintext()

def test_TestAnsibleVaultEncryptedUnicode_test_string_from_plaintext():
    ret = TestAnsibleVaultEncryptedUnicode().test_string_from_plaintext()

def test_TestAnsibleVaultEncryptedUnicode_test_unicode_from_plaintext():
    ret = TestAnsibleVaultEncryptedUnicode().test_unicode_from_plaintext()

def test_TestAnsibleVaultEncryptedUnicode_test_unicode_from_plaintext_encode():
    ret = TestAnsibleVaultEncryptedUnicode().test_unicode_from_plaintext_encode()

def test_TestAnsibleVaultEncryptedUnicode_compare():
    ret = TestAnsibleVaultEncryptedUnicode().compare()

def test_TestAnsibleVaultEncryptedUnicode_test_empty_string_wrong_password():
    ret = TestAnsibleVaultEncryptedUnicode().test_empty_string_wrong_password()

def test_TestAnsibleVaultEncryptedUnicode_test_vaulted_utf8_value_37258():
    ret = TestAnsibleVaultEncryptedUnicode().test_vaulted_utf8_value_37258()

def test_TestAnsibleVaultEncryptedUnicode_test_str_vaulted_utf8_value_37258():
    ret = TestAnsibleVaultEncryptedUnicode().test_str_vaulted_utf8_value_37258()