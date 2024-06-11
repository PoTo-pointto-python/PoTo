"""Say hello."""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(argument_spec={'name': {'default': 'world'}})
    name = module.params['name']
    module.exit_json(msg='Greeting {name} completed.'.format(name=name.title()), greeting='Hello, {name}!'.format(name=name))
if __name__ == '__main__':
    main()