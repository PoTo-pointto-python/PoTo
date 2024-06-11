from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['stableinterface'], 'supported_by': 'core'}
DOCUMENTATION = '\n---\nmodule: selinux\nshort_description: Change policy and state of SELinux\ndescription:\n  - Configures the SELinux mode and policy.\n  - A reboot may be required after usage.\n  - Ansible will not issue this reboot but will let you know when it is required.\nversion_added: "0.7"\noptions:\n  policy:\n    description:\n      - The name of the SELinux policy to use (e.g. C(targeted)) will be required if state is not C(disabled).\n  state:\n    description:\n      - The SELinux mode.\n    required: true\n    choices: [ disabled, enforcing, permissive ]\n  configfile:\n    description:\n      - The path to the SELinux configuration file, if non-standard.\n    default: /etc/selinux/config\n    aliases: [ conf, file ]\nrequirements: [ libselinux-python ]\nauthor:\n- Derek Carter (@goozbach) <goozbach@friocorte.com>\n'
EXAMPLES = '\n- name: Enable SELinux\n  selinux:\n    policy: targeted\n    state: enforcing\n\n- name: Put SELinux in permissive mode, logging actions that would be blocked.\n  selinux:\n    policy: targeted\n    state: permissive\n\n- name: Disable SELinux\n  selinux:\n    state: disabled\n'
RETURN = "\nmsg:\n    description: Messages that describe changes that were made.\n    returned: always\n    type: str\n    sample: Config SELinux state changed from 'disabled' to 'permissive'\nconfigfile:\n    description: Path to SELinux configuration file.\n    returned: always\n    type: str\n    sample: /etc/selinux/config\npolicy:\n    description: Name of the SELinux policy.\n    returned: always\n    type: str\n    sample: targeted\nstate:\n    description: SELinux mode.\n    returned: always\n    type: str\n    sample: enforcing\nreboot_required:\n    description: Whether or not an reboot is required for the changes to take effect.\n    returned: always\n    type: bool\n    sample: true\n"
import os
import re
import tempfile
import traceback
SELINUX_IMP_ERR = None
try:
    import selinux
    HAS_SELINUX = True
except ImportError:
    SELINUX_IMP_ERR = traceback.format_exc()
    HAS_SELINUX = False
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.facts.utils import get_file_lines

def get_config_state(configfile):
    lines = get_file_lines(configfile, strip=False)
    for line in lines:
        stateline = re.match('^SELINUX=.*$', line)
        if stateline:
            return line.split('=')[1].strip()

def get_config_policy(configfile):
    lines = get_file_lines(configfile, strip=False)
    for line in lines:
        stateline = re.match('^SELINUXTYPE=.*$', line)
        if stateline:
            return line.split('=')[1].strip()

def set_config_state(module, state, configfile):
    stateline = 'SELINUX=%s' % state
    lines = get_file_lines(configfile, strip=False)
    (tmpfd, tmpfile) = tempfile.mkstemp()
    with open(tmpfile, 'w') as write_file:
        for line in lines:
            write_file.write(re.sub('^SELINUX=.*', stateline, line) + '\n')
    module.atomic_move(tmpfile, configfile)

def set_state(module, state):
    if state == 'enforcing':
        selinux.security_setenforce(1)
    elif state == 'permissive':
        selinux.security_setenforce(0)
    elif state == 'disabled':
        pass
    else:
        msg = 'trying to set invalid runtime state %s' % state
        module.fail_json(msg=msg)

def set_config_policy(module, policy, configfile):
    if not os.path.exists('/etc/selinux/%s/policy' % policy):
        module.fail_json(msg='Policy %s does not exist in /etc/selinux/' % policy)
    policyline = 'SELINUXTYPE=%s' % policy
    lines = get_file_lines(configfile, strip=False)
    (tmpfd, tmpfile) = tempfile.mkstemp()
    with open(tmpfile, 'w') as write_file:
        for line in lines:
            write_file.write(re.sub('^SELINUXTYPE=.*', policyline, line) + '\n')
    module.atomic_move(tmpfile, configfile)

def main():
    module = AnsibleModule(argument_spec=dict(policy=dict(type='str'), state=dict(type='str', required='True', choices=['enforcing', 'permissive', 'disabled']), configfile=dict(type='str', default='/etc/selinux/config', aliases=['conf', 'file'])), supports_check_mode=True)
    if not HAS_SELINUX:
        module.fail_json(msg=missing_required_lib('libselinux-python'), exception=SELINUX_IMP_ERR)
    changed = False
    msgs = []
    configfile = module.params['configfile']
    policy = module.params['policy']
    state = module.params['state']
    runtime_enabled = selinux.is_selinux_enabled()
    runtime_policy = selinux.selinux_getpolicytype()[1]
    runtime_state = 'disabled'
    reboot_required = False
    if runtime_enabled:
        if selinux.security_getenforce():
            runtime_state = 'enforcing'
        else:
            runtime_state = 'permissive'
    if not os.path.isfile(configfile):
        module.fail_json(msg='Unable to find file {0}'.format(configfile), details='Please install SELinux-policy package, if this package is not installed previously.')
    config_policy = get_config_policy(configfile)
    config_state = get_config_state(configfile)
    if state != 'disabled':
        if not policy:
            module.fail_json(msg="Policy is required if state is not 'disabled'")
    elif not policy:
        policy = config_policy
    if policy != runtime_policy:
        if module.check_mode:
            module.exit_json(changed=True)
        msgs.append("Running SELinux policy changed from '%s' to '%s'" % (runtime_policy, policy))
        changed = True
    if policy != config_policy:
        if module.check_mode:
            module.exit_json(changed=True)
        set_config_policy(module, policy, configfile)
        msgs.append("SELinux policy configuration in '%s' changed from '%s' to '%s'" % (configfile, config_policy, policy))
        changed = True
    if state != runtime_state:
        if runtime_enabled:
            if state == 'disabled':
                if runtime_state != 'permissive':
                    if not module.check_mode:
                        set_state(module, 'permissive')
                    module.warn("SELinux state temporarily changed from '%s' to 'permissive'. State change will take effect next reboot." % runtime_state)
                    changed = True
                else:
                    module.warn('SELinux state change will take effect next reboot')
                reboot_required = True
            else:
                if not module.check_mode:
                    set_state(module, state)
                msgs.append("SELinux state changed from '%s' to '%s'" % (runtime_state, state))
                changed = True
        else:
            module.warn("Reboot is required to set SELinux state to '%s'" % state)
            reboot_required = True
    if state != config_state:
        if not module.check_mode:
            set_config_state(module, state, configfile)
        msgs.append("Config SELinux state changed from '%s' to '%s'" % (config_state, state))
        changed = True
    module.exit_json(changed=changed, msg=', '.join(msgs), configfile=configfile, policy=policy, state=state, reboot_required=reboot_required)
if __name__ == '__main__':
    main()