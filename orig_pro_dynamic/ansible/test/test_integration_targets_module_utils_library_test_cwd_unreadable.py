from __future__ import absolute_import, division, print_function
__metaclass__ = type
import os
from ansible.module_utils.basic import AnsibleModule

def main():
    try:
        cwd = os.getcwd()
    except OSError:
        cwd = '/'
        os.chdir(cwd)
    module = AnsibleModule(argument_spec=dict())
    module.exit_json(before=cwd, after=os.getcwd())
if __name__ == '__main__':
    main()