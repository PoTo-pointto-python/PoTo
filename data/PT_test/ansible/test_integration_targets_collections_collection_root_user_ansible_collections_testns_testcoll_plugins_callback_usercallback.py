from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.plugins.callback import CallbackBase
DOCUMENTATION = '\n    callback: usercallback\n    callback_type: notification\n    short_description: does stuff\n    description:\n      - does some stuff\n'

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'usercallback'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()
        self._display.display('loaded usercallback from collection, yay')

    def v2_runner_on_ok(self, result):
        self._display.display('usercallback says ok')

def test_CallbackModule_v2_runner_on_ok():
    ret = CallbackModule().v2_runner_on_ok()