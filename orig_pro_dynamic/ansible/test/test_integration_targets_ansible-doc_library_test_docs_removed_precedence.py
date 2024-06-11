from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = "\n---\nmodule: test_docs_removed_precedence\nshort_description: Test module\ndescription:\n    - Test module\nauthor:\n    - Ansible Core Team\ndeprecated:\n  alternative: new_module\n  why: Updated module released with more functionality\n  removed_at_date: '2022-06-01'\n  removed_in: '2.14'\n"
EXAMPLES = '\n'
RETURN = '\n'
from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(argument_spec=dict())
    module.exit_json()
if __name__ == '__main__':
    main()