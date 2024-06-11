from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: zypper\nauthor:\n    - "Patrick Callahan (@dirtyharrycallahan)"\n    - "Alexander Gubin (@alxgu)"\n    - "Thomas O\'Donnell (@andytom)"\n    - "Robin Roth (@robinro)"\n    - "Andrii Radyk (@AnderEnder)"\nversion_added: "1.2"\nshort_description: Manage packages on SUSE and openSUSE\ndescription:\n    - Manage packages on SUSE and openSUSE using the zypper and rpm tools.\noptions:\n    name:\n        description:\n        - Package name C(name) or package specifier or a list of either.\n        - Can include a version like C(name=1.0), C(name>3.4) or C(name<=2.7). If a version is given, C(oldpackage) is implied and zypper is allowed to\n          update the package within the version range given.\n        - You can also pass a url or a local path to a rpm file.\n        - When using state=latest, this can be \'*\', which updates all installed packages.\n        required: true\n        aliases: [ \'pkg\' ]\n    state:\n        description:\n          - C(present) will make sure the package is installed.\n            C(latest)  will make sure the latest version of the package is installed.\n            C(absent)  will make sure the specified package is not installed.\n            C(dist-upgrade) will make sure the latest version of all installed packages from all enabled repositories is installed.\n          - When using C(dist-upgrade), I(name) should be C(\'*\').\n        required: false\n        choices: [ present, latest, absent, dist-upgrade ]\n        default: "present"\n    type:\n        description:\n          - The type of package to be operated on.\n        required: false\n        choices: [ package, patch, pattern, product, srcpackage, application ]\n        default: "package"\n        version_added: "2.0"\n    extra_args_precommand:\n       version_added: "2.6"\n       required: false\n       description:\n         - Add additional global target options to C(zypper).\n         - Options should be supplied in a single line as if given in the command line.\n    disable_gpg_check:\n        description:\n          - Whether to disable to GPG signature checking of the package\n            signature being installed. Has an effect only if state is\n            I(present) or I(latest).\n        required: false\n        default: "no"\n        type: bool\n    disable_recommends:\n        version_added: "1.8"\n        description:\n          - Corresponds to the C(--no-recommends) option for I(zypper). Default behavior (C(yes)) modifies zypper\'s default behavior; C(no) does\n            install recommended packages.\n        required: false\n        default: "yes"\n        type: bool\n    force:\n        version_added: "2.2"\n        description:\n          - Adds C(--force) option to I(zypper). Allows to downgrade packages and change vendor or architecture.\n        required: false\n        default: "no"\n        type: bool\n    force_resolution:\n        version_added: "2.10"\n        description:\n          - Adds C(--force-resolution) option to I(zypper). Allows to (un)install packages with conflicting requirements (resolver will choose a solution).\n        required: false\n        default: "no"\n        type: bool\n    update_cache:\n        version_added: "2.2"\n        description:\n          - Run the equivalent of C(zypper refresh) before the operation. Disabled in check mode.\n        required: false\n        default: "no"\n        type: bool\n        aliases: [ "refresh" ]\n    oldpackage:\n        version_added: "2.2"\n        description:\n          - Adds C(--oldpackage) option to I(zypper). Allows to downgrade packages with less side-effects than force. This is implied as soon as a\n            version is specified as part of the package name.\n        required: false\n        default: "no"\n        type: bool\n    extra_args:\n        version_added: "2.4"\n        required: false\n        description:\n          - Add additional options to C(zypper) command.\n          - Options should be supplied in a single line as if given in the command line.\nnotes:\n  - When used with a `loop:` each package will be processed individually,\n    it is much more efficient to pass the list directly to the `name` option.\n# informational: requirements for nodes\nrequirements:\n    - "zypper >= 1.0  # included in openSUSE >= 11.1 or SUSE Linux Enterprise Server/Desktop >= 11.0"\n    - python-xml\n    - rpm\n'
EXAMPLES = '\n# Install "nmap"\n- zypper:\n    name: nmap\n    state: present\n\n# Install apache2 with recommended packages\n- zypper:\n    name: apache2\n    state: present\n    disable_recommends: no\n\n# Apply a given patch\n- zypper:\n    name: openSUSE-2016-128\n    state: present\n    type: patch\n\n# Remove the "nmap" package\n- zypper:\n    name: nmap\n    state: absent\n\n# Install the nginx rpm from a remote repo\n- zypper:\n    name: \'http://nginx.org/packages/sles/12/x86_64/RPMS/nginx-1.8.0-1.sles12.ngx.x86_64.rpm\'\n    state: present\n\n# Install local rpm file\n- zypper:\n    name: /tmp/fancy-software.rpm\n    state: present\n\n# Update all packages\n- zypper:\n    name: \'*\'\n    state: latest\n\n# Apply all available patches\n- zypper:\n    name: \'*\'\n    state: latest\n    type: patch\n\n# Perform a dist-upgrade with additional arguments\n- zypper:\n    name: \'*\'\n    state: dist-upgrade\n    extra_args: \'--no-allow-vendor-change --allow-arch-change\'\n\n# Refresh repositories and update package "openssl"\n- zypper:\n    name: openssl\n    state: present\n    update_cache: yes\n\n# Install specific version (possible comparisons: <, >, <=, >=, =)\n- zypper:\n    name: \'docker>=1.10\'\n    state: present\n\n# Wait 20 seconds to acquire the lock before failing\n- zypper:\n    name: mosh\n    state: present\n  environment:\n    ZYPP_LOCK_TIMEOUT: 20\n'
import xml
import re
from xml.dom.minidom import parseString as parseXML
from ansible.module_utils.six import iteritems
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule

