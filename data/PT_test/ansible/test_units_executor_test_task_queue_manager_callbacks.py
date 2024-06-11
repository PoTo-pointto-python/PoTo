from __future__ import absolute_import, division, print_function
from units.compat import unittest
from units.compat.mock import MagicMock
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.playbook import Playbook
from ansible.plugins.callback import CallbackBase
from ansible.utils import context_objects as co
__metaclass__ = type

class TestTaskQueueManagerCallbacks(unittest.TestCase):

    def setUp(self):
        inventory = MagicMock()
        variable_manager = MagicMock()
        loader = MagicMock()
        passwords = []
        co.GlobalCLIArgs._Singleton__instance = None
        self._tqm = TaskQueueManager(inventory, variable_manager, loader, passwords)
        self._playbook = Playbook(loader)
        self._register = MagicMock()

    def tearDown(self):
        co.GlobalCLIArgs._Singleton__instance = None

    def test_task_queue_manager_callbacks_v2_playbook_on_start(self):
        """
        Assert that no exceptions are raised when sending a Playbook
        start callback to a current callback module plugin.
        """
        register = self._register

        class CallbackModule(CallbackBase):
            """
            This is a callback module with the current
            method signature for `v2_playbook_on_start`.
            """
            CALLBACK_VERSION = 2.0
            CALLBACK_TYPE = 'notification'
            CALLBACK_NAME = 'current_module'

            def v2_playbook_on_start(self, playbook):
                register(self, playbook)
        callback_module = CallbackModule()
        self._tqm._callback_plugins.append(callback_module)
        self._tqm.send_callback('v2_playbook_on_start', self._playbook)
        register.assert_called_once_with(callback_module, self._playbook)

    def test_task_queue_manager_callbacks_v2_playbook_on_start_wrapped(self):
        """
        Assert that no exceptions are raised when sending a Playbook
        start callback to a wrapped current callback module plugin.
        """
        register = self._register

        def wrap_callback(func):
            """
            This wrapper changes the exposed argument
            names for a method from the original names
            to (*args, **kwargs). This is used in order
            to validate that wrappers which change par-
            ameter names do not break the TQM callback
            system.

            :param func: function to decorate
            :return: decorated function
            """

            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper

        class WrappedCallbackModule(CallbackBase):
            """
            This is a callback module with the current
            method signature for `v2_playbook_on_start`
            wrapped in order to change the signature.
            """
            CALLBACK_VERSION = 2.0
            CALLBACK_TYPE = 'notification'
            CALLBACK_NAME = 'current_module'

            @wrap_callback
            def v2_playbook_on_start(self, playbook):
                register(self, playbook)
        callback_module = WrappedCallbackModule()
        self._tqm._callback_plugins.append(callback_module)
        self._tqm.send_callback('v2_playbook_on_start', self._playbook)
        register.assert_called_once_with(callback_module, self._playbook)

def test_TestTaskQueueManagerCallbacks_setUp():
    ret = TestTaskQueueManagerCallbacks().setUp()

def test_TestTaskQueueManagerCallbacks_tearDown():
    ret = TestTaskQueueManagerCallbacks().tearDown()

def test_TestTaskQueueManagerCallbacks_test_task_queue_manager_callbacks_v2_playbook_on_start():
    ret = TestTaskQueueManagerCallbacks().test_task_queue_manager_callbacks_v2_playbook_on_start()

def test_TestTaskQueueManagerCallbacks_wrapper():
    ret = TestTaskQueueManagerCallbacks().wrapper()

def test_TestTaskQueueManagerCallbacks_wrap_callback():
    ret = TestTaskQueueManagerCallbacks().wrap_callback()

def test_TestTaskQueueManagerCallbacks_test_task_queue_manager_callbacks_v2_playbook_on_start_wrapped():
    ret = TestTaskQueueManagerCallbacks().test_task_queue_manager_callbacks_v2_playbook_on_start_wrapped()

def test_CallbackModule_v2_playbook_on_start():
    ret = CallbackModule().v2_playbook_on_start()

def test_WrappedCallbackModule_v2_playbook_on_start():
    ret = WrappedCallbackModule().v2_playbook_on_start()