from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: openssl_certificate_info\nversion_added: \'2.8\'\nshort_description: Provide information of OpenSSL X.509 certificates\ndescription:\n    - This module allows one to query information on OpenSSL certificates.\n    - It uses the pyOpenSSL or cryptography python library to interact with OpenSSL. If both the\n      cryptography and PyOpenSSL libraries are available (and meet the minimum version requirements)\n      cryptography will be preferred as a backend over PyOpenSSL (unless the backend is forced with\n      C(select_crypto_backend)). Please note that the PyOpenSSL backend was deprecated in Ansible 2.9\n      and will be removed in Ansible 2.13.\nrequirements:\n    - PyOpenSSL >= 0.15 or cryptography >= 1.6\nauthor:\n  - Felix Fontein (@felixfontein)\n  - Yanis Guenane (@Spredzy)\n  - Markus Teufelberger (@MarkusTeufelberger)\noptions:\n    path:\n        description:\n            - Remote absolute path where the certificate file is loaded from.\n            - Either I(path) or I(content) must be specified, but not both.\n        type: path\n    content:\n        description:\n            - Content of the X.509 certificate in PEM format.\n            - Either I(path) or I(content) must be specified, but not both.\n        type: str\n        version_added: "2.10"\n    valid_at:\n        description:\n            - A dict of names mapping to time specifications. Every time specified here\n              will be checked whether the certificate is valid at this point. See the\n              C(valid_at) return value for informations on the result.\n            - Time can be specified either as relative time or as absolute timestamp.\n            - Time will always be interpreted as UTC.\n            - Valid format is C([+-]timespec | ASN.1 TIME) where timespec can be an integer\n              + C([w | d | h | m | s]) (e.g. C(+32w1d2h), and ASN.1 TIME (i.e. pattern C(YYYYMMDDHHMMSSZ)).\n              Note that all timestamps will be treated as being in UTC.\n        type: dict\n    select_crypto_backend:\n        description:\n            - Determines which crypto backend to use.\n            - The default choice is C(auto), which tries to use C(cryptography) if available, and falls back to C(pyopenssl).\n            - If set to C(pyopenssl), will try to use the L(pyOpenSSL,https://pypi.org/project/pyOpenSSL/) library.\n            - If set to C(cryptography), will try to use the L(cryptography,https://cryptography.io/) library.\n            - Please note that the C(pyopenssl) backend has been deprecated in Ansible 2.9, and will be removed in Ansible 2.13.\n              From that point on, only the C(cryptography) backend will be available.\n        type: str\n        default: auto\n        choices: [ auto, cryptography, pyopenssl ]\n\nnotes:\n    - All timestamp values are provided in ASN.1 TIME format, i.e. following the C(YYYYMMDDHHMMSSZ) pattern.\n      They are all in UTC.\nseealso:\n- module: openssl_certificate\n'
EXAMPLES = '\n- name: Generate a Self Signed OpenSSL certificate\n  openssl_certificate:\n    path: /etc/ssl/crt/ansible.com.crt\n    privatekey_path: /etc/ssl/private/ansible.com.pem\n    csr_path: /etc/ssl/csr/ansible.com.csr\n    provider: selfsigned\n\n\n# Get information on the certificate\n\n- name: Get information on generated certificate\n  openssl_certificate_info:\n    path: /etc/ssl/crt/ansible.com.crt\n  register: result\n\n- name: Dump information\n  debug:\n    var: result\n\n\n# Check whether the certificate is valid or not valid at certain times, fail\n# if this is not the case. The first task (openssl_certificate_info) collects\n# the information, and the second task (assert) validates the result and\n# makes the playbook fail in case something is not as expected.\n\n- name: Test whether that certificate is valid tomorrow and/or in three weeks\n  openssl_certificate_info:\n    path: /etc/ssl/crt/ansible.com.crt\n    valid_at:\n      point_1: "+1d"\n      point_2: "+3w"\n  register: result\n\n- name: Validate that certificate is valid tomorrow, but not in three weeks\n  assert:\n    that:\n      - result.valid_at.point_1      # valid in one day\n      - not result.valid_at.point_2  # not valid in three weeks\n'
RETURN = '\nexpired:\n    description: Whether the certificate is expired (i.e. C(notAfter) is in the past)\n    returned: success\n    type: bool\nbasic_constraints:\n    description: Entries in the C(basic_constraints) extension, or C(none) if extension is not present.\n    returned: success\n    type: list\n    elements: str\n    sample: "[CA:TRUE, pathlen:1]"\nbasic_constraints_critical:\n    description: Whether the C(basic_constraints) extension is critical.\n    returned: success\n    type: bool\nextended_key_usage:\n    description: Entries in the C(extended_key_usage) extension, or C(none) if extension is not present.\n    returned: success\n    type: list\n    elements: str\n    sample: "[Biometric Info, DVCS, Time Stamping]"\nextended_key_usage_critical:\n    description: Whether the C(extended_key_usage) extension is critical.\n    returned: success\n    type: bool\nextensions_by_oid:\n    description: Returns a dictionary for every extension OID\n    returned: success\n    type: dict\n    contains:\n        critical:\n            description: Whether the extension is critical.\n            returned: success\n            type: bool\n        value:\n            description: The Base64 encoded value (in DER format) of the extension\n            returned: success\n            type: str\n            sample: "MAMCAQU="\n    sample: \'{"1.3.6.1.5.5.7.1.24": { "critical": false, "value": "MAMCAQU="}}\'\nkey_usage:\n    description: Entries in the C(key_usage) extension, or C(none) if extension is not present.\n    returned: success\n    type: str\n    sample: "[Key Agreement, Data Encipherment]"\nkey_usage_critical:\n    description: Whether the C(key_usage) extension is critical.\n    returned: success\n    type: bool\nsubject_alt_name:\n    description: Entries in the C(subject_alt_name) extension, or C(none) if extension is not present.\n    returned: success\n    type: list\n    elements: str\n    sample: "[DNS:www.ansible.com, IP:1.2.3.4]"\nsubject_alt_name_critical:\n    description: Whether the C(subject_alt_name) extension is critical.\n    returned: success\n    type: bool\nocsp_must_staple:\n    description: C(yes) if the OCSP Must Staple extension is present, C(none) otherwise.\n    returned: success\n    type: bool\nocsp_must_staple_critical:\n    description: Whether the C(ocsp_must_staple) extension is critical.\n    returned: success\n    type: bool\nissuer:\n    description:\n        - The certificate\'s issuer.\n        - Note that for repeated values, only the last one will be returned.\n    returned: success\n    type: dict\n    sample: \'{"organizationName": "Ansible", "commonName": "ca.example.com"}\'\nissuer_ordered:\n    description: The certificate\'s issuer as an ordered list of tuples.\n    returned: success\n    type: list\n    elements: list\n    sample: \'[["organizationName", "Ansible"], ["commonName": "ca.example.com"]]\'\n    version_added: "2.9"\nsubject:\n    description:\n        - The certificate\'s subject as a dictionary.\n        - Note that for repeated values, only the last one will be returned.\n    returned: success\n    type: dict\n    sample: \'{"commonName": "www.example.com", "emailAddress": "test@example.com"}\'\nsubject_ordered:\n    description: The certificate\'s subject as an ordered list of tuples.\n    returned: success\n    type: list\n    elements: list\n    sample: \'[["commonName", "www.example.com"], ["emailAddress": "test@example.com"]]\'\n    version_added: "2.9"\nnot_after:\n    description: C(notAfter) date as ASN.1 TIME\n    returned: success\n    type: str\n    sample: 20190413202428Z\nnot_before:\n    description: C(notBefore) date as ASN.1 TIME\n    returned: success\n    type: str\n    sample: 20190331202428Z\npublic_key:\n    description: Certificate\'s public key in PEM format\n    returned: success\n    type: str\n    sample: "-----BEGIN PUBLIC KEY-----\\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8A..."\npublic_key_fingerprints:\n    description:\n        - Fingerprints of certificate\'s public key.\n        - For every hash algorithm available, the fingerprint is computed.\n    returned: success\n    type: dict\n    sample: "{\'sha256\': \'d4:b3:aa:6d:c8:04:ce:4e:ba:f6:29:4d:92:a3:94:b0:c2:ff:bd:bf:33:63:11:43:34:0f:51:b0:95:09:2f:63\',\n              \'sha512\': \'f7:07:4a:f0:b0:f0:e6:8b:95:5f:f9:e6:61:0a:32:68:f1..."\nsignature_algorithm:\n    description: The signature algorithm used to sign the certificate.\n    returned: success\n    type: str\n    sample: sha256WithRSAEncryption\nserial_number:\n    description: The certificate\'s serial number.\n    returned: success\n    type: int\n    sample: 1234\nversion:\n    description: The certificate version.\n    returned: success\n    type: int\n    sample: 3\nvalid_at:\n    description: For every time stamp provided in the I(valid_at) option, a\n                 boolean whether the certificate is valid at that point in time\n                 or not.\n    returned: success\n    type: dict\nsubject_key_identifier:\n    description:\n        - The certificate\'s subject key identifier.\n        - The identifier is returned in hexadecimal, with C(:) used to separate bytes.\n        - Is C(none) if the C(SubjectKeyIdentifier) extension is not present.\n    returned: success and if the pyOpenSSL backend is I(not) used\n    type: str\n    sample: \'00:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff:00:11:22:33\'\n    version_added: "2.9"\nauthority_key_identifier:\n    description:\n        - The certificate\'s authority key identifier.\n        - The identifier is returned in hexadecimal, with C(:) used to separate bytes.\n        - Is C(none) if the C(AuthorityKeyIdentifier) extension is not present.\n    returned: success and if the pyOpenSSL backend is I(not) used\n    type: str\n    sample: \'00:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff:00:11:22:33\'\n    version_added: "2.9"\nauthority_cert_issuer:\n    description:\n        - The certificate\'s authority cert issuer as a list of general names.\n        - Is C(none) if the C(AuthorityKeyIdentifier) extension is not present.\n    returned: success and if the pyOpenSSL backend is I(not) used\n    type: list\n    elements: str\n    sample: "[DNS:www.ansible.com, IP:1.2.3.4]"\n    version_added: "2.9"\nauthority_cert_serial_number:\n    description:\n        - The certificate\'s authority cert serial number.\n        - Is C(none) if the C(AuthorityKeyIdentifier) extension is not present.\n    returned: success and if the pyOpenSSL backend is I(not) used\n    type: int\n    sample: \'12345\'\n    version_added: "2.9"\nocsp_uri:\n    description: The OCSP responder URI, if included in the certificate. Will be\n                 C(none) if no OCSP responder URI is included.\n    returned: success\n    type: str\n    version_added: "2.9"\n'
import abc
import binascii
import datetime
import os
import re
import traceback
from distutils.version import LooseVersion
from ansible.module_utils import crypto as crypto_utils
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.six import string_types
from ansible.module_utils._text import to_native, to_text, to_bytes
from ansible.module_utils.compat import ipaddress as compat_ipaddress
MINIMAL_CRYPTOGRAPHY_VERSION = '1.6'
MINIMAL_PYOPENSSL_VERSION = '0.15'
PYOPENSSL_IMP_ERR = None
try:
    import OpenSSL
    from OpenSSL import crypto
    PYOPENSSL_VERSION = LooseVersion(OpenSSL.__version__)
    if OpenSSL.SSL.OPENSSL_VERSION_NUMBER >= 269484032:
        OPENSSL_MUST_STAPLE_NAME = b'tlsfeature'
        OPENSSL_MUST_STAPLE_VALUE = b'status_request'
    else:
        OPENSSL_MUST_STAPLE_NAME = b'1.3.6.1.5.5.7.1.24'
        OPENSSL_MUST_STAPLE_VALUE = b'DER:30:03:02:01:05'
