from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: x509_crl\nversion_added: "2.10"\nshort_description: Generate Certificate Revocation Lists (CRLs)\ndescription:\n    - This module allows one to (re)generate or update Certificate Revocation Lists (CRLs).\n    - Certificates on the revocation list can be either specified via serial number and (optionally) their issuer,\n      or as a path to a certificate file in PEM format.\nrequirements:\n    - cryptography >= 1.2\nauthor:\n    - Felix Fontein (@felixfontein)\noptions:\n    state:\n        description:\n            - Whether the CRL file should exist or not, taking action if the state is different from what is stated.\n        type: str\n        default: present\n        choices: [ absent, present ]\n\n    mode:\n        description:\n            - Defines how to process entries of existing CRLs.\n            - If set to C(generate), makes sure that the CRL has the exact set of revoked certificates\n              as specified in I(revoked_certificates).\n            - If set to C(update), makes sure that the CRL contains the revoked certificates from\n              I(revoked_certificates), but can also contain other revoked certificates. If the CRL file\n              already exists, all entries from the existing CRL will also be included in the new CRL.\n              When using C(update), you might be interested in setting I(ignore_timestamps) to C(yes).\n        type: str\n        default: generate\n        choices: [ generate, update ]\n\n    force:\n        description:\n            - Should the CRL be forced to be regenerated.\n        type: bool\n        default: no\n\n    backup:\n        description:\n            - Create a backup file including a timestamp so you can get the original\n              CRL back if you overwrote it with a new one by accident.\n        type: bool\n        default: no\n\n    path:\n        description:\n            - Remote absolute path where the generated CRL file should be created or is already located.\n        type: path\n        required: yes\n\n    privatekey_path:\n        description:\n            - Path to the CA\'s private key to use when signing the CRL.\n            - Either I(privatekey_path) or I(privatekey_content) must be specified if I(state) is C(present), but not both.\n        type: path\n\n    privatekey_content:\n        description:\n            - The content of the CA\'s private key to use when signing the CRL.\n            - Either I(privatekey_path) or I(privatekey_content) must be specified if I(state) is C(present), but not both.\n        type: str\n\n    privatekey_passphrase:\n        description:\n            - The passphrase for the I(privatekey_path).\n            - This is required if the private key is password protected.\n        type: str\n\n    issuer:\n        description:\n            - Key/value pairs that will be present in the issuer name field of the CRL.\n            - If you need to specify more than one value with the same key, use a list as value.\n            - Required if I(state) is C(present).\n        type: dict\n\n    last_update:\n        description:\n            - The point in time from which this CRL can be trusted.\n            - Time can be specified either as relative time or as absolute timestamp.\n            - Time will always be interpreted as UTC.\n            - Valid format is C([+-]timespec | ASN.1 TIME) where timespec can be an integer\n              + C([w | d | h | m | s]) (e.g. C(+32w1d2h).\n            - Note that if using relative time this module is NOT idempotent, except when\n              I(ignore_timestamps) is set to C(yes).\n        type: str\n        default: "+0s"\n\n    next_update:\n        description:\n            - "The absolute latest point in time by which this I(issuer) is expected to have issued\n               another CRL. Many clients will treat a CRL as expired once I(next_update) occurs."\n            - Time can be specified either as relative time or as absolute timestamp.\n            - Time will always be interpreted as UTC.\n            - Valid format is C([+-]timespec | ASN.1 TIME) where timespec can be an integer\n              + C([w | d | h | m | s]) (e.g. C(+32w1d2h).\n            - Note that if using relative time this module is NOT idempotent, except when\n              I(ignore_timestamps) is set to C(yes).\n            - Required if I(state) is C(present).\n        type: str\n\n    digest:\n        description:\n            - Digest algorithm to be used when signing the CRL.\n        type: str\n        default: sha256\n\n    revoked_certificates:\n        description:\n            - List of certificates to be revoked.\n            - Required if I(state) is C(present).\n        type: list\n        elements: dict\n        suboptions:\n            path:\n                description:\n                    - Path to a certificate in PEM format.\n                    - The serial number and issuer will be extracted from the certificate.\n                    - Mutually exclusive with I(content) and I(serial_number). One of these three options\n                      must be specified.\n                type: path\n            content:\n                description:\n                    - Content of a certificate in PEM format.\n                    - The serial number and issuer will be extracted from the certificate.\n                    - Mutually exclusive with I(path) and I(serial_number). One of these three options\n                      must be specified.\n                type: str\n            serial_number:\n                description:\n                    - Serial number of the certificate.\n                    - Mutually exclusive with I(path) and I(content). One of these three options must\n                      be specified.\n                type: int\n            revocation_date:\n                description:\n                    - The point in time the certificate was revoked.\n                    - Time can be specified either as relative time or as absolute timestamp.\n                    - Time will always be interpreted as UTC.\n                    - Valid format is C([+-]timespec | ASN.1 TIME) where timespec can be an integer\n                      + C([w | d | h | m | s]) (e.g. C(+32w1d2h).\n                    - Note that if using relative time this module is NOT idempotent, except when\n                      I(ignore_timestamps) is set to C(yes).\n                type: str\n                default: "+0s"\n            issuer:\n                description:\n                    - The certificate\'s issuer.\n                    - "Example: C(DNS:ca.example.org)"\n                type: list\n                elements: str\n            issuer_critical:\n                description:\n                    - Whether the certificate issuer extension should be critical.\n                type: bool\n                default: no\n            reason:\n                description:\n                    - The value for the revocation reason extension.\n                type: str\n                choices:\n                    - unspecified\n                    - key_compromise\n                    - ca_compromise\n                    - affiliation_changed\n                    - superseded\n                    - cessation_of_operation\n                    - certificate_hold\n                    - privilege_withdrawn\n                    - aa_compromise\n                    - remove_from_crl\n            reason_critical:\n                description:\n                    - Whether the revocation reason extension should be critical.\n                type: bool\n                default: no\n            invalidity_date:\n                description:\n                    - The point in time it was known/suspected that the private key was compromised\n                      or that the certificate otherwise became invalid.\n                    - Time can be specified either as relative time or as absolute timestamp.\n                    - Time will always be interpreted as UTC.\n                    - Valid format is C([+-]timespec | ASN.1 TIME) where timespec can be an integer\n                      + C([w | d | h | m | s]) (e.g. C(+32w1d2h).\n                    - Note that if using relative time this module is NOT idempotent. This will NOT\n                      change when I(ignore_timestamps) is set to C(yes).\n                type: str\n            invalidity_date_critical:\n                description:\n                    - Whether the invalidity date extension should be critical.\n                type: bool\n                default: no\n\n    ignore_timestamps:\n        description:\n            - Whether the timestamps I(last_update), I(next_update) and I(revocation_date) (in\n              I(revoked_certificates)) should be ignored for idempotency checks. The timestamp\n              I(invalidity_date) in I(revoked_certificates) will never be ignored.\n            - Use this in combination with relative timestamps for these values to get idempotency.\n        type: bool\n        default: no\n\n    return_content:\n        description:\n            - If set to C(yes), will return the (current or generated) CRL\'s content as I(crl).\n        type: bool\n        default: no\n\nextends_documentation_fragment:\n    - files\n\nnotes:\n    - All ASN.1 TIME values should be specified following the YYYYMMDDHHMMSSZ pattern.\n    - Date specified should be UTC. Minutes and seconds are mandatory.\n'
EXAMPLES = '\n- name: Generate a CRL\n  x509_crl:\n    path: /etc/ssl/my-ca.crl\n    privatekey_path: /etc/ssl/private/my-ca.pem\n    issuer:\n      CN: My CA\n    last_update: "+0s"\n    next_update: "+7d"\n    revoked_certificates:\n      - serial_number: 1234\n        revocation_date: 20190331202428Z\n        issuer:\n          CN: My CA\n      - serial_number: 2345\n        revocation_date: 20191013152910Z\n        reason: affiliation_changed\n        invalidity_date: 20191001000000Z\n      - path: /etc/ssl/crt/revoked-cert.pem\n        revocation_date: 20191010010203Z\n'
RETURN = '\nfilename:\n    description: Path to the generated CRL\n    returned: changed or success\n    type: str\n    sample: /path/to/my-ca.crl\nbackup_file:\n    description: Name of backup file created.\n    returned: changed and if I(backup) is C(yes)\n    type: str\n    sample: /path/to/my-ca.crl.2019-03-09@11:22~\nprivatekey:\n    description: Path to the private CA key\n    returned: changed or success\n    type: str\n    sample: /path/to/my-ca.pem\nissuer:\n    description:\n        - The CRL\'s issuer.\n        - Note that for repeated values, only the last one will be returned.\n    returned: success\n    type: dict\n    sample: \'{"organizationName": "Ansible", "commonName": "ca.example.com"}\'\nissuer_ordered:\n    description: The CRL\'s issuer as an ordered list of tuples.\n    returned: success\n    type: list\n    elements: list\n    sample: \'[["organizationName", "Ansible"], ["commonName": "ca.example.com"]]\'\nlast_update:\n    description: The point in time from which this CRL can be trusted as ASN.1 TIME.\n    returned: success\n    type: str\n    sample: 20190413202428Z\nnext_update:\n    description: The point in time from which a new CRL will be issued and the client has to check for it as ASN.1 TIME.\n    returned: success\n    type: str\n    sample: 20190413202428Z\ndigest:\n    description: The signature algorithm used to sign the CRL.\n    returned: success\n    type: str\n    sample: sha256WithRSAEncryption\nrevoked_certificates:\n    description: List of certificates to be revoked.\n    returned: success\n    type: list\n    elements: dict\n    contains:\n        serial_number:\n            description: Serial number of the certificate.\n            type: int\n            sample: 1234\n        revocation_date:\n            description: The point in time the certificate was revoked as ASN.1 TIME.\n            type: str\n            sample: 20190413202428Z\n        issuer:\n            description: The certificate\'s issuer.\n            type: list\n            elements: str\n            sample: \'["DNS:ca.example.org"]\'\n        issuer_critical:\n            description: Whether the certificate issuer extension is critical.\n            type: bool\n            sample: no\n        reason:\n            description:\n                - The value for the revocation reason extension.\n                - One of C(unspecified), C(key_compromise), C(ca_compromise), C(affiliation_changed), C(superseded),\n                  C(cessation_of_operation), C(certificate_hold), C(privilege_withdrawn), C(aa_compromise), and\n                  C(remove_from_crl).\n            type: str\n            sample: key_compromise\n        reason_critical:\n            description: Whether the revocation reason extension is critical.\n            type: bool\n            sample: no\n        invalidity_date:\n            description: |\n                The point in time it was known/suspected that the private key was compromised\n                or that the certificate otherwise became invalid as ASN.1 TIME.\n            type: str\n            sample: 20190413202428Z\n        invalidity_date_critical:\n            description: Whether the invalidity date extension is critical.\n            type: bool\n            sample: no\ncrl:\n    description: The (current or generated) CRL\'s content.\n    returned: if I(state) is C(present) and I(return_content) is C(yes)\n    type: str\n'
import os
import traceback
from distutils.version import LooseVersion
from ansible.module_utils import crypto as crypto_utils
from ansible.module_utils._text import to_native, to_text
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
MINIMAL_CRYPTOGRAPHY_VERSION = '1.2'
CRYPTOGRAPHY_IMP_ERR = None
try:
    import cryptography
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.serialization import Encoding
    from cryptography.x509 import CertificateRevocationListBuilder, RevokedCertificateBuilder, NameAttribute, Name
    CRYPTOGRAPHY_VERSION = LooseVersion(cryptography.__version__)
