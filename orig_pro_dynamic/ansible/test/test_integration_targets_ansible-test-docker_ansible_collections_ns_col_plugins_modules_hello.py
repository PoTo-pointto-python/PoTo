from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\nmodule: hello\nshort_description: Hello test module\ndescription: Hello test module.\noptions:\n  name:\n    description: Name to say hello to.\n    type: str\nauthor:\n  - Ansible Core Team\n'
EXAMPLES = '\n- minimal:\n'
RETURN = ''
from ansible.module_utils.basic import AnsibleModule
from ..module_utils.my_util import hello

def main():
    module = AnsibleModule(argument_spec=dict(name=dict(type='str')))
    module.exit_json(**say_hello(module.params['name']))

def say_hello(name):
    return dict(message=hello(name))
if __name__ == '__main__':
    main()