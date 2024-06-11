from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: sefcontext\nshort_description: Manages SELinux file context mapping definitions\ndescription:\n- Manages SELinux file context mapping definitions.\n- Similar to the C(semanage fcontext) command.\nversion_added: \'2.2\'\noptions:\n  target:\n    description:\n    - Target path (expression).\n    type: str\n    required: yes\n    aliases: [ path ]\n  ftype:\n    description:\n    - The file type that should have SELinux contexts applied.\n    - "The following file type options are available:"\n    - C(a) for all files,\n    - C(b) for block devices,\n    - C(c) for character devices,\n    - C(d) for directories,\n    - C(f) for regular files,\n    - C(l) for symbolic links,\n    - C(p) for named pipes,\n    - C(s) for socket files.\n    type: str\n    choices: [ a, b, c, d, f, l, p, s ]\n    default: a\n  setype:\n    description:\n    - SELinux type for the specified target.\n    type: str\n    required: yes\n  seuser:\n    description:\n    - SELinux user for the specified target.\n    type: str\n  selevel:\n    description:\n    - SELinux range for the specified target.\n    type: str\n    aliases: [ serange ]\n  state:\n    description:\n    - Whether the SELinux file context must be C(absent) or C(present).\n    type: str\n    choices: [ absent, present ]\n    default: present\n  reload:\n    description:\n    - Reload SELinux policy after commit.\n    - Note that this does not apply SELinux file contexts to existing files.\n    type: bool\n    default: yes\n  ignore_selinux_state:\n    description:\n    - Useful for scenarios (chrooted environment) that you can\'t get the real SELinux state.\n    type: bool\n    default: no\n    version_added: \'2.8\'\nnotes:\n- The changes are persistent across reboots.\n- The M(sefcontext) module does not modify existing files to the new\n  SELinux context(s), so it is advisable to first create the SELinux\n  file contexts before creating files, or run C(restorecon) manually\n  for the existing files that require the new SELinux file contexts.\n- Not applying SELinux fcontexts to existing files is a deliberate\n  decision as it would be unclear what reported changes would entail\n  to, and there\'s no guarantee that applying SELinux fcontext does\n  not pick up other unrelated prior changes.\nrequirements:\n- libselinux-python\n- policycoreutils-python\nauthor:\n- Dag Wieers (@dagwieers)\n'
EXAMPLES = "\n- name: Allow apache to modify files in /srv/git_repos\n  sefcontext:\n    target: '/srv/git_repos(/.*)?'\n    setype: httpd_git_rw_content_t\n    state: present\n\n- name: Apply new SELinux file context to filesystem\n  command: restorecon -irv /srv/git_repos\n"
RETURN = '\n# Default return values\n'
import traceback
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_native
SELINUX_IMP_ERR = None
try:
    import selinux
    HAVE_SELINUX = True
except ImportError:
    SELINUX_IMP_ERR = traceback.format_exc()
    HAVE_SELINUX = False
SEOBJECT_IMP_ERR = None
try:
    import seobject
    HAVE_SEOBJECT = True
except ImportError:
    SEOBJECT_IMP_ERR = traceback.format_exc()
    HAVE_SEOBJECT = False
if HAVE_SEOBJECT:
    seobject.file_types.update(a=seobject.SEMANAGE_FCONTEXT_ALL, b=seobject.SEMANAGE_FCONTEXT_BLOCK, c=seobject.SEMANAGE_FCONTEXT_CHAR, d=seobject.SEMANAGE_FCONTEXT_DIR, f=seobject.SEMANAGE_FCONTEXT_REG, l=seobject.SEMANAGE_FCONTEXT_LINK, p=seobject.SEMANAGE_FCONTEXT_PIPE, s=seobject.SEMANAGE_FCONTEXT_SOCK)
option_to_file_type_str = dict(a='all files', b='block device', c='character device', d='directory', f='regular file', l='symbolic link', p='named pipe', s='socket')

def get_runtime_status(ignore_selinux_state=False):
    return True if ignore_selinux_state is True else selinux.is_selinux_enabled()

def semanage_fcontext_exists(sefcontext, target, ftype):
    """ Get the SELinux file context mapping definition from policy. Return None if it does not exist. """
    record = (target, option_to_file_type_str[ftype])
    records = sefcontext.get_all()
    try:
        return records[record]
    except KeyError:
        return None

