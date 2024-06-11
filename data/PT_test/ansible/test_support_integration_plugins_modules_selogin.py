from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: selogin\nshort_description: Manages linux user to SELinux user mapping\ndescription:\n     - Manages linux user to SELinux user mapping\nversion_added: "2.8"\noptions:\n  login:\n    description:\n      - a Linux user\n    required: true\n  seuser:\n    description:\n      - SELinux user name\n    required: true\n  selevel:\n    aliases: [ serange ]\n    description:\n      - MLS/MCS Security Range (MLS/MCS Systems only) SELinux Range for SELinux login mapping defaults to the SELinux user record range.\n    default: s0\n  state:\n    description:\n      - Desired mapping value.\n    required: true\n    default: present\n    choices: [ \'present\', \'absent\' ]\n  reload:\n    description:\n      - Reload SELinux policy after commit.\n    default: yes\n  ignore_selinux_state:\n    description:\n    - Run independent of selinux runtime state\n    type: bool\n    default: false\nnotes:\n   - The changes are persistent across reboots\n   - Not tested on any debian based system\nrequirements: [ \'libselinux\', \'policycoreutils\' ]\nauthor:\n- Dan Keder (@dankeder)\n- Petr Lautrbach (@bachradsusi)\n- James Cassell (@jamescassell)\n'
EXAMPLES = "\n# Modify the default user on the system to the guest_u user\n- selogin:\n    login: __default__\n    seuser: guest_u\n    state: present\n\n# Assign gijoe user on an MLS machine a range and to the staff_u user\n- selogin:\n    login: gijoe\n    seuser: staff_u\n    serange: SystemLow-Secret\n    state: present\n\n# Assign all users in the engineering group to the staff_u user\n- selogin:\n    login: '%engineering'\n    seuser: staff_u\n    state: present\n"
RETURN = '\n# Default return values\n'
import traceback
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
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_native

def semanage_login_add(module, login, seuser, do_reload, serange='s0', sestore=''):
    """ Add linux user to SELinux user mapping

    :type module: AnsibleModule
    :param module: Ansible module

    :type login: str
    :param login: a Linux User or a Linux group if it begins with %

    :type seuser: str
    :param proto: An SELinux user ('__default__', 'unconfined_u', 'staff_u', ...), see 'semanage login -l'

    :type serange: str
    :param serange: SELinux MLS/MCS range (defaults to 's0')

    :type do_reload: bool
    :param do_reload: Whether to reload SELinux policy after commit

    :type sestore: str
    :param sestore: SELinux store

    :rtype: bool
    :return: True if the policy was changed, otherwise False
    """
    try:
        selogin = seobject.loginRecords(sestore)
        selogin.set_reload(do_reload)
        change = False
        all_logins = selogin.get_all()
        if login not in all_logins.keys():
            change = True
            if not module.check_mode:
                selogin.add(login, seuser, serange)
        elif all_logins[login][0] != seuser or all_logins[login][1] != serange:
            change = True
            if not module.check_mode:
                selogin.modify(login, seuser, serange)
    except (ValueError, KeyError, OSError, RuntimeError) as e:
        module.fail_json(msg='%s: %s\n' % (e.__class__.__name__, to_native(e)), exception=traceback.format_exc())
    return change

def semanage_login_del(module, login, seuser, do_reload, sestore=''):
    """ Delete linux user to SELinux user mapping

    :type module: AnsibleModule
    :param module: Ansible module

    :type login: str
    :param login: a Linux User or a Linux group if it begins with %

    :type seuser: str
    :param proto: An SELinux user ('__default__', 'unconfined_u', 'staff_u', ...), see 'semanage login -l'

    :type do_reload: bool
    :param do_reload: Whether to reload SELinux policy after commit

    :type sestore: str
    :param sestore: SELinux store

    :rtype: bool
    :return: True if the policy was changed, otherwise False
    """
    try:
        selogin = seobject.loginRecords(sestore)
        selogin.set_reload(do_reload)
        change = False
        all_logins = selogin.get_all()
        if login in all_logins.keys():
            change = True
            if not module.check_mode:
                selogin.delete(login)
    except (ValueError, KeyError, OSError, RuntimeError) as e:
        module.fail_json(msg='%s: %s\n' % (e.__class__.__name__, to_native(e)), exception=traceback.format_exc())
    return change

def get_runtime_status(ignore_selinux_state=False):
    return True if ignore_selinux_state is True else selinux.is_selinux_enabled()

def main():
    module = AnsibleModule(argument_spec=dict(ignore_selinux_state=dict(type='bool', default=False), login=dict(type='str', required=True), seuser=dict(type='str'), selevel=dict(type='str', aliases=['serange'], default='s0'), state=dict(type='str', default='present', choices=['absent', 'present']), reload=dict(type='bool', default=True)), required_if=[['state', 'present', ['seuser']]], supports_check_mode=True)
    if not HAVE_SELINUX:
        module.fail_json(msg=missing_required_lib('libselinux'), exception=SELINUX_IMP_ERR)
    if not HAVE_SEOBJECT:
        module.fail_json(msg=missing_required_lib('seobject from policycoreutils'), exception=SEOBJECT_IMP_ERR)
    ignore_selinux_state = module.params['ignore_selinux_state']
    if not get_runtime_status(ignore_selinux_state):
        module.fail_json(msg='SELinux is disabled on this host.')
    login = module.params['login']
    seuser = module.params['seuser']
    serange = module.params['selevel']
    state = module.params['state']
    do_reload = module.params['reload']
    result = {'login': login, 'seuser': seuser, 'serange': serange, 'state': state}
    if state == 'present':
        result['changed'] = semanage_login_add(module, login, seuser, do_reload, serange)
    elif state == 'absent':
        result['changed'] = semanage_login_del(module, login, seuser, do_reload)
    else:
        module.fail_json(msg='Invalid value of argument "state": {0}'.format(state))
    module.exit_json(**result)
if __name__ == '__main__':
    main()