except ImportError:
    CRYPTOGRAPHY_IMP_ERR = traceback.format_exc()
    CRYPTOGRAPHY_FOUND = False
else:
    CRYPTOGRAPHY_FOUND = True
TIMESTAMP_FORMAT = '%Y%m%d%H%M%SZ'

class CRLError(crypto_utils.OpenSSLObjectError):
    pass

class CRL(crypto_utils.OpenSSLObject):

    def __init__(self, module):
        super(CRL, self).__init__(module.params['path'], module.params['state'], module.params['force'], module.check_mode)
        self.update = module.params['mode'] == 'update'
        self.ignore_timestamps = module.params['ignore_timestamps']
        self.return_content = module.params['return_content']
        self.crl_content = None
        self.privatekey_path = module.params['privatekey_path']
        self.privatekey_content = module.params['privatekey_content']
        if self.privatekey_content is not None:
            self.privatekey_content = self.privatekey_content.encode('utf-8')
        self.privatekey_passphrase = module.params['privatekey_passphrase']
        self.issuer = crypto_utils.parse_name_field(module.params['issuer'])
        self.issuer = [(entry[0], entry[1]) for entry in self.issuer if entry[1]]
        self.last_update = crypto_utils.get_relative_time_option(module.params['last_update'], 'last_update')
        self.next_update = crypto_utils.get_relative_time_option(module.params['next_update'], 'next_update')
        self.digest = crypto_utils.select_message_digest(module.params['digest'])
        if self.digest is None:
            raise CRLError('The digest "{0}" is not supported'.format(module.params['digest']))
        self.revoked_certificates = []
        for (i, rc) in enumerate(module.params['revoked_certificates']):
            result = {'serial_number': None, 'revocation_date': None, 'issuer': None, 'issuer_critical': False, 'reason': None, 'reason_critical': False, 'invalidity_date': None, 'invalidity_date_critical': False}
            path_prefix = 'revoked_certificates[{0}].'.format(i)
            if rc['path'] is not None or rc['content'] is not None:
                try:
                    if rc['content'] is not None:
                        rc['content'] = rc['content'].encode('utf-8')
                    cert = crypto_utils.load_certificate(rc['path'], content=rc['content'], backend='cryptography')
                    try:
                        result['serial_number'] = cert.serial_number
                    except AttributeError:
                        result['serial_number'] = cert.serial
                except crypto_utils.OpenSSLObjectError as e:
                    if rc['content'] is not None:
                        module.fail_json(msg='Cannot parse certificate from {0}content: {1}'.format(path_prefix, to_native(e)))
                    else:
                        module.fail_json(msg='Cannot read certificate "{1}" from {0}path: {2}'.format(path_prefix, rc['path'], to_native(e)))
            else:
                result['serial_number'] = rc['serial_number']
            if rc['issuer']:
                result['issuer'] = [crypto_utils.cryptography_get_name(issuer) for issuer in rc['issuer']]
                result['issuer_critical'] = rc['issuer_critical']
            result['revocation_date'] = crypto_utils.get_relative_time_option(rc['revocation_date'], path_prefix + 'revocation_date')
            if rc['reason']:
                result['reason'] = crypto_utils.REVOCATION_REASON_MAP[rc['reason']]
                result['reason_critical'] = rc['reason_critical']
            if rc['invalidity_date']:
                result['invalidity_date'] = crypto_utils.get_relative_time_option(rc['invalidity_date'], path_prefix + 'invalidity_date')
                result['invalidity_date_critical'] = rc['invalidity_date_critical']
            self.revoked_certificates.append(result)
        self.module = module
        self.backup = module.params['backup']
        self.backup_file = None
        try:
            self.privatekey = crypto_utils.load_privatekey(path=self.privatekey_path, content=self.privatekey_content, passphrase=self.privatekey_passphrase, backend='cryptography')
        except crypto_utils.OpenSSLBadPassphraseError as exc:
            raise CRLError(exc)
        self.crl = None
        try:
            with open(self.path, 'rb') as f:
                data = f.read()
            self.crl = x509.load_pem_x509_crl(data, default_backend())
            if self.return_content:
                self.crl_content = data
        except Exception as dummy:
            self.crl_content = None

    def remove(self):
        if self.backup:
            self.backup_file = self.module.backup_local(self.path)
        super(CRL, self).remove(self.module)

    def _compress_entry(self, entry):
        if self.ignore_timestamps:
            return (entry['serial_number'], tuple(entry['issuer']) if entry['issuer'] is not None else None, entry['issuer_critical'], entry['reason'], entry['reason_critical'], entry['invalidity_date'], entry['invalidity_date_critical'])
        else:
            return (entry['serial_number'], entry['revocation_date'], tuple(entry['issuer']) if entry['issuer'] is not None else None, entry['issuer_critical'], entry['reason'], entry['reason_critical'], entry['invalidity_date'], entry['invalidity_date_critical'])

    def check(self, perms_required=True):
        """Ensure the resource is in its desired state."""
        state_and_perms = super(CRL, self).check(self.module, perms_required)
        if not state_and_perms:
            return False
        if self.crl is None:
            return False
        if self.last_update != self.crl.last_update and (not self.ignore_timestamps):
            return False
        if self.next_update != self.crl.next_update and (not self.ignore_timestamps):
            return False
        if self.digest.name != self.crl.signature_hash_algorithm.name:
            return False
        want_issuer = [(crypto_utils.cryptography_name_to_oid(entry[0]), entry[1]) for entry in self.issuer]
        if want_issuer != [(sub.oid, sub.value) for sub in self.crl.issuer]:
            return False
        old_entries = [self._compress_entry(crypto_utils.cryptography_decode_revoked_certificate(cert)) for cert in self.crl]
        new_entries = [self._compress_entry(cert) for cert in self.revoked_certificates]
        if self.update:
            for entry in new_entries:
                try:
                    old_entries.remove(entry)
                except ValueError:
                    return False
        elif old_entries != new_entries:
            return False
        return True

    def _generate_crl(self):
        backend = default_backend()
        crl = CertificateRevocationListBuilder()
        try:
            crl = crl.issuer_name(Name([NameAttribute(crypto_utils.cryptography_name_to_oid(entry[0]), to_text(entry[1])) for entry in self.issuer]))
        except ValueError as e:
            raise CRLError(e)
        crl = crl.last_update(self.last_update)
        crl = crl.next_update(self.next_update)
        if self.update and self.crl:
            new_entries = set([self._compress_entry(entry) for entry in self.revoked_certificates])
            for entry in self.crl:
                decoded_entry = self._compress_entry(crypto_utils.cryptography_decode_revoked_certificate(entry))
                if decoded_entry not in new_entries:
                    crl = crl.add_revoked_certificate(entry)
        for entry in self.revoked_certificates:
            revoked_cert = RevokedCertificateBuilder()
            revoked_cert = revoked_cert.serial_number(entry['serial_number'])
            revoked_cert = revoked_cert.revocation_date(entry['revocation_date'])
            if entry['issuer'] is not None:
                revoked_cert = revoked_cert.add_extension(x509.CertificateIssuer([crypto_utils.cryptography_get_name(name) for name in self.entry['issuer']]), entry['issuer_critical'])
            if entry['reason'] is not None:
                revoked_cert = revoked_cert.add_extension(x509.CRLReason(entry['reason']), entry['reason_critical'])
            if entry['invalidity_date'] is not None:
                revoked_cert = revoked_cert.add_extension(x509.InvalidityDate(entry['invalidity_date']), entry['invalidity_date_critical'])
            crl = crl.add_revoked_certificate(revoked_cert.build(backend))
        self.crl = crl.sign(self.privatekey, self.digest, backend=backend)
        return self.crl.public_bytes(Encoding.PEM)

    def generate(self):
        if not self.check(perms_required=False) or self.force:
            result = self._generate_crl()
            if self.return_content:
                self.crl_content = result
            if self.backup:
                self.backup_file = self.module.backup_local(self.path)
            crypto_utils.write_file(self.module, result)
            self.changed = True
        file_args = self.module.load_file_common_arguments(self.module.params)
        if self.module.set_fs_attributes_if_different(file_args, False):
            self.changed = True

    def _dump_revoked(self, entry):
        return {'serial_number': entry['serial_number'], 'revocation_date': entry['revocation_date'].strftime(TIMESTAMP_FORMAT), 'issuer': [crypto_utils.cryptography_decode_name(issuer) for issuer in entry['issuer']] if entry['issuer'] is not None else None, 'issuer_critical': entry['issuer_critical'], 'reason': crypto_utils.REVOCATION_REASON_MAP_INVERSE.get(entry['reason']) if entry['reason'] is not None else None, 'reason_critical': entry['reason_critical'], 'invalidity_date': entry['invalidity_date'].strftime(TIMESTAMP_FORMAT) if entry['invalidity_date'] is not None else None, 'invalidity_date_critical': entry['invalidity_date_critical']}

    def dump(self, check_mode=False):
        result = {'changed': self.changed, 'filename': self.path, 'privatekey': self.privatekey_path, 'last_update': None, 'next_update': None, 'digest': None, 'issuer_ordered': None, 'issuer': None, 'revoked_certificates': []}
        if self.backup_file:
            result['backup_file'] = self.backup_file
        if check_mode:
            result['last_update'] = self.last_update.strftime(TIMESTAMP_FORMAT)
            result['next_update'] = self.next_update.strftime(TIMESTAMP_FORMAT)
            result['digest'] = self.module.params['digest']
            result['issuer_ordered'] = self.issuer
            result['issuer'] = {}
            for (k, v) in self.issuer:
                result['issuer'][k] = v
            result['revoked_certificates'] = []
            for entry in self.revoked_certificates:
                result['revoked_certificates'].append(self._dump_revoked(entry))
        elif self.crl:
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
        if self.return_content:
            result['crl'] = self.crl_content
        return result

