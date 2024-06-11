from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\n---\nmodule: test_docs_returns\nshort_description: Test module\ndescription:\n    - Test module\nauthor:\n    - Ansible Core Team\noptions:\n    test:\n        type: str\n'
EXAMPLES = '\n'
RETURN = '\n'
from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(argument_spec=dict(test=dict(type='str')))
    module.exit_json()
if __name__ == '__main__':
    main()