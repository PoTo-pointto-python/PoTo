from __future__ import absolute_import, division, print_function
__metaclass__ = type
import itertools
import pytest
from ansible.module_utils.six import PY3
from ansible.module_utils.common.text.converters import to_text, to_bytes, to_native
from ansible.utils.unsafe_proxy import AnsibleUnsafeBytes, AnsibleUnsafeText
VALID_STRINGS = ((b'abcde', u'abcde', 'ascii'), (b'caf\xc3\xa9', u'café', 'utf-8'), (b'caf\xe9', u'café', 'latin-1'), (b'\xe3\x81\x8f\xe3\x82\x89\xe3\x81\xa8\xe3\x81\xbf', u'くらとみ', 'utf-8'), (b'\x82\xad\x82\xe7\x82\xc6\x82\xdd', u'くらとみ', 'shift-jis'))

@pytest.mark.parametrize('in_string, encoding, expected', itertools.chain(((d[0], d[2], d[1]) for d in VALID_STRINGS), ((d[1], d[2], d[1]) for d in VALID_STRINGS)))
def test_to_text(in_string, encoding, expected):
    (in_string,  encoding,  expected) = itertools.chain(((d[0], d[2], d[1]) for d in VALID_STRINGS), ((d[1], d[2], d[1]) for d in VALID_STRINGS))[0]
    'test happy path of decoding to text'
    assert to_text(in_string, encoding) == expected

@pytest.mark.parametrize('in_string, encoding, expected', itertools.chain(((d[0], d[2], d[0]) for d in VALID_STRINGS), ((d[1], d[2], d[0]) for d in VALID_STRINGS)))
def test_to_bytes(in_string, encoding, expected):
    (in_string,  encoding,  expected) = itertools.chain(((d[0], d[2], d[0]) for d in VALID_STRINGS), ((d[1], d[2], d[0]) for d in VALID_STRINGS))[0]
    'test happy path of encoding to bytes'
    assert to_bytes(in_string, encoding) == expected

@pytest.mark.parametrize('in_string, encoding, expected', itertools.chain(((d[0], d[2], d[1] if PY3 else d[0]) for d in VALID_STRINGS), ((d[1], d[2], d[1] if PY3 else d[0]) for d in VALID_STRINGS)))
def test_to_native(in_string, encoding, expected):
    (in_string,  encoding,  expected) = itertools.chain(((d[0], d[2], d[1] if PY3 else d[0]) for d in VALID_STRINGS), ((d[1], d[2], d[1] if PY3 else d[0]) for d in VALID_STRINGS))[0]
    'test happy path of encoding to native strings'
    assert to_native(in_string, encoding) == expected

def test_to_text_unsafe():
    assert isinstance(to_text(AnsibleUnsafeBytes(b'foo')), AnsibleUnsafeText)
    assert to_text(AnsibleUnsafeBytes(b'foo')) == AnsibleUnsafeText(u'foo')

def test_to_bytes_unsafe():
    assert isinstance(to_bytes(AnsibleUnsafeText(u'foo')), AnsibleUnsafeBytes)
    assert to_bytes(AnsibleUnsafeText(u'foo')) == AnsibleUnsafeBytes(b'foo')