except ImportError:
    PYOPENSSL_IMP_ERR = traceback.format_exc()
    PYOPENSSL_FOUND = False
else:
    PYOPENSSL_FOUND = True
CRYPTOGRAPHY_IMP_ERR = None
try:
    import cryptography
    from cryptography import x509
    from cryptography.hazmat.primitives import serialization
    CRYPTOGRAPHY_VERSION = LooseVersion(cryptography.__version__)
except ImportError:
    CRYPTOGRAPHY_IMP_ERR = traceback.format_exc()
    CRYPTOGRAPHY_FOUND = False
else:
    CRYPTOGRAPHY_FOUND = True
TIMESTAMP_FORMAT = '%Y%m%d%H%M%SZ'

class CertificateInfo(crypto_utils.OpenSSLObject):

    def __init__(self, module, backend):
        super(CertificateInfo, self).__init__(module.params['path'] or '', 'present', False, module.check_mode)
        self.backend = backend
        self.module = module
        self.content = module.params['content']
        if self.content is not None:
            self.content = self.content.encode('utf-8')
        self.valid_at = module.params['valid_at']
        if self.valid_at:
            for (k, v) in self.valid_at.items():
                if not isinstance(v, string_types):
                    self.module.fail_json(msg='The value for valid_at.{0} must be of type string (got {1})'.format(k, type(v)))
                self.valid_at[k] = crypto_utils.get_relative_time_option(v, 'valid_at.{0}'.format(k))

    def generate(self):
        pass

    def dump(self):
        pass

    @abc.abstractmethod
    def _get_signature_algorithm(self):
        pass

    @abc.abstractmethod
    def _get_subject_ordered(self):
        pass

    @abc.abstractmethod
    def _get_issuer_ordered(self):
        pass

    @abc.abstractmethod
    def _get_version(self):
        pass

    @abc.abstractmethod
    def _get_key_usage(self):
        pass

    @abc.abstractmethod
    def _get_extended_key_usage(self):
        pass

    @abc.abstractmethod
    def _get_basic_constraints(self):
        pass

    @abc.abstractmethod
    def _get_ocsp_must_staple(self):
        pass

    @abc.abstractmethod
    def _get_subject_alt_name(self):
        pass

    @abc.abstractmethod
    def _get_not_before(self):
        pass

    @abc.abstractmethod
    def _get_not_after(self):
        pass

    @abc.abstractmethod
    def _get_public_key(self, binary):
        pass

    @abc.abstractmethod
    def _get_subject_key_identifier(self):
        pass

    @abc.abstractmethod
    def _get_authority_key_identifier(self):
        pass

    @abc.abstractmethod
    def _get_serial_number(self):
        pass

    @abc.abstractmethod
    def _get_all_extensions(self):
        pass

    @abc.abstractmethod
    def _get_ocsp_uri(self):
        pass

    def get_info(self):
        result = dict()
        self.cert = crypto_utils.load_certificate(self.path, content=self.content, backend=self.backend)
        result['signature_algorithm'] = self._get_signature_algorithm()
        subject = self._get_subject_ordered()
        issuer = self._get_issuer_ordered()
        result['subject'] = dict()
        for (k, v) in subject:
            result['subject'][k] = v
        result['subject_ordered'] = subject
        result['issuer'] = dict()
        for (k, v) in issuer:
            result['issuer'][k] = v
        result['issuer_ordered'] = issuer
        result['version'] = self._get_version()
        (result['key_usage'], result['key_usage_critical']) = self._get_key_usage()
        (result['extended_key_usage'], result['extended_key_usage_critical']) = self._get_extended_key_usage()
        (result['basic_constraints'], result['basic_constraints_critical']) = self._get_basic_constraints()
        (result['ocsp_must_staple'], result['ocsp_must_staple_critical']) = self._get_ocsp_must_staple()
        (result['subject_alt_name'], result['subject_alt_name_critical']) = self._get_subject_alt_name()
        not_before = self._get_not_before()
        not_after = self._get_not_after()
        result['not_before'] = not_before.strftime(TIMESTAMP_FORMAT)
        result['not_after'] = not_after.strftime(TIMESTAMP_FORMAT)
        result['expired'] = not_after < datetime.datetime.utcnow()
        result['valid_at'] = dict()
        if self.valid_at:
            for (k, v) in self.valid_at.items():
                result['valid_at'][k] = not_before <= v <= not_after
        result['public_key'] = self._get_public_key(binary=False)
        pk = self._get_public_key(binary=True)
        result['public_key_fingerprints'] = crypto_utils.get_fingerprint_of_bytes(pk) if pk is not None else dict()
        if self.backend != 'pyopenssl':
            ski = self._get_subject_key_identifier()
            if ski is not None:
                ski = to_native(binascii.hexlify(ski))
                ski = ':'.join([ski[i:i + 2] for i in range(0, len(ski), 2)])
            result['subject_key_identifier'] = ski
            (aki, aci, acsn) = self._get_authority_key_identifier()
            if aki is not None:
                aki = to_native(binascii.hexlify(aki))
                aki = ':'.join([aki[i:i + 2] for i in range(0, len(aki), 2)])
            result['authority_key_identifier'] = aki
            result['authority_cert_issuer'] = aci
            result['authority_cert_serial_number'] = acsn
        result['serial_number'] = self._get_serial_number()
        result['extensions_by_oid'] = self._get_all_extensions()
        result['ocsp_uri'] = self._get_ocsp_uri()
        return result

