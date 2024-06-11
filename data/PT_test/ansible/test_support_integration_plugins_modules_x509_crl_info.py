from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: x509_crl_info\nversion_added: "2.10"\nshort_description: Retrieve information on Certificate Revocation Lists (CRLs)\ndescription:\n    - This module allows one to retrieve information on Certificate Revocation Lists (CRLs).\nrequirements:\n    - cryptography >= 1.2\nauthor:\n    - Felix Fontein (@felixfontein)\noptions:\n    path:\n        description:\n            - Remote absolute path where the generated CRL file should be created or is already located.\n            - Either I(path) or I(content) must be specified, but not both.\n        type: path\n    content:\n        description:\n            - Content of the X.509 certificate in PEM format.\n            - Either I(path) or I(content) must be specified, but not both.\n        type: str\n\nnotes:\n    - All timestamp values are provided in ASN.1 TIME format, i.e. following the C(YYYYMMDDHHMMSSZ) pattern.\n      They are all in UTC.\nseealso:\n    - module: x509_crl\n'
EXAMPLES = '\n- name: Get information on CRL\n  x509_crl_info:\n    path: /etc/ssl/my-ca.crl\n  register: result\n\n- debug:\n    msg: "{{ result }}"\n'
RETURN = '\nissuer:\n    description:\n        - The CRL\'s issuer.\n        - Note that for repeated values, only the last one will be returned.\n    returned: success\n    type: dict\n    sample: \'{"organizationName": "Ansible", "commonName": "ca.example.com"}\'\nissuer_ordered:\n    description: The CRL\'s issuer as an ordered list of tuples.\n    returned: success\n    type: list\n    elements: list\n    sample: \'[["organizationName", "Ansible"], ["commonName": "ca.example.com"]]\'\nlast_update:\n    description: The point in time from which this CRL can be trusted as ASN.1 TIME.\n    returned: success\n    type: str\n    sample: 20190413202428Z\nnext_update:\n    description: The point in time from which a new CRL will be issued and the client has to check for it as ASN.1 TIME.\n    returned: success\n    type: str\n    sample: 20190413202428Z\ndigest:\n    description: The signature algorithm used to sign the CRL.\n    returned: success\n    type: str\n    sample: sha256WithRSAEncryption\nrevoked_certificates:\n    description: List of certificates to be revoked.\n    returned: success\n    type: list\n    elements: dict\n    contains:\n        serial_number:\n            description: Serial number of the certificate.\n            type: int\n            sample: 1234\n        revocation_date:\n            description: The point in time the certificate was revoked as ASN.1 TIME.\n            type: str\n            sample: 20190413202428Z\n        issuer:\n            description: The certificate\'s issuer.\n            type: list\n            elements: str\n            sample: \'["DNS:ca.example.org"]\'\n        issuer_critical:\n            description: Whether the certificate issuer extension is critical.\n            type: bool\n            sample: no\n        reason:\n            description:\n                - The value for the revocation reason extension.\n                - One of C(unspecified), C(key_compromise), C(ca_compromise), C(affiliation_changed), C(superseded),\n                  C(cessation_of_operation), C(certificate_hold), C(privilege_withdrawn), C(aa_compromise), and\n                  C(remove_from_crl).\n            type: str\n            sample: key_compromise\n        reason_critical:\n            description: Whether the revocation reason extension is critical.\n            type: bool\n            sample: no\n        invalidity_date:\n            description: |\n                The point in time it was known/suspected that the private key was compromised\n                or that the certificate otherwise became invalid as ASN.1 TIME.\n            type: str\n            sample: 20190413202428Z\n        invalidity_date_critical:\n            description: Whether the invalidity date extension is critical.\n            type: bool\n            sample: no\n'
import traceback
from distutils.version import LooseVersion
from ansible.module_utils import crypto as crypto_utils
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
MINIMAL_CRYPTOGRAPHY_VERSION = '1.2'
CRYPTOGRAPHY_IMP_ERR = None
try:
    import cryptography
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_VERSION = LooseVersion(cryptography.__version__)
except ImportError:
    CRYPTOGRAPHY_IMP_ERR = traceback.format_exc()
    CRYPTOGRAPHY_FOUND = False
