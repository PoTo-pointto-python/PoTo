from __future__ import absolute_import, division, print_function
__metaclass__ = type
import json
import os
import sys
import ansible_runner
PLAYBOOK = '\n- hosts: localhost\n  gather_facts: False\n  tasks:\n    - set_fact:\n        foo: bar\n'
output_dir = sys.argv[1]
invdir = os.path.join(output_dir, 'inventory')
if not os.path.isdir(invdir):
    os.makedirs(invdir)
with open(os.path.join(invdir, 'hosts'), 'w') as f:
    f.write('localhost\n')
pbfile = os.path.join(output_dir, 'test.yml')
with open(pbfile, 'w') as f:
    f.write(PLAYBOOK)
r = ansible_runner.run(private_data_dir=output_dir, playbook='test.yml')
data = {'rc': r.rc, 'status': r.status, 'events': [x['event'] for x in r.events], 'stats': r.stats}
print('#STARTJSON')
json.dump(data, sys.stdout)