class Package:

    def __init__(self, name, prefix, version):
        self.name = name
        self.prefix = prefix
        self.version = version
        self.shouldinstall = prefix == '+'

    def __str__(self):
        return self.prefix + self.name + self.version

def split_name_version(name):
    """splits of the package name and desired version

    example formats:
        - docker>=1.10
        - apache=2.4

    Allowed version specifiers: <, >, <=, >=, =
    Allowed version format: [0-9.-]*

    Also allows a prefix indicating remove "-", "~" or install "+"
    """
    prefix = ''
    if name[0] in ['-', '~', '+']:
        prefix = name[0]
        name = name[1:]
    if prefix == '~':
        prefix = '-'
    version_check = re.compile('^(.*?)((?:<|>|<=|>=|=)[0-9.-]*)?$')
    try:
        reres = version_check.match(name)
        (name, version) = reres.groups()
        if version is None:
            version = ''
        return (prefix, name, version)
    except Exception:
        return (prefix, name, '')

def get_want_state(names, remove=False):
    packages = []
    urls = []
    for name in names:
        if '://' in name or name.endswith('.rpm'):
            urls.append(name)
        else:
            (prefix, pname, version) = split_name_version(name)
            if prefix not in ['-', '+']:
                if remove:
                    prefix = '-'
                else:
                    prefix = '+'
            packages.append(Package(pname, prefix, version))
    return (packages, urls)

def get_installed_state(m, packages):
    """get installed state of packages"""
    cmd = get_cmd(m, 'search')
    cmd.extend(['--match-exact', '--details', '--installed-only'])
    cmd.extend([p.name for p in packages])
    return parse_zypper_xml(m, cmd, fail_not_found=False)[0]

