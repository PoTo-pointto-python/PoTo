from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\nmodule: bad\nshort_description: Bad test module\ndescription: Bad test module.\nauthor:\n  - Ansible Core Team\n'
EXAMPLES = '\n- bad:\n'
RETURN = ''
from ansible.module_utils.basic import AnsibleModule
from ansible import constants

def main():
    module = AnsibleModule(argument_spec=dict())
    module.exit_json()
if __name__ == '__main__':
    main()