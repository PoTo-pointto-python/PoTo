from __future__ import absolute_import, division, print_function
__metaclass__ = type
import os
import json
import pytest
from datetime import date, datetime
from pytz import timezone as tz
from ansible.module_utils.common._collections_compat import Mapping
from ansible.parsing.ajson import AnsibleJSONEncoder, AnsibleJSONDecoder
from ansible.parsing.yaml.objects import AnsibleVaultEncryptedUnicode
from ansible.utils.unsafe_proxy import AnsibleUnsafeText

def test_AnsibleJSONDecoder_vault():
    with open(os.path.join(os.path.dirname(__file__), 'fixtures/ajson.json')) as f:
        data = json.load(f, cls=AnsibleJSONDecoder)
    assert isinstance(data['password'], AnsibleVaultEncryptedUnicode)
    assert isinstance(data['bar']['baz'][0]['password'], AnsibleVaultEncryptedUnicode)
    assert isinstance(data['foo']['password'], AnsibleVaultEncryptedUnicode)

def test_encode_decode_unsafe():
    data = {'key_value': AnsibleUnsafeText(u'{#NOTACOMMENT#}'), 'list': [AnsibleUnsafeText(u'{#NOTACOMMENT#}')], 'list_dict': [{'key_value': AnsibleUnsafeText(u'{#NOTACOMMENT#}')}]}
    json_expected = '{"key_value": {"__ansible_unsafe": "{#NOTACOMMENT#}"}, "list": [{"__ansible_unsafe": "{#NOTACOMMENT#}"}], "list_dict": [{"key_value": {"__ansible_unsafe": "{#NOTACOMMENT#}"}}]}'
    assert json.dumps(data, cls=AnsibleJSONEncoder, preprocess_unsafe=True, sort_keys=True) == json_expected
    assert json.loads(json_expected, cls=AnsibleJSONDecoder) == data

def vault_data():
    """
    Prepare AnsibleVaultEncryptedUnicode test data for AnsibleJSONEncoder.default().

    Return a list of tuples (input, expected).
    """
    with open(os.path.join(os.path.dirname(__file__), 'fixtures/ajson.json')) as f:
        data = json.load(f, cls=AnsibleJSONDecoder)
    data_0 = data['password']
    data_1 = data['bar']['baz'][0]['password']
    expected_0 = u'$ANSIBLE_VAULT;1.1;AES256\n34646264306632313333393636316562356435376162633631326264383934326565333633366238\n3863373264326461623132613931346165636465346337310a326434313830316337393263616439\n64653937313463396366633861363266633465663730303633323534363331316164623237363831\n3536333561393238370a313330316263373938326162386433313336613532653538376662306435\n3339\n'
    expected_1 = u'$ANSIBLE_VAULT;1.1;AES256\n34646264306632313333393636316562356435376162633631326264383934326565333633366238\n3863373264326461623132613931346165636465346337310a326434313830316337393263616439\n64653937313463396366633861363266633465663730303633323534363331316164623237363831\n3536333561393238370a313330316263373938326162386433313336613532653538376662306435\n3338\n'
    return [(data_0, expected_0), (data_1, expected_1)]