def parse_zypper_xml(m, cmd, fail_not_found=True, packages=None):
    (rc, stdout, stderr) = m.run_command(cmd, check_rc=False)
    try:
        dom = parseXML(stdout)
    except xml.parsers.expat.ExpatError as exc:
        m.fail_json(msg='Failed to parse zypper xml output: %s' % to_native(exc), rc=rc, stdout=stdout, stderr=stderr, cmd=cmd)
    if rc == 104:
        if fail_not_found:
            errmsg = dom.getElementsByTagName('message')[-1].childNodes[0].data
            m.fail_json(msg=errmsg, rc=rc, stdout=stdout, stderr=stderr, cmd=cmd)
        else:
            return ({}, rc, stdout, stderr)
    elif rc in [0, 106, 103]:
        if packages is None:
            firstrun = True
            packages = {}
        solvable_list = dom.getElementsByTagName('solvable')
        for solvable in solvable_list:
            name = solvable.getAttribute('name')
            packages[name] = {}
            packages[name]['version'] = solvable.getAttribute('edition')
            packages[name]['oldversion'] = solvable.getAttribute('edition-old')
            status = solvable.getAttribute('status')
            packages[name]['installed'] = status == 'installed'
            packages[name]['group'] = solvable.parentNode.nodeName
        if rc == 103 and firstrun:
            return parse_zypper_xml(m, cmd, fail_not_found=fail_not_found, packages=packages)
        return (packages, rc, stdout, stderr)
    m.fail_json(msg='Zypper run command failed with return code %s.' % rc, rc=rc, stdout=stdout, stderr=stderr, cmd=cmd)

def get_cmd(m, subcommand):
    """puts together the basic zypper command arguments with those passed to the module"""
    is_install = subcommand in ['install', 'update', 'patch', 'dist-upgrade']
    is_refresh = subcommand == 'refresh'
    cmd = ['/usr/bin/zypper', '--quiet', '--non-interactive', '--xmlout']
    if m.params['extra_args_precommand']:
        args_list = m.params['extra_args_precommand'].split()
        cmd.extend(args_list)
    if (is_install or is_refresh) and m.params['disable_gpg_check']:
        cmd.append('--no-gpg-checks')
    if subcommand == 'search':
        cmd.append('--disable-repositories')
    cmd.append(subcommand)
    if subcommand not in ['patch', 'dist-upgrade'] and (not is_refresh):
        cmd.extend(['--type', m.params['type']])
    if m.check_mode and subcommand != 'search':
        cmd.append('--dry-run')
    if is_install:
        cmd.append('--auto-agree-with-licenses')
        if m.params['disable_recommends']:
            cmd.append('--no-recommends')
        if m.params['force']:
            cmd.append('--force')
        if m.params['force_resolution']:
            cmd.append('--force-resolution')
        if m.params['oldpackage']:
            cmd.append('--oldpackage')
    if m.params['extra_args']:
        args_list = m.params['extra_args'].split(' ')
        cmd.extend(args_list)
    return cmd

def set_diff(m, retvals, result):
    packages = {'installed': [], 'removed': [], 'upgraded': []}
    if result:
        for p in result:
            group = result[p]['group']
            if group == 'to-upgrade':
                versions = ' (' + result[p]['oldversion'] + ' => ' + result[p]['version'] + ')'
                packages['upgraded'].append(p + versions)
            elif group == 'to-install':
                packages['installed'].append(p)
            elif group == 'to-remove':
                packages['removed'].append(p)
    output = ''
    for state in packages:
        if packages[state]:
            output += state + ': ' + ', '.join(packages[state]) + '\n'
    if 'diff' not in retvals:
        retvals['diff'] = {}
    if 'prepared' not in retvals['diff']:
        retvals['diff']['prepared'] = output
    else:
        retvals['diff']['prepared'] += '\n' + output

def package_present(m, name, want_latest):
    """install and update (if want_latest) the packages in name_install, while removing the packages in name_remove"""
    retvals = {'rc': 0, 'stdout': '', 'stderr': ''}
    (packages, urls) = get_want_state(name)
    if any((p.version for p in packages)):
        m.params['oldpackage'] = True
    if not want_latest:
        packageswithoutversion = [p for p in packages if not p.version]
        prerun_state = get_installed_state(m, packageswithoutversion)
        packages = [p for p in packages if p.shouldinstall != (p.name in prerun_state)]
    if not packages and (not urls):
        return (None, retvals)
    cmd = get_cmd(m, 'install')
    cmd.append('--')
    cmd.extend(urls)
    cmd.extend([str(p) for p in packages])
    retvals['cmd'] = cmd
    (result, retvals['rc'], retvals['stdout'], retvals['stderr']) = parse_zypper_xml(m, cmd)
    return (result, retvals)

