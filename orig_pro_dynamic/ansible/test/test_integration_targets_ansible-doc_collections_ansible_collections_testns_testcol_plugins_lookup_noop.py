from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\n    lookup: noop\n    author: Ansible core team\n    short_description: returns input\n    description:\n      - this is a noop\n'
EXAMPLES = '\n- name: do nothing\n  debug: msg="{{ lookup(\'testns.testcol.noop\', [1,2,3,4] }}"\n'
RETURN = '\n  _list:\n    description: input given\n'
from ansible.module_utils.common._collections_compat import Sequence
from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError

class LookupModule(LookupBase):

    def run(self, terms, **kwargs):
        if not isinstance(terms, Sequence):
            raise AnsibleError('testns.testcol.noop expects a list')
        return terms

def test_LookupModule_run():
    ret = LookupModule().run()