def semanage_fcontext_modify(module, result, target, ftype, setype, do_reload, serange, seuser, sestore=''):
    """ Add or modify SELinux file context mapping definition to the policy. """
    changed = False
    prepared_diff = ''
    try:
        sefcontext = seobject.fcontextRecords(sestore)
        sefcontext.set_reload(do_reload)
        exists = semanage_fcontext_exists(sefcontext, target, ftype)
        if exists:
            (orig_seuser, orig_serole, orig_setype, orig_serange) = exists
            if seuser is None:
                seuser = orig_seuser
            if serange is None:
                serange = orig_serange
            if setype != orig_setype or seuser != orig_seuser or serange != orig_serange:
                if not module.check_mode:
                    sefcontext.modify(target, setype, ftype, serange, seuser)
                changed = True
                if module._diff:
                    prepared_diff += '# Change to semanage file context mappings\n'
                    prepared_diff += '-%s      %s      %s:%s:%s:%s\n' % (target, ftype, orig_seuser, orig_serole, orig_setype, orig_serange)
                    prepared_diff += '+%s      %s      %s:%s:%s:%s\n' % (target, ftype, seuser, orig_serole, setype, serange)
        else:
            if seuser is None:
                seuser = 'system_u'
            if serange is None:
                serange = 's0'
            if not module.check_mode:
                sefcontext.add(target, setype, ftype, serange, seuser)
            changed = True
            if module._diff:
                prepared_diff += '# Addition to semanage file context mappings\n'
                prepared_diff += '+%s      %s      %s:%s:%s:%s\n' % (target, ftype, seuser, 'object_r', setype, serange)
    except Exception as e:
        module.fail_json(msg='%s: %s\n' % (e.__class__.__name__, to_native(e)))
    if module._diff and prepared_diff:
        result['diff'] = dict(prepared=prepared_diff)
    module.exit_json(changed=changed, seuser=seuser, serange=serange, **result)

def semanage_fcontext_delete(module, result, target, ftype, do_reload, sestore=''):
    """ Delete SELinux file context mapping definition from the policy. """
    changed = False
    prepared_diff = ''
    try:
        sefcontext = seobject.fcontextRecords(sestore)
        sefcontext.set_reload(do_reload)
        exists = semanage_fcontext_exists(sefcontext, target, ftype)
        if exists:
            (orig_seuser, orig_serole, orig_setype, orig_serange) = exists
            if not module.check_mode:
                sefcontext.delete(target, ftype)
            changed = True
            if module._diff:
                prepared_diff += '# Deletion to semanage file context mappings\n'
                prepared_diff += '-%s      %s      %s:%s:%s:%s\n' % (target, ftype, exists[0], exists[1], exists[2], exists[3])
    except Exception as e:
        module.fail_json(msg='%s: %s\n' % (e.__class__.__name__, to_native(e)))
    if module._diff and prepared_diff:
        result['diff'] = dict(prepared=prepared_diff)
    module.exit_json(changed=changed, **result)

def main():
    module = AnsibleModule(argument_spec=dict(ignore_selinux_state=dict(type='bool', default=False), target=dict(type='str', required=True, aliases=['path']), ftype=dict(type='str', default='a', choices=option_to_file_type_str.keys()), setype=dict(type='str', required=True), seuser=dict(type='str'), selevel=dict(type='str', aliases=['serange']), state=dict(type='str', default='present', choices=['absent', 'present']), reload=dict(type='bool', default=True)), supports_check_mode=True)
    if not HAVE_SELINUX:
        module.fail_json(msg=missing_required_lib('libselinux-python'), exception=SELINUX_IMP_ERR)
    if not HAVE_SEOBJECT:
        module.fail_json(msg=missing_required_lib('policycoreutils-python'), exception=SEOBJECT_IMP_ERR)
    ignore_selinux_state = module.params['ignore_selinux_state']
    if not get_runtime_status(ignore_selinux_state):
        module.fail_json(msg='SELinux is disabled on this host.')
    target = module.params['target']
    ftype = module.params['ftype']
    setype = module.params['setype']
    seuser = module.params['seuser']
    serange = module.params['selevel']
    state = module.params['state']
    do_reload = module.params['reload']
    result = dict(target=target, ftype=ftype, setype=setype, state=state)
    if state == 'present':
        semanage_fcontext_modify(module, result, target, ftype, setype, do_reload, serange, seuser)
    elif state == 'absent':
        semanage_fcontext_delete(module, result, target, ftype, do_reload)
    else:
        module.fail_json(msg='Invalid value of argument "state": {0}'.format(state))
if __name__ == '__main__':
    main()