class CertificateInfoCryptography(CertificateInfo):
    """Validate the supplied cert, using the cryptography backend"""

    def __init__(self, module):
        super(CertificateInfoCryptography, self).__init__(module, 'cryptography')

    def _get_signature_algorithm(self):
        return crypto_utils.cryptography_oid_to_name(self.cert.signature_algorithm_oid)

    def _get_subject_ordered(self):
        result = []
        for attribute in self.cert.subject:
            result.append([crypto_utils.cryptography_oid_to_name(attribute.oid), attribute.value])
        return result

    def _get_issuer_ordered(self):
        result = []
        for attribute in self.cert.issuer:
            result.append([crypto_utils.cryptography_oid_to_name(attribute.oid), attribute.value])
        return result

    def _get_version(self):
        if self.cert.version == x509.Version.v1:
            return 1
        if self.cert.version == x509.Version.v3:
            return 3
        return 'unknown'

    def _get_key_usage(self):
        try:
            current_key_ext = self.cert.extensions.get_extension_for_class(x509.KeyUsage)
            current_key_usage = current_key_ext.value
            key_usage = dict(digital_signature=current_key_usage.digital_signature, content_commitment=current_key_usage.content_commitment, key_encipherment=current_key_usage.key_encipherment, data_encipherment=current_key_usage.data_encipherment, key_agreement=current_key_usage.key_agreement, key_cert_sign=current_key_usage.key_cert_sign, crl_sign=current_key_usage.crl_sign, encipher_only=False, decipher_only=False)
            if key_usage['key_agreement']:
                key_usage.update(dict(encipher_only=current_key_usage.encipher_only, decipher_only=current_key_usage.decipher_only))
            key_usage_names = dict(digital_signature='Digital Signature', content_commitment='Non Repudiation', key_encipherment='Key Encipherment', data_encipherment='Data Encipherment', key_agreement='Key Agreement', key_cert_sign='Certificate Sign', crl_sign='CRL Sign', encipher_only='Encipher Only', decipher_only='Decipher Only')
            return (sorted([key_usage_names[name] for (name, value) in key_usage.items() if value]), current_key_ext.critical)
        except cryptography.x509.ExtensionNotFound:
            return (None, False)

    def _get_extended_key_usage(self):
        try:
            ext_keyusage_ext = self.cert.extensions.get_extension_for_class(x509.ExtendedKeyUsage)
            return (sorted([crypto_utils.cryptography_oid_to_name(eku) for eku in ext_keyusage_ext.value]), ext_keyusage_ext.critical)
        except cryptography.x509.ExtensionNotFound:
            return (None, False)

    def _get_basic_constraints(self):
        try:
            ext_keyusage_ext = self.cert.extensions.get_extension_for_class(x509.BasicConstraints)
            result = []
            result.append('CA:{0}'.format('TRUE' if ext_keyusage_ext.value.ca else 'FALSE'))
            if ext_keyusage_ext.value.path_length is not None:
                result.append('pathlen:{0}'.format(ext_keyusage_ext.value.path_length))
            return (sorted(result), ext_keyusage_ext.critical)
        except cryptography.x509.ExtensionNotFound:
            return (None, False)

    def _get_ocsp_must_staple(self):
        try:
            try:
                tlsfeature_ext = self.cert.extensions.get_extension_for_class(x509.TLSFeature)
                value = cryptography.x509.TLSFeatureType.status_request in tlsfeature_ext.value
            except AttributeError as dummy:
                oid = x509.oid.ObjectIdentifier('1.3.6.1.5.5.7.1.24')
                tlsfeature_ext = self.cert.extensions.get_extension_for_oid(oid)
                value = tlsfeature_ext.value.value == b'0\x03\x02\x01\x05'
            return (value, tlsfeature_ext.critical)
        except cryptography.x509.ExtensionNotFound:
            return (None, False)

    def _get_subject_alt_name(self):
        try:
            san_ext = self.cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            result = [crypto_utils.cryptography_decode_name(san) for san in san_ext.value]
            return (result, san_ext.critical)
        except cryptography.x509.ExtensionNotFound:
            return (None, False)

    def _get_not_before(self):
        return self.cert.not_valid_before

    def _get_not_after(self):
        return self.cert.not_valid_after

    def _get_public_key(self, binary):
        return self.cert.public_key().public_bytes(serialization.Encoding.DER if binary else serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)

    def _get_subject_key_identifier(self):
        try:
            ext = self.cert.extensions.get_extension_for_class(x509.SubjectKeyIdentifier)
            return ext.value.digest
        except cryptography.x509.ExtensionNotFound:
            return None

    def _get_authority_key_identifier(self):
        try:
            ext = self.cert.extensions.get_extension_for_class(x509.AuthorityKeyIdentifier)
            issuer = None
            if ext.value.authority_cert_issuer is not None:
                issuer = [crypto_utils.cryptography_decode_name(san) for san in ext.value.authority_cert_issuer]
            return (ext.value.key_identifier, issuer, ext.value.authority_cert_serial_number)
        except cryptography.x509.ExtensionNotFound:
            return (None, None, None)

    def _get_serial_number(self):
        return self.cert.serial_number

    def _get_all_extensions(self):
        return crypto_utils.cryptography_get_extensions_from_cert(self.cert)

    def _get_ocsp_uri(self):
        try:
            ext = self.cert.extensions.get_extension_for_class(x509.AuthorityInformationAccess)
            for desc in ext.value:
                if desc.access_method == x509.oid.AuthorityInformationAccessOID.OCSP:
                    if isinstance(desc.access_location, x509.UniformResourceIdentifier):
                        return desc.access_location.value
        except x509.ExtensionNotFound as dummy:
            pass
        return None