def main():
    module = AnsibleModule(argument_spec=dict(state=dict(type='str', default='present', choices=['present', 'absent']), mode=dict(type='str', default='generate', choices=['generate', 'update']), force=dict(type='bool', default=False), backup=dict(type='bool', default=False), path=dict(type='path', required=True), privatekey_path=dict(type='path'), privatekey_content=dict(type='str'), privatekey_passphrase=dict(type='str', no_log=True), issuer=dict(type='dict'), last_update=dict(type='str', default='+0s'), next_update=dict(type='str'), digest=dict(type='str', default='sha256'), ignore_timestamps=dict(type='bool', default=False), return_content=dict(type='bool', default=False), revoked_certificates=dict(type='list', elements='dict', options=dict(path=dict(type='path'), content=dict(type='str'), serial_number=dict(type='int'), revocation_date=dict(type='str', default='+0s'), issuer=dict(type='list', elements='str'), issuer_critical=dict(type='bool', default=False), reason=dict(type='str', choices=['unspecified', 'key_compromise', 'ca_compromise', 'affiliation_changed', 'superseded', 'cessation_of_operation', 'certificate_hold', 'privilege_withdrawn', 'aa_compromise', 'remove_from_crl']), reason_critical=dict(type='bool', default=False), invalidity_date=dict(type='str'), invalidity_date_critical=dict(type='bool', default=False)), required_one_of=[['path', 'content', 'serial_number']], mutually_exclusive=[['path', 'content', 'serial_number']])), required_if=[('state', 'present', ['privatekey_path', 'privatekey_content'], True), ('state', 'present', ['issuer', 'next_update', 'revoked_certificates'], False)], mutually_exclusive=(['privatekey_path', 'privatekey_content'],), supports_check_mode=True, add_file_common_args=True)
    if not CRYPTOGRAPHY_FOUND:
        module.fail_json(msg=missing_required_lib('cryptography >= {0}'.format(MINIMAL_CRYPTOGRAPHY_VERSION)), exception=CRYPTOGRAPHY_IMP_ERR)
    try:
        crl = CRL(module)
        if module.params['state'] == 'present':
            if module.check_mode:
                result = crl.dump(check_mode=True)
                result['changed'] = module.params['force'] or not crl.check()
                module.exit_json(**result)
            crl.generate()
        else:
            if module.check_mode:
                result = crl.dump(check_mode=True)
                result['changed'] = os.path.exists(module.params['path'])
                module.exit_json(**result)
            crl.remove()
        result = crl.dump()
        module.exit_json(**result)
    except crypto_utils.OpenSSLObjectError as exc:
        module.fail_json(msg=to_native(exc))
if __name__ == '__main__':
    main()

def test_CRL_remove():
    ret = CRL().remove()

def test_CRL__compress_entry():
    ret = CRL()._compress_entry()

def test_CRL_check():
    ret = CRL().check()

def test_CRL__generate_crl():
    ret = CRL()._generate_crl()

def test_CRL_generate():
    ret = CRL().generate()

def test_CRL__dump_revoked():
    ret = CRL()._dump_revoked()

def test_CRL_dump():
    ret = CRL().dump()