def package_update_all(m):
    """run update or patch on all available packages"""
    retvals = {'rc': 0, 'stdout': '', 'stderr': ''}
    if m.params['type'] == 'patch':
        cmdname = 'patch'
    elif m.params['state'] == 'dist-upgrade':
        cmdname = 'dist-upgrade'
    else:
        cmdname = 'update'
    cmd = get_cmd(m, cmdname)
    retvals['cmd'] = cmd
    (result, retvals['rc'], retvals['stdout'], retvals['stderr']) = parse_zypper_xml(m, cmd)
    return (result, retvals)

def package_absent(m, name):
    """remove the packages in name"""
    retvals = {'rc': 0, 'stdout': '', 'stderr': ''}
    (packages, urls) = get_want_state(name, remove=True)
    if any((p.prefix == '+' for p in packages)):
        m.fail_json(msg="Can not combine '+' prefix with state=remove/absent.")
    if urls:
        m.fail_json(msg='Can not remove via URL.')
    if m.params['type'] == 'patch':
        m.fail_json(msg='Can not remove patches.')
    prerun_state = get_installed_state(m, packages)
    packages = [p for p in packages if p.name in prerun_state]
    if not packages:
        return (None, retvals)
    cmd = get_cmd(m, 'remove')
    cmd.extend([p.name + p.version for p in packages])
    retvals['cmd'] = cmd
    (result, retvals['rc'], retvals['stdout'], retvals['stderr']) = parse_zypper_xml(m, cmd)
    return (result, retvals)

def repo_refresh(m):
    """update the repositories"""
    retvals = {'rc': 0, 'stdout': '', 'stderr': ''}
    cmd = get_cmd(m, 'refresh')
    retvals['cmd'] = cmd
    (result, retvals['rc'], retvals['stdout'], retvals['stderr']) = parse_zypper_xml(m, cmd)
    return retvals

def main():
    module = AnsibleModule(argument_spec=dict(name=dict(required=True, aliases=['pkg'], type='list'), state=dict(required=False, default='present', choices=['absent', 'installed', 'latest', 'present', 'removed', 'dist-upgrade']), type=dict(required=False, default='package', choices=['package', 'patch', 'pattern', 'product', 'srcpackage', 'application']), extra_args_precommand=dict(required=False, default=None), disable_gpg_check=dict(required=False, default='no', type='bool'), disable_recommends=dict(required=False, default='yes', type='bool'), force=dict(required=False, default='no', type='bool'), force_resolution=dict(required=False, default='no', type='bool'), update_cache=dict(required=False, aliases=['refresh'], default='no', type='bool'), oldpackage=dict(required=False, default='no', type='bool'), extra_args=dict(required=False, default=None)), supports_check_mode=True)
    name = module.params['name']
    state = module.params['state']
    update_cache = module.params['update_cache']
    name = list(filter(None, name))
    if update_cache and (not module.check_mode):
        retvals = repo_refresh(module)
        if retvals['rc'] != 0:
            module.fail_json(msg='Zypper refresh run failed.', **retvals)
    if name == ['*'] and state in ['latest', 'dist-upgrade']:
        (packages_changed, retvals) = package_update_all(module)
    elif name != ['*'] and state == 'dist-upgrade':
        module.fail_json(msg='Can not dist-upgrade specific packages.')
    elif state in ['absent', 'removed']:
        (packages_changed, retvals) = package_absent(module, name)
    elif state in ['installed', 'present', 'latest']:
        (packages_changed, retvals) = package_present(module, name, state == 'latest')
    retvals['changed'] = retvals['rc'] == 0 and bool(packages_changed)
    if module._diff:
        set_diff(module, retvals, packages_changed)
    if retvals['rc'] != 0:
        module.fail_json(msg='Zypper run failed.', **retvals)
    if not retvals['changed']:
        del retvals['stdout']
        del retvals['stderr']
    module.exit_json(name=name, state=state, update_cache=update_cache, **retvals)
if __name__ == '__main__':
    main()

def test_Package___str__():
    ret = Package().__str__()