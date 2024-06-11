from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(argument_spec=dict())
    result = {'selinux_special_fs': module._selinux_special_fs, 'tmpdir': module._tmpdir, 'keep_remote_files': module._keep_remote_files, 'version': module.ansible_version}
    module.exit_json(**result)
if __name__ == '__main__':
    main()