class CertificateInfoPyOpenSSL(CertificateInfo):
    """validate the supplied certificate."""

    def __init__(self, module):
        super(CertificateInfoPyOpenSSL, self).__init__(module, 'pyopenssl')

    def _get_signature_algorithm(self):
        return to_text(self.cert.get_signature_algorithm())

    def __get_name(self, name):
        result = []
        for sub in name.get_components():
            result.append([crypto_utils.pyopenssl_normalize_name(sub[0]), to_text(sub[1])])
        return result

    def _get_subject_ordered(self):
        return self.__get_name(self.cert.get_subject())

    def _get_issuer_ordered(self):
        return self.__get_name(self.cert.get_issuer())

    def _get_version(self):
        return self.cert.get_version() + 1

    def _get_extension(self, short_name):
        for extension_idx in range(0, self.cert.get_extension_count()):
            extension = self.cert.get_extension(extension_idx)
            if extension.get_short_name() == short_name:
                result = [crypto_utils.pyopenssl_normalize_name(usage.strip()) for usage in to_text(extension, errors='surrogate_or_strict').split(',')]
                return (sorted(result), bool(extension.get_critical()))
        return (None, False)

    def _get_key_usage(self):
        return self._get_extension(b'keyUsage')

    def _get_extended_key_usage(self):
        return self._get_extension(b'extendedKeyUsage')

    def _get_basic_constraints(self):
        return self._get_extension(b'basicConstraints')

    def _get_ocsp_must_staple(self):
        extensions = [self.cert.get_extension(i) for i in range(0, self.cert.get_extension_count())]
        oms_ext = [ext for ext in extensions if to_bytes(ext.get_short_name()) == OPENSSL_MUST_STAPLE_NAME and to_bytes(ext) == OPENSSL_MUST_STAPLE_VALUE]
        if OpenSSL.SSL.OPENSSL_VERSION_NUMBER < 269484032:
            oms_ext.extend([ext for ext in extensions if ext.get_short_name() == b'UNDEF' and ext.get_data() == b'0\x03\x02\x01\x05'])
        if oms_ext:
            return (True, bool(oms_ext[0].get_critical()))
        else:
            return (None, False)

    def _normalize_san(self, san):
        if san.startswith('IP Address:'):
            san = 'IP:' + san[len('IP Address:'):]
        if san.startswith('IP:'):
            ip = compat_ipaddress.ip_address(san[3:])
            san = 'IP:{0}'.format(ip.compressed)
        return san

    def _get_subject_alt_name(self):
        for extension_idx in range(0, self.cert.get_extension_count()):
            extension = self.cert.get_extension(extension_idx)
            if extension.get_short_name() == b'subjectAltName':
                result = [self._normalize_san(altname.strip()) for altname in to_text(extension, errors='surrogate_or_strict').split(', ')]
                return (result, bool(extension.get_critical()))
        return (None, False)

    def _get_not_before(self):
        time_string = to_native(self.cert.get_notBefore())
        return datetime.datetime.strptime(time_string, '%Y%m%d%H%M%SZ')

    def _get_not_after(self):
        time_string = to_native(self.cert.get_notAfter())
        return datetime.datetime.strptime(time_string, '%Y%m%d%H%M%SZ')

    def _get_public_key(self, binary):
        try:
            return crypto.dump_publickey(crypto.FILETYPE_ASN1 if binary else crypto.FILETYPE_PEM, self.cert.get_pubkey())
        except AttributeError:
            try:
                bio = crypto._new_mem_buf()
                if binary:
                    rc = crypto._lib.i2d_PUBKEY_bio(bio, self.cert.get_pubkey()._pkey)
                else:
                    rc = crypto._lib.PEM_write_bio_PUBKEY(bio, self.cert.get_pubkey()._pkey)
                if rc != 1:
                    crypto._raise_current_error()
                return crypto._bio_to_string(bio)
            except AttributeError:
                self.module.warn('Your pyOpenSSL version does not support dumping public keys. Please upgrade to version 16.0 or newer, or use the cryptography backend.')

    def _get_subject_key_identifier(self):
        return None

    def _get_authority_key_identifier(self):
        return (None, None, None)

    def _get_serial_number(self):
        return self.cert.get_serial_number()

    def _get_all_extensions(self):
        return crypto_utils.pyopenssl_get_extensions_from_cert(self.cert)

    def _get_ocsp_uri(self):
        for i in range(self.cert.get_extension_count()):
            ext = self.cert.get_extension(i)
            if ext.get_short_name() == b'authorityInfoAccess':
                v = str(ext)
                m = re.search('^OCSP - URI:(.*)$', v, flags=re.MULTILINE)
                if m:
                    return m.group(1)
        return None

