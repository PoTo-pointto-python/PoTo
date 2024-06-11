from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\nmodule: pids\nversion_added: 2.8\ndescription: "Retrieves a list of PIDs of given process name in Ansible controller/controlled machines.Returns an empty list if no process in that name exists."\nshort_description: "Retrieves process IDs list if the process is running otherwise return empty list"\nauthor:\n  - Saranya Sridharan (@saranyasridharan)\nrequirements:\n  - psutil(python module)\noptions:\n  name:\n    description: the name of the process you want to get PID for.\n    required: true\n    type: str\n'
EXAMPLES = '\n# Pass the process name\n- name: Getting process IDs of the process\n  pids:\n      name: python\n  register: pids_of_python\n\n- name: Printing the process IDs obtained\n  debug:\n    msg: "PIDS of python:{{pids_of_python.pids|join(\',\')}}"\n'
RETURN = '\npids:\n  description: Process IDs of the given process\n  returned: list of none, one, or more process IDs\n  type: list\n  sample: [100,200]\n'
from ansible.module_utils.basic import AnsibleModule
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

def compare_lower(a, b):
    if a is None or b is None:
        return a == b
    return a.lower() == b.lower()

def get_pid(name):
    pids = []
    for proc in psutil.process_iter(attrs=['name', 'cmdline']):
        if compare_lower(proc.info['name'], name) or (proc.info['cmdline'] and compare_lower(proc.info['cmdline'][0], name)):
            pids.append(proc.pid)
    return pids

def main():
    module = AnsibleModule(argument_spec=dict(name=dict(required=True, type='str')), supports_check_mode=True)
    if not HAS_PSUTIL:
        module.fail_json(msg="Missing required 'psutil' python module. Try installing it with: pip install psutil")
    name = module.params['name']
    response = dict(pids=get_pid(name))
    module.exit_json(**response)
if __name__ == '__main__':
    main()