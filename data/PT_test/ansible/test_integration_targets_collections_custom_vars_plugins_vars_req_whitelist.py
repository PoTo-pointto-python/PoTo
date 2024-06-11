from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\n    vars: vars_req_whitelist\n    version_added: "2.10"\n    short_description: load host and group vars\n    description: test loading host and group vars from a collection\n    options:\n      stage:\n        choices: [\'all\', \'inventory\', \'task\']\n        type: str\n        ini:\n          - key: stage\n            section: vars_req_whitelist\n        env:\n          - name: ANSIBLE_VARS_PLUGIN_STAGE\n'
from ansible.plugins.vars import BaseVarsPlugin

class VarsModule(BaseVarsPlugin):
    REQUIRES_WHITELIST = True

    def get_vars(self, loader, path, entities, cache=True):
        super(VarsModule, self).get_vars(loader, path, entities)
        return {'whitelisted': True, 'collection': False}

def test_VarsModule_get_vars():
    ret = VarsModule().get_vars()