else:
    CRYPTOGRAPHY_FOUND = True
TIMESTAMP_FORMAT = '%Y%m%d%H%M%SZ'

class CRLError(crypto_utils.OpenSSLObjectError):
    pass

class CRLInfo(crypto_utils.OpenSSLObject):
    """The main module implementation."""

    def __init__(self, module):
        super(CRLInfo, self).__init__(module.params['path'] or '', 'present', False, module.check_mode)
        self.content = module.params['content']
        self.module = module
        self.crl = None
        if self.content is None:
            try:
                with open(self.path, 'rb') as f:
                    data = f.read()
            except Exception as e:
                self.module.fail_json(msg='Error while reading CRL file from disk: {0}'.format(e))
        else:
            data = self.content.encode('utf-8')
        try:
            self.crl = x509.load_pem_x509_crl(data, default_backend())
        except Exception as e:
            self.module.fail_json(msg='Error while decoding CRL: {0}'.format(e))

    def _dump_revoked(self, entry):
        return {'serial_number': entry['serial_number'], 'revocation_date': entry['revocation_date'].strftime(TIMESTAMP_FORMAT), 'issuer': [crypto_utils.cryptography_decode_name(issuer) for issuer in entry['issuer']] if entry['issuer'] is not None else None, 'issuer_critical': entry['issuer_critical'], 'reason': crypto_utils.REVOCATION_REASON_MAP_INVERSE.get(entry['reason']) if entry['reason'] is not None else None, 'reason_critical': entry['reason_critical'], 'invalidity_date': entry['invalidity_date'].strftime(TIMESTAMP_FORMAT) if entry['invalidity_date'] is not None else None, 'invalidity_date_critical': entry['invalidity_date_critical']}

    def get_info(self):
        result = {'changed': False, 'last_update': None, 'next_update': None, 'digest': None, 'issuer_ordered': None, 'issuer': None, 'revoked_certificates': []}
        result['last_update'] = self.crl.last_update.strftime(TIMESTAMP_FORMAT)
        result['next_update'] = self.crl.next_update.strftime(TIMESTAMP_FORMAT)
        try:
            result['digest'] = crypto_utils.cryptography_oid_to_name(self.crl.signature_algorithm_oid)
        except AttributeError:
            dotted = crypto_utils._obj2txt(self.crl._backend._lib, self.crl._backend._ffi, self.crl._x509_crl.sig_alg.algorithm)
            oid = x509.oid.ObjectIdentifier(dotted)
            result['digest'] = crypto_utils.cryptography_oid_to_name(oid)
        issuer = []
        for attribute in self.crl.issuer:
            issuer.append([crypto_utils.cryptography_oid_to_name(attribute.oid), attribute.value])
        result['issuer_ordered'] = issuer
        result['issuer'] = {}
        for (k, v) in issuer:
            result['issuer'][k] = v
        result['revoked_certificates'] = []
        for cert in self.crl:
            entry = crypto_utils.cryptography_decode_revoked_certificate(cert)
            result['revoked_certificates'].append(self._dump_revoked(entry))
        return result

    def generate(self):
        pass

    def dump(self):
        pass

def main():
    module = AnsibleModule(argument_spec=dict(path=dict(type='path'), content=dict(type='str')), required_one_of=(['path', 'content'],), mutually_exclusive=(['path', 'content'],), supports_check_mode=True)
    if not CRYPTOGRAPHY_FOUND:
        module.fail_json(msg=missing_required_lib('cryptography >= {0}'.format(MINIMAL_CRYPTOGRAPHY_VERSION)), exception=CRYPTOGRAPHY_IMP_ERR)
    try:
        crl = CRLInfo(module)
        result = crl.get_info()
        module.exit_json(**result)
    except crypto_utils.OpenSSLObjectError as e:
        module.fail_json(msg=to_native(e))
if __name__ == '__main__':
    main()

def test_CRLInfo__dump_revoked():
    ret = CRLInfo()._dump_revoked()

def test_CRLInfo_get_info():
    ret = CRLInfo().get_info()

def test_CRLInfo_generate():
    ret = CRLInfo().generate()

def test_CRLInfo_dump():
    ret = CRLInfo().dump()