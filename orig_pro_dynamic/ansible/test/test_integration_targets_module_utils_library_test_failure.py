from __future__ import absolute_import, division, print_function
__metaclass__ = type
results = {}
try:
    from ansible.module_utils.zebra import foo
    results['zebra'] = foo.data
except ImportError:
    results['zebra'] = 'Failed in module as expected but incorrectly did not fail in AnsiballZ construction'
from ansible.module_utils.basic import AnsibleModule
AnsibleModule(argument_spec=dict()).exit_json(**results)