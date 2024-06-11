__metaclass__ = type
from ansible.plugins.lookup import LookupBase

class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):
        return [__name__]

def test_LookupModule_run():
    ret = LookupModule().run()