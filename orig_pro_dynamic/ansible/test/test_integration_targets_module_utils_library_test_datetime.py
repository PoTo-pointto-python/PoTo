from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.module_utils.basic import AnsibleModule
import datetime
module = AnsibleModule(argument_spec=dict(datetime=dict(type=str, required=True), date=dict(type=str, required=True)))
result = {'datetime': datetime.datetime.strptime(module.params.get('datetime'), '%Y-%m-%dT%H:%M:%S'), 'date': datetime.datetime.strptime(module.params.get('date'), '%Y-%m-%d').date()}
module.exit_json(**result)