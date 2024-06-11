from __future__ import absolute_import, division, print_function
__metaclass__ = type
import os
from ansible.module_utils.basic import AnsibleModule

def main():
    temp = os.path.abspath('temp')
    os.mkdir(temp)
    os.chdir(temp)
    os.rmdir(temp)
    module = AnsibleModule(argument_spec=dict())
    module.exit_json(before=temp, after=os.getcwd())
if __name__ == '__main__':
    main()