from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['removed'], 'supported_by': 'core'}
DOCUMENTATION = '\n---\nmodule: test_docs_removed_status\nshort_description: Test module\ndescription:\n    - Test module\nauthor:\n    - Ansible Core Team\n'
EXAMPLES = '\n'
RETURN = '\n'
from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(argument_spec=dict())
    module.exit_json()
if __name__ == '__main__':
    main()