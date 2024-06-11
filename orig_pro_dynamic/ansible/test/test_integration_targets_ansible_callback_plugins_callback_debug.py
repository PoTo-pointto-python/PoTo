from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.plugins.callback import CallbackBase

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'callback_debug'

    def __init__(self, *args, **kwargs):
        super(CallbackModule, self).__init__(*args, **kwargs)
        self._display.display('__init__')
        for cb in [x for x in dir(CallbackBase) if x.startswith('v2_')]:
            delattr(CallbackBase, cb)

    def __getattr__(self, name):
        if name.startswith('v2_'):
            return lambda *args, **kwargs: self._display.display(name)

def test_CallbackModule___getattr__():
    ret = CallbackModule().__getattr__()