def main():
    module = AnsibleModule(argument_spec=dict(path=dict(type='path'), content=dict(type='str'), valid_at=dict(type='dict'), select_crypto_backend=dict(type='str', default='auto', choices=['auto', 'cryptography', 'pyopenssl'])), required_one_of=(['path', 'content'],), mutually_exclusive=(['path', 'content'],), supports_check_mode=True)
    try:
        if module.params['path'] is not None:
            base_dir = os.path.dirname(module.params['path']) or '.'
            if not os.path.isdir(base_dir):
                module.fail_json(name=base_dir, msg='The directory %s does not exist or the file is not a directory' % base_dir)
        backend = module.params['select_crypto_backend']
        if backend == 'auto':
            can_use_cryptography = CRYPTOGRAPHY_FOUND and CRYPTOGRAPHY_VERSION >= LooseVersion(MINIMAL_CRYPTOGRAPHY_VERSION)
            can_use_pyopenssl = PYOPENSSL_FOUND and PYOPENSSL_VERSION >= LooseVersion(MINIMAL_PYOPENSSL_VERSION)
            if can_use_cryptography:
                backend = 'cryptography'
            elif can_use_pyopenssl:
                backend = 'pyopenssl'
            if backend == 'auto':
                module.fail_json(msg="Can't detect any of the required Python libraries cryptography (>= {0}) or PyOpenSSL (>= {1})".format(MINIMAL_CRYPTOGRAPHY_VERSION, MINIMAL_PYOPENSSL_VERSION))
        if backend == 'pyopenssl':
            if not PYOPENSSL_FOUND:
                module.fail_json(msg=missing_required_lib('pyOpenSSL >= {0}'.format(MINIMAL_PYOPENSSL_VERSION)), exception=PYOPENSSL_IMP_ERR)
            try:
                getattr(crypto.X509Req, 'get_extensions')
            except AttributeError:
                module.fail_json(msg='You need to have PyOpenSSL>=0.15')
            module.deprecate('The module is using the PyOpenSSL backend. This backend has been deprecated', version='2.13', collection_name='ansible.builtin')
            certificate = CertificateInfoPyOpenSSL(module)
        elif backend == 'cryptography':
            if not CRYPTOGRAPHY_FOUND:
                module.fail_json(msg=missing_required_lib('cryptography >= {0}'.format(MINIMAL_CRYPTOGRAPHY_VERSION)), exception=CRYPTOGRAPHY_IMP_ERR)
            certificate = CertificateInfoCryptography(module)
        result = certificate.get_info()
        module.exit_json(**result)
    except crypto_utils.OpenSSLObjectError as exc:
        module.fail_json(msg=to_native(exc))
