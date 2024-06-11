from __future__ import absolute_import, division, print_function
__metaclass__ = type
import json
import os
import sys
import ansible_runner
output_dir = sys.argv[1]
r = ansible_runner.run(private_data_dir=output_dir, host_pattern='localhost', module='shell', module_args='whoami')
data = {'rc': r.rc, 'status': r.status, 'events': [x['event'] for x in r.events], 'stats': r.stats}
print('#STARTJSON')
json.dump(data, sys.stdout)