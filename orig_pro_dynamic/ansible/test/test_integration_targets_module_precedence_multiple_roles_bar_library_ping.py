from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['stableinterface'], 'supported_by': 'core'}
DOCUMENTATION = '\n---\nmodule: ping\nversion_added: historical\nshort_description: Try to connect to host, verify a usable python and return C(pong) on success.\ndescription:\n   - A trivial test module, this module always returns C(pong) on successful\n     contact. It does not make sense in playbooks, but it is useful from\n     C(/usr/bin/ansible) to verify the ability to login and that a usable python is configured.\n   - This is NOT ICMP ping, this is just a trivial test module.\noptions: {}\nauthor:\n    - "Ansible Core Team"\n    - "Michael DeHaan"\n'
EXAMPLES = "\n# Test we can logon to 'webservers' and execute python with json lib.\nansible webservers -m ping\n"
from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(argument_spec=dict(data=dict(required=False, default=None)), supports_check_mode=True)
    result = dict(ping='pong')
    if module.params['data']:
        if module.params['data'] == 'crash':
            raise Exception('boom')
        result['ping'] = module.params['data']
    result['location'] = 'role: bar'
    module.exit_json(**result)
if __name__ == '__main__':
    main()