if __name__ == '__main__':
    main()

def test_CertificateInfo_generate():
    ret = CertificateInfo().generate()

def test_CertificateInfo_dump():
    ret = CertificateInfo().dump()

def test_CertificateInfo__get_signature_algorithm():
    ret = CertificateInfo()._get_signature_algorithm()

def test_CertificateInfo__get_subject_ordered():
    ret = CertificateInfo()._get_subject_ordered()

def test_CertificateInfo__get_issuer_ordered():
    ret = CertificateInfo()._get_issuer_ordered()

def test_CertificateInfo__get_version():
    ret = CertificateInfo()._get_version()

def test_CertificateInfo__get_key_usage():
    ret = CertificateInfo()._get_key_usage()

def test_CertificateInfo__get_extended_key_usage():
    ret = CertificateInfo()._get_extended_key_usage()

def test_CertificateInfo__get_basic_constraints():
    ret = CertificateInfo()._get_basic_constraints()

def test_CertificateInfo__get_ocsp_must_staple():
    ret = CertificateInfo()._get_ocsp_must_staple()

def test_CertificateInfo__get_subject_alt_name():
    ret = CertificateInfo()._get_subject_alt_name()

def test_CertificateInfo__get_not_before():
    ret = CertificateInfo()._get_not_before()