class TestAnsibleJSONEncoder:
    """
    Namespace for testing AnsibleJSONEncoder.
    """

    @pytest.fixture(scope='class')
    def mapping(self, request):
        """
        Returns object of Mapping mock class.

        The object is used for testing handling of Mapping objects
        in AnsibleJSONEncoder.default().
        Using a plain dictionary instead is not suitable because
        it is handled by default encoder of the superclass (json.JSONEncoder).
        """

        class M(Mapping):
            """Mock mapping class."""

            def __init__(self, *args, **kwargs):
                self.__dict__.update(*args, **kwargs)

            def __getitem__(self, key):
                return self.__dict__[key]

            def __iter__(self):
                return iter(self.__dict__)

            def __len__(self):
                return len(self.__dict__)
        return M(request.param)

    @pytest.fixture
    def ansible_json_encoder(self):
        """Return AnsibleJSONEncoder object."""
        return AnsibleJSONEncoder()

    @pytest.mark.parametrize('test_input,expected', [(datetime(2019, 5, 14, 13, 39, 38, 569047), '2019-05-14T13:39:38.569047'), (datetime(2019, 5, 14, 13, 47, 16, 923866), '2019-05-14T13:47:16.923866'), (date(2019, 5, 14), '2019-05-14'), (date(2020, 5, 14), '2020-05-14'), (datetime(2019, 6, 15, 14, 45, tzinfo=tz('UTC')), '2019-06-15T14:45:00+00:00'), (datetime(2019, 6, 15, 14, 45, tzinfo=tz('Europe/Helsinki')), '2019-06-15T14:45:00+01:40')])
    def test_date_datetime(self, ansible_json_encoder, test_input, expected):
        (test_input, expected) = (datetime(2019, 5, 14, 13, 39, 38, 569047), '2019-05-14T13:39:38.569047')
        ansible_json_encoder = ansible_json_encoder()
        '\n        Test for passing datetime.date or datetime.datetime objects to AnsibleJSONEncoder.default().\n        '
        assert ansible_json_encoder.default(test_input) == expected

    @pytest.mark.parametrize('mapping,expected', [({1: 1}, {1: 1}), ({2: 2}, {2: 2}), ({1: 2}, {1: 2}), ({2: 1}, {2: 1})], indirect=['mapping'])
    def test_mapping(self, ansible_json_encoder, mapping, expected):
        (mapping, expected) = ({1: 1}, {1: 1})
        ansible_json_encoder = ansible_json_encoder()
        mapping = mapping()
        '\n        Test for passing Mapping object to AnsibleJSONEncoder.default().\n        '
        assert ansible_json_encoder.default(mapping) == expected

    @pytest.mark.parametrize('test_input,expected', vault_data())
    def test_ansible_json_decoder_vault(self, ansible_json_encoder, test_input, expected):
        (test_input, expected) = vault_data()[0]
        ansible_json_encoder = ansible_json_encoder()
        '\n        Test for passing AnsibleVaultEncryptedUnicode to AnsibleJSONEncoder.default().\n        '
        assert ansible_json_encoder.default(test_input) == {'__ansible_vault': expected}
        assert json.dumps(test_input, cls=AnsibleJSONEncoder, preprocess_unsafe=True) == '{"__ansible_vault": "%s"}' % expected.replace('\n', '\\n')

    @pytest.mark.parametrize('test_input,expected', [({1: 'first'}, {1: 'first'}), ({2: 'second'}, {2: 'second'})])
    def test_default_encoder(self, ansible_json_encoder, test_input, expected):
        (test_input, expected) = ({1: 'first'}, {1: 'first'})
        ansible_json_encoder = ansible_json_encoder()
        "\n        Test for the default encoder of AnsibleJSONEncoder.default().\n\n        If objects of different classes that are not tested above were passed,\n        AnsibleJSONEncoder.default() invokes 'default()' method of json.JSONEncoder superclass.\n        "
        assert ansible_json_encoder.default(test_input) == expected

    @pytest.mark.parametrize('test_input', [1, 1.1, 'string', [1, 2], set('set'), True, None])
    def test_default_encoder_unserializable(self, ansible_json_encoder, test_input):
        test_input = 1
        ansible_json_encoder = ansible_json_encoder()
        "\n        Test for the default encoder of AnsibleJSONEncoder.default(), not serializable objects.\n\n        It must fail with TypeError 'object is not serializable'.\n        "
        with pytest.raises(TypeError):
            ansible_json_encoder.default(test_input)

def test_TestAnsibleJSONEncoder_mapping():
    ret = TestAnsibleJSONEncoder().mapping()

def test_TestAnsibleJSONEncoder_ansible_json_encoder():
    ret = TestAnsibleJSONEncoder().ansible_json_encoder()

def test_TestAnsibleJSONEncoder_test_date_datetime():
    ret = TestAnsibleJSONEncoder().test_date_datetime()

def test_TestAnsibleJSONEncoder_test_mapping():
    ret = TestAnsibleJSONEncoder().test_mapping()

def test_TestAnsibleJSONEncoder_test_ansible_json_decoder_vault():
    ret = TestAnsibleJSONEncoder().test_ansible_json_decoder_vault()

def test_TestAnsibleJSONEncoder_test_default_encoder():
    ret = TestAnsibleJSONEncoder().test_default_encoder()

def test_TestAnsibleJSONEncoder_test_default_encoder_unserializable():
    ret = TestAnsibleJSONEncoder().test_default_encoder_unserializable()

def test_M___getitem__():
    ret = M().__getitem__()

def test_M___iter__():
    ret = M().__iter__()

def test_M___len__():
    ret = M().__len__()