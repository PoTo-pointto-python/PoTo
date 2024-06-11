from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\nmodule: htpasswd\nversion_added: "1.3"\nshort_description: manage user files for basic authentication\ndescription:\n  - Add and remove username/password entries in a password file using htpasswd.\n  - This is used by web servers such as Apache and Nginx for basic authentication.\noptions:\n  path:\n    required: true\n    aliases: [ dest, destfile ]\n    description:\n      - Path to the file that contains the usernames and passwords\n  name:\n    required: true\n    aliases: [ username ]\n    description:\n      - User name to add or remove\n  password:\n    required: false\n    description:\n      - Password associated with user.\n      - Must be specified if user does not exist yet.\n  crypt_scheme:\n    required: false\n    choices: ["apr_md5_crypt", "des_crypt", "ldap_sha1", "plaintext"]\n    default: "apr_md5_crypt"\n    description:\n      - Encryption scheme to be used.  As well as the four choices listed\n        here, you can also use any other hash supported by passlib, such as\n        md5_crypt and sha256_crypt, which are linux passwd hashes.  If you\n        do so the password file will not be compatible with Apache or Nginx\n  state:\n    required: false\n    choices: [ present, absent ]\n    default: "present"\n    description:\n      - Whether the user entry should be present or not\n  create:\n    required: false\n    type: bool\n    default: "yes"\n    description:\n      - Used with C(state=present). If specified, the file will be created\n        if it does not already exist. If set to "no", will fail if the\n        file does not exist\nnotes:\n  - "This module depends on the I(passlib) Python library, which needs to be installed on all target systems."\n  - "On Debian, Ubuntu, or Fedora: install I(python-passlib)."\n  - "On RHEL or CentOS: Enable EPEL, then install I(python-passlib)."\nrequirements: [ passlib>=1.6 ]\nauthor: "Ansible Core Team"\nextends_documentation_fragment: files\n'
EXAMPLES = "\n# Add a user to a password file and ensure permissions are set\n- htpasswd:\n    path: /etc/nginx/passwdfile\n    name: janedoe\n    password: '9s36?;fyNp'\n    owner: root\n    group: www-data\n    mode: 0640\n\n# Remove a user from a password file\n- htpasswd:\n    path: /etc/apache2/passwdfile\n    name: foobar\n    state: absent\n\n# Add a user to a password file suitable for use by libpam-pwdfile\n- htpasswd:\n    path: /etc/mail/passwords\n    name: alex\n    password: oedu2eGh\n    crypt_scheme: md5_crypt\n"
import os
import tempfile
import traceback
from distutils.version import LooseVersion
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_native
PASSLIB_IMP_ERR = None
try:
    from passlib.apache import HtpasswdFile, htpasswd_context
    from passlib.context import CryptContext
    import passlib
except ImportError:
    PASSLIB_IMP_ERR = traceback.format_exc()
    passlib_installed = False
else:
    passlib_installed = True
apache_hashes = ['apr_md5_crypt', 'des_crypt', 'ldap_sha1', 'plaintext']

def create_missing_directories(dest):
    destpath = os.path.dirname(dest)
    if not os.path.exists(destpath):
        os.makedirs(destpath)

def present(dest, username, password, crypt_scheme, create, check_mode):
    """ Ensures user is present

    Returns (msg, changed) """
    if crypt_scheme in apache_hashes:
        context = htpasswd_context
    else:
        context = CryptContext(schemes=[crypt_scheme] + apache_hashes)
    if not os.path.exists(dest):
        if not create:
            raise ValueError('Destination %s does not exist' % dest)
        if check_mode:
            return ('Create %s' % dest, True)
        create_missing_directories(dest)
        if LooseVersion(passlib.__version__) >= LooseVersion('1.6'):
            ht = HtpasswdFile(dest, new=True, default_scheme=crypt_scheme, context=context)
        else:
            ht = HtpasswdFile(dest, autoload=False, default=crypt_scheme, context=context)
        if getattr(ht, 'set_password', None):
            ht.set_password(username, password)
        else:
            ht.update(username, password)
        ht.save()
        return ('Created %s and added %s' % (dest, username), True)
    else:
        if LooseVersion(passlib.__version__) >= LooseVersion('1.6'):
            ht = HtpasswdFile(dest, new=False, default_scheme=crypt_scheme, context=context)
        else:
            ht = HtpasswdFile(dest, default=crypt_scheme, context=context)
        found = None
        if getattr(ht, 'check_password', None):
            found = ht.check_password(username, password)
        else:
            found = ht.verify(username, password)
        if found:
            return ('%s already present' % username, False)
        else:
            if not check_mode:
                if getattr(ht, 'set_password', None):
                    ht.set_password(username, password)
                else:
                    ht.update(username, password)
                ht.save()
            return ('Add/update %s' % username, True)

def absent(dest, username, check_mode):
    """ Ensures user is absent

    Returns (msg, changed) """
    if LooseVersion(passlib.__version__) >= LooseVersion('1.6'):
        ht = HtpasswdFile(dest, new=False)
    else:
        ht = HtpasswdFile(dest)
    if username not in ht.users():
        return ('%s not present' % username, False)
    else:
        if not check_mode:
            ht.delete(username)
            ht.save()
        return ('Remove %s' % username, True)

def check_file_attrs(module, changed, message):
    file_args = module.load_file_common_arguments(module.params)
    if module.set_fs_attributes_if_different(file_args, False):
        if changed:
            message += ' and '
        changed = True
        message += 'ownership, perms or SE linux context changed'
    return (message, changed)

def main():
    arg_spec = dict(path=dict(required=True, aliases=['dest', 'destfile']), name=dict(required=True, aliases=['username']), password=dict(required=False, default=None, no_log=True), crypt_scheme=dict(required=False, default='apr_md5_crypt'), state=dict(required=False, default='present'), create=dict(type='bool', default='yes'))
    module = AnsibleModule(argument_spec=arg_spec, add_file_common_args=True, supports_check_mode=True)
    path = module.params['path']
    username = module.params['name']
    password = module.params['password']
    crypt_scheme = module.params['crypt_scheme']
    state = module.params['state']
    create = module.params['create']
    check_mode = module.check_mode
    if not passlib_installed:
        module.fail_json(msg=missing_required_lib('passlib'), exception=PASSLIB_IMP_ERR)
    try:
        f = open(path, 'r')
    except IOError:
        f = None
    else:
        try:
            lines = f.readlines()
        finally:
            f.close()
        strip = False
        for line in lines:
            if not line.strip():
                strip = True
                break
        if strip:
            if check_mode:
                temp = tempfile.NamedTemporaryFile()
                path = temp.name
            f = open(path, 'w')
            try:
                [f.write(line) for line in lines if line.strip()]
            finally:
                f.close()
    try:
        if state == 'present':
            (msg, changed) = present(path, username, password, crypt_scheme, create, check_mode)
        elif state == 'absent':
            if not os.path.exists(path):
                module.exit_json(msg='%s not present' % username, warnings='%s does not exist' % path, changed=False)
            (msg, changed) = absent(path, username, check_mode)
        else:
            module.fail_json(msg='Invalid state: %s' % state)
        check_file_attrs(module, changed, msg)
        module.exit_json(msg=msg, changed=changed)
    except Exception as e:
        module.fail_json(msg=to_native(e))
if __name__ == '__main__':
    main()