def test_CertificateInfo__get_not_after():
    ret = CertificateInfo()._get_not_after()

def test_CertificateInfo__get_public_key():
    ret = CertificateInfo()._get_public_key()

def test_CertificateInfo__get_subject_key_identifier():
    ret = CertificateInfo()._get_subject_key_identifier()

def test_CertificateInfo__get_authority_key_identifier():
    ret = CertificateInfo()._get_authority_key_identifier()

def test_CertificateInfo__get_serial_number():
    ret = CertificateInfo()._get_serial_number()

def test_CertificateInfo__get_all_extensions():
    ret = CertificateInfo()._get_all_extensions()

def test_CertificateInfo__get_ocsp_uri():
    ret = CertificateInfo()._get_ocsp_uri()

def test_CertificateInfo_get_info():
    ret = CertificateInfo().get_info()

def test_CertificateInfoCryptography__get_signature_algorithm():
    ret = CertificateInfoCryptography()._get_signature_algorithm()

def test_CertificateInfoCryptography__get_subject_ordered():
    ret = CertificateInfoCryptography()._get_subject_ordered()

def test_CertificateInfoCryptography__get_issuer_ordered():
    ret = CertificateInfoCryptography()._get_issuer_ordered()

def test_CertificateInfoCryptography__get_version():
    ret = CertificateInfoCryptography()._get_version()

def test_CertificateInfoCryptography__get_key_usage():
    ret = CertificateInfoCryptography()._get_key_usage()

def test_CertificateInfoCryptography__get_extended_key_usage():
    ret = CertificateInfoCryptography()._get_extended_key_usage()

def test_CertificateInfoCryptography__get_basic_constraints():
    ret = CertificateInfoCryptography()._get_basic_constraints()

def test_CertificateInfoCryptography__get_ocsp_must_staple():
    ret = CertificateInfoCryptography()._get_ocsp_must_staple()

def test_CertificateInfoCryptography__get_subject_alt_name():
    ret = CertificateInfoCryptography()._get_subject_alt_name()

def test_CertificateInfoCryptography__get_not_before():
    ret = CertificateInfoCryptography()._get_not_before()

def test_CertificateInfoCryptography__get_not_after():
    ret = CertificateInfoCryptography()._get_not_after()

def test_CertificateInfoCryptography__get_public_key():
    ret = CertificateInfoCryptography()._get_public_key()

def test_CertificateInfoCryptography__get_subject_key_identifier():
    ret = CertificateInfoCryptography()._get_subject_key_identifier()

def test_CertificateInfoCryptography__get_authority_key_identifier():
    ret = CertificateInfoCryptography()._get_authority_key_identifier()

def test_CertificateInfoCryptography__get_serial_number():
    ret = CertificateInfoCryptography()._get_serial_number()

def test_CertificateInfoCryptography__get_all_extensions():
    ret = CertificateInfoCryptography()._get_all_extensions()

def test_CertificateInfoCryptography__get_ocsp_uri():
    ret = CertificateInfoCryptography()._get_ocsp_uri()

def test_CertificateInfoPyOpenSSL__get_signature_algorithm():
    ret = CertificateInfoPyOpenSSL()._get_signature_algorithm()

def test_CertificateInfoPyOpenSSL___get_name():
    ret = CertificateInfoPyOpenSSL().__get_name()

def test_CertificateInfoPyOpenSSL__get_subject_ordered():
    ret = CertificateInfoPyOpenSSL()._get_subject_ordered()

def test_CertificateInfoPyOpenSSL__get_issuer_ordered():
    ret = CertificateInfoPyOpenSSL()._get_issuer_ordered()

def test_CertificateInfoPyOpenSSL__get_version():
    ret = CertificateInfoPyOpenSSL()._get_version()

def test_CertificateInfoPyOpenSSL__get_extension():
    ret = CertificateInfoPyOpenSSL()._get_extension()

def test_CertificateInfoPyOpenSSL__get_key_usage():
    ret = CertificateInfoPyOpenSSL()._get_key_usage()

def test_CertificateInfoPyOpenSSL__get_extended_key_usage():
    ret = CertificateInfoPyOpenSSL()._get_extended_key_usage()

def test_CertificateInfoPyOpenSSL__get_basic_constraints():
    ret = CertificateInfoPyOpenSSL()._get_basic_constraints()

def test_CertificateInfoPyOpenSSL__get_ocsp_must_staple():
    ret = CertificateInfoPyOpenSSL()._get_ocsp_must_staple()

def test_CertificateInfoPyOpenSSL__normalize_san():
    ret = CertificateInfoPyOpenSSL()._normalize_san()

def test_CertificateInfoPyOpenSSL__get_subject_alt_name():
    ret = CertificateInfoPyOpenSSL()._get_subject_alt_name()

def test_CertificateInfoPyOpenSSL__get_not_before():
    ret = CertificateInfoPyOpenSSL()._get_not_before()

def test_CertificateInfoPyOpenSSL__get_not_after():
    ret = CertificateInfoPyOpenSSL()._get_not_after()

def test_CertificateInfoPyOpenSSL__get_public_key():
    ret = CertificateInfoPyOpenSSL()._get_public_key()

def test_CertificateInfoPyOpenSSL__get_subject_key_identifier():
    ret = CertificateInfoPyOpenSSL()._get_subject_key_identifier()

def test_CertificateInfoPyOpenSSL__get_authority_key_identifier():
    ret = CertificateInfoPyOpenSSL()._get_authority_key_identifier()

def test_CertificateInfoPyOpenSSL__get_serial_number():
    ret = CertificateInfoPyOpenSSL()._get_serial_number()

def test_CertificateInfoPyOpenSSL__get_all_extensions():
    ret = CertificateInfoPyOpenSSL()._get_all_extensions()

def test_CertificateInfoPyOpenSSL__get_ocsp_uri():
    ret = CertificateInfoPyOpenSSL()._get_ocsp_uri()