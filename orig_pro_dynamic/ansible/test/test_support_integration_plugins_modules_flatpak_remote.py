from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = "\n---\nmodule: flatpak_remote\nversion_added: '2.6'\nshort_description: Manage flatpak repository remotes\ndescription:\n- Allows users to add or remove flatpak remotes.\n- The flatpak remotes concept is comparable to what is called repositories in other packaging\n  formats.\n- Currently, remote addition is only supported via I(flatpakrepo) file URLs.\n- Existing remotes will not be updated.\n- See the M(flatpak) module for managing flatpaks.\nauthor:\n- John Kwiatkoski (@JayKayy)\n- Alexander Bethke (@oolongbrothers)\nrequirements:\n- flatpak\noptions:\n  executable:\n    description:\n    - The path to the C(flatpak) executable to use.\n    - By default, this module looks for the C(flatpak) executable on the path.\n    default: flatpak\n  flatpakrepo_url:\n    description:\n    - The URL to the I(flatpakrepo) file representing the repository remote to add.\n    - When used with I(state=present), the flatpak remote specified under the I(flatpakrepo_url)\n      is added using the specified installation C(method).\n    - When used with I(state=absent), this is not required.\n    - Required when I(state=present).\n  method:\n    description:\n    - The installation method to use.\n    - Defines if the I(flatpak) is supposed to be installed globally for the whole C(system)\n      or only for the current C(user).\n    choices: [ system, user ]\n    default: system\n  name:\n    description:\n    - The desired name for the flatpak remote to be registered under on the managed host.\n    - When used with I(state=present), the remote will be added to the managed host under\n      the specified I(name).\n    - When used with I(state=absent) the remote with that name will be removed.\n    required: true\n  state:\n    description:\n    - Indicates the desired package state.\n    choices: [ absent, present ]\n    default: present\n"
EXAMPLES = '\n- name: Add the Gnome flatpak remote to the system installation\n  flatpak_remote:\n    name: gnome\n    state: present\n    flatpakrepo_url: https://sdk.gnome.org/gnome-apps.flatpakrepo\n\n- name: Add the flathub flatpak repository remote to the user installation\n  flatpak_remote:\n    name: flathub\n    state: present\n    flatpakrepo_url: https://dl.flathub.org/repo/flathub.flatpakrepo\n    method: user\n\n- name: Remove the Gnome flatpak remote from the user installation\n  flatpak_remote:\n    name: gnome\n    state: absent\n    method: user\n\n- name: Remove the flathub remote from the system installation\n  flatpak_remote:\n    name: flathub\n    state: absent\n'
RETURN = '\ncommand:\n  description: The exact flatpak command that was executed\n  returned: When a flatpak command has been executed\n  type: str\n  sample: "/usr/bin/flatpak remote-add --system flatpak-test https://dl.flathub.org/repo/flathub.flatpakrepo"\nmsg:\n  description: Module error message\n  returned: failure\n  type: str\n  sample: "Executable \'/usr/local/bin/flatpak\' was not found on the system."\nrc:\n  description: Return code from flatpak binary\n  returned: When a flatpak command has been executed\n  type: int\n  sample: 0\nstderr:\n  description: Error output from flatpak binary\n  returned: When a flatpak command has been executed\n  type: str\n  sample: "error: GPG verification enabled, but no summary found (check that the configured URL in remote config is correct)\\n"\nstdout:\n  description: Output from flatpak binary\n  returned: When a flatpak command has been executed\n  type: str\n  sample: "flathub\\tFlathub\\thttps://dl.flathub.org/repo/\\t1\\t\\n"\n'
import subprocess
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes, to_native

def add_remote(module, binary, name, flatpakrepo_url, method):
    """Add a new remote."""
    global result
    command = '{0} remote-add --{1} {2} {3}'.format(binary, method, name, flatpakrepo_url)
    _flatpak_command(module, module.check_mode, command)
    result['changed'] = True

def remove_remote(module, binary, name, method):
    """Remove an existing remote."""
    global result
    command = '{0} remote-delete --{1} --force {2} '.format(binary, method, name)
    _flatpak_command(module, module.check_mode, command)
    result['changed'] = True

def remote_exists(module, binary, name, method):
    """Check if the remote exists."""
    command = '{0} remote-list -d --{1}'.format(binary, method)
    output = _flatpak_command(module, False, command)
    for line in output.splitlines():
        listed_remote = line.split()
        if len(listed_remote) == 0:
            continue
        if listed_remote[0] == to_native(name):
            return True
    return False

def _flatpak_command(module, noop, command):
    global result
    if noop:
        result['rc'] = 0
        result['command'] = command
        return ''
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout_data, stderr_data) = process.communicate()
    result['rc'] = process.returncode
    result['command'] = command
    result['stdout'] = stdout_data
    result['stderr'] = stderr_data
    if result['rc'] != 0:
        module.fail_json(msg='Failed to execute flatpak command', **result)
    return to_native(stdout_data)

def main():
    module = AnsibleModule(argument_spec=dict(name=dict(type='str', required=True), flatpakrepo_url=dict(type='str'), method=dict(type='str', default='system', choices=['user', 'system']), state=dict(type='str', default='present', choices=['absent', 'present']), executable=dict(type='str', default='flatpak')), supports_check_mode=True)
    name = module.params['name']
    flatpakrepo_url = module.params['flatpakrepo_url']
    method = module.params['method']
    state = module.params['state']
    executable = module.params['executable']
    binary = module.get_bin_path(executable, None)
    if flatpakrepo_url is None:
        flatpakrepo_url = ''
    global result
    result = dict(changed=False)
    if not binary:
        module.fail_json(msg="Executable '%s' was not found on the system." % executable, **result)
    remote_already_exists = remote_exists(module, binary, to_bytes(name), method)
    if state == 'present' and (not remote_already_exists):
        add_remote(module, binary, name, flatpakrepo_url, method)
    elif state == 'absent' and remote_already_exists:
        remove_remote(module, binary, name, method)
    module.exit_json(**result)
if __name__ == '__main__':
    main()