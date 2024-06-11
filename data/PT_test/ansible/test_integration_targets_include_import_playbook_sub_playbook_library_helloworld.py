from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(argument_spec={})
    module.exit_json(msg='Hello, World!')
if __name__ == '__main__':
    main()