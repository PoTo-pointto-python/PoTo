from __future__ import absolute_import, division, print_function
__metaclass__ = type
import resource
import subprocess
from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(argument_spec=dict())
    rlimit_nofile = resource.getrlimit(resource.RLIMIT_NOFILE)
    try:
        maxfd = subprocess.MAXFD
    except AttributeError:
        maxfd = -1
    module.exit_json(rlimit_nofile=rlimit_nofile, maxfd=maxfd, infinity=resource.RLIM_INFINITY)
if __name__